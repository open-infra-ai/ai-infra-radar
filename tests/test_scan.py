from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scan


NOW = datetime(2026, 10, 4, tzinfo=timezone.utc)
PROJECT = {"repo": "example/infra", "priority": 3}
PROFILE = {"username": "holtwood", "topics": {"KV": ["kv cache"]}}


def issue(number=1, body="CPU-only repro", author="reporter"):
    return scan.normalize({
        "id": f"I_{number}", "number": number, "title": "KV cache lifetime",
        "url": f"https://github.com/example/infra/issues/{number}", "body": body,
        "createdAt": "2026-10-01T00:00:00Z", "updatedAt": "2026-10-03T00:00:00Z",
        "author": {"login": author}, "state": "OPEN", "labels": {"nodes": []},
        "assignees": {"nodes": []}, "comments": {"totalCount": 0},
    }, PROJECT["repo"], "issue", "recent")


def comment(author, body):
    return {"author": {"login": author}, "body": body, "url": "https://github.com/comment"}


def connection(nodes, more=False, cursor=None):
    return {"nodes": nodes, "totalCount": len(nodes),
            "pageInfo": {"hasNextPage": more, "endCursor": cursor}}


class FakeAPI:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.calls = []

    def graphql(self, query, **variables):
        self.calls.append((query, variables))
        return {"node": next(self.pages)}


class ScanTests(unittest.TestCase):
    def test_author_intent_beyond_excerpt_routes_to_collaboration(self):
        intent = "If maintainers agree, I'm happy to work on the fix."
        row = issue(body="x" * 6100 + "\n" + intent)
        row.update(detail_checked=True, detail_complete=True)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertTrue(row["body_truncated"])
        self.assertNotIn(intent, row["body_excerpt"])
        self.assertEqual(row["author_work_intent"], intent)
        self.assertEqual(row["claimants"], [])
        self.assertEqual(row["mode"], "collaborate")
        self.assertIn("需确认是否已开工", scan.signals(row))

    def test_author_intent_ignores_code_quotes_and_negation(self):
        for body in (
            "```python\nprint(\"I'm happy to work on the fix.\")\n```",
            "~~~text\nI will fix this.\n~~~",
            "```text\nI will fix this.\n````",
            "```text\nI will fix this.",
            "> I'm happy to work on the fix.",
            "Example: `I will fix this.`",
            "    I will fix this.",
            "I will not work on this; I'm not willing to fix it.",
            "The author is happy to work on the fix.",
        ):
            with self.subTest(body=body):
                row = issue(body=body)
                row.update(detail_checked=True, detail_complete=True)
                scan.score_item(row, PROJECT, PROFILE, NOW)
                self.assertEqual(row["author_work_intent"], "")
                self.assertEqual(row["mode"], "investigate")

    def test_prose_intent_after_fenced_example_is_detected(self):
        body = "```text\nI will fix the example.\n````\nI can work on the actual issue."
        self.assertEqual(scan.author_work_intent(body), "I can work on the actual issue.")

    def test_own_author_intent_does_not_imply_competing_work(self):
        row = issue(body="我愿意修复这个问题。", author="holtwood")
        row.update(detail_checked=True, detail_complete=True)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "investigate")
        self.assertEqual(row["score"], 50)

    def test_author_intent_cannot_hide_incomplete_thread_or_closed_state(self):
        row = issue(body="I can fix this.")
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "verify")
        row.update(state="CLOSED", detail_complete=True)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "closed")

    def test_topic_search_is_merged_with_recent_window(self):
        original = issue()
        raw = {"id": original["node_id"], "number": 1, "title": original["title"], "url": original["url"],
               "body": "CPU-only repro", "createdAt": original["created_at"], "updatedAt": original["updated_at"],
               "author": {"login": "reporter"}, "state": "OPEN", "labels": {"nodes": []},
               "assignees": {"nodes": []}, "comments": {"totalCount": 0}}
        repo = {"nameWithOwner": PROJECT["repo"], "isArchived": False, "hasDiscussionsEnabled": False,
                "recent": connection([raw]), "first": connection([]), "help": connection([]), "discussions": connection([])}
        pages = iter([{"repository": repo}, {"search": {"issueCount": 1, **connection([raw])}}])
        class TopicAPI:
            def graphql(self, document, **variables):
                return next(pages)
        rows, coverage = scan.collect_project(TopicAPI(), {**PROJECT, "search_terms": ["cache"]},
                                              {"recent_issues": 25, "labelled_issues": 10, "discussions": 6, "topic_issues": 15})
        self.assertEqual(len(rows), 1)
        self.assertEqual(next(iter(rows.values()))["origins"], ["recent", "topic:cache"])
        self.assertEqual(coverage["topic_searches"][0]["available"], 1)

    def test_rfc_without_existing_work_is_a_discussion_opportunity(self):
        row = issue()
        row.update(title="[RFC]: KV cache contract", detail_checked=True, detail_complete=True)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "discuss")

    def test_zero_comments_still_requires_reference_check(self):
        row = scan.score_item(issue(), PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "verify")
        self.assertIn("线程尚未核查", scan.signals(row))

    def test_open_closing_pr_routes_to_collaboration(self):
        row = issue()
        row.update(detail_checked=True, detail_complete=True,
                   linked_prs=[{"state": "OPEN", "will_close_target": True,
                                "repo": "example/infra", "number": 8, "url": "https://github.com/pr"}])
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "collaborate")
        self.assertIn("关闭关联 PR", scan.signals(row))

    def test_related_pr_is_not_asserted_to_fix_issue(self):
        row = issue()
        row.update(detail_checked=True, detail_complete=True,
                   linked_prs=[{"state": "OPEN", "will_close_target": False,
                                "repo": "example/other", "number": 9, "url": "https://github.com/pr"}])
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertEqual(row["mode"], "verify")
        self.assertEqual(row["open_closing_prs"], [])

    def test_claim_release_does_not_release_other_contributor(self):
        records = [scan.comment_record(comment("one", "/claim")),
                   scan.comment_record(comment("two", "I would like work on this.")),
                   scan.comment_record(comment("one", "Releasing this claim."))]
        self.assertEqual(scan.detect_claims(records), ["two"])

    def test_claim_in_later_comment_page_is_detected(self):
        row = issue()
        api = FakeAPI([
            {"comments": connection([comment("one", "Some context")], True, "next"),
             "references": connection([])},
            {"comments": connection([comment("two", "I'll take the fix.")])},
        ])
        scan.check_details(api, row, 10)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertTrue(row["detail_complete"])
        self.assertEqual(row["mode"], "collaborate")
        self.assertEqual(api.calls[1][1]["comments"], "next")
        self.assertNotIn("references", api.calls[1][1])

    def test_page_budget_exhaustion_is_not_marked_complete(self):
        row = issue()
        api = FakeAPI([{"comments": connection([], True, "next"), "references": connection([])}])
        scan.check_details(api, row, 1)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        self.assertFalse(row["detail_complete"])
        self.assertEqual(row["mode"], "verify")

    def test_truncated_comment_is_not_marked_complete(self):
        row = issue()
        api = FakeAPI([{"comments": connection([comment("one", "x" * 4001)]), "references": connection([])}])
        scan.check_details(api, row, 10)
        self.assertFalse(row["detail_complete"])
        self.assertTrue(row["comments"][0]["body_truncated"])

    def test_missing_discussion_replies_are_visible(self):
        row = issue()
        row.update(kind="discussion", answered=False)
        node = comment("one", "Question")
        node["replies"] = connection([], True, "reply-next")
        scan.check_details(FakeAPI([{"comments": connection([node])}]), row, 10)
        self.assertFalse(row["detail_complete"])

    def test_manual_review_cannot_reopen_closed_issue_or_hide_claim(self):
        review = {"mode": "investigate", "reviewed_at": "2026-10-04", "next_step": "Reproduce", "reason": "Fit"}
        row = issue()
        row.update(detail_checked=True, detail_complete=True, assignees=["another"])
        scan.score_item(row, PROJECT, PROFILE, NOW)
        scan.apply_review(row, review, NOW.date())
        self.assertEqual(row["mode"], "collaborate")
        row["state"] = "CLOSED"
        scan.score_item(row, PROJECT, PROFILE, NOW)
        scan.apply_review(row, review, NOW.date())
        self.assertEqual(row["mode"], "closed")

    def test_window_absence_does_not_mean_closed(self):
        old = {"items": [issue(1), issue(2)]}
        current = issue(1)
        current["state"] = "CLOSED"
        changes = scan.changes_since(old, [current])
        self.assertEqual(changes, [{"url": current["url"], "change": "OPEN → CLOSED"}])

    def test_generated_reports_preserve_manual_files(self):
        row = issue()
        row.update(detail_checked=True, detail_complete=True)
        scan.score_item(row, PROJECT, PROFILE, NOW)
        snapshot = {"scanned_at": NOW.isoformat(), "items": [row], "shortlist": [row],
                    "coverage": [], "changes": []}
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "tracking").mkdir()
            manual = root / "tracking" / "contributions.json"
            manual.write_text('{"manual": "retain exactly"}\n')
            before = manual.read_bytes()
            scan.generate(root, snapshot, {"entries": []})
            self.assertEqual(manual.read_bytes(), before)
            self.assertTrue((root / "reports" / "latest.md").exists())
            history = scan.read_json(root / "data" / "history" / "2026-10-04.json")
            self.assertNotIn("body_excerpt", history["shortlist"][0])

    def test_network_failure_preserves_successful_snapshot(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for folder in ("config", "tracking", "data", "reports"):
                (root / folder).mkdir()
            config = {"projects": [PROJECT], "scan": {"recent_issues": 25, "labelled_issues": 10, "discussions": 6}, "profile": PROFILE}
            scan.write_json(root / "config" / "projects.json", config)
            for filename in ("triage.json", "contributions.json"):
                scan.write_json(root / "tracking" / filename, {"entries": []})
            scan.write_json(root / "data" / "latest.json", {"items": []})
            report = root / "reports" / "latest.md"
            report.write_text("last successful report")
            before = (root / "data" / "latest.json").read_bytes()
            with patch.object(scan.GitHub, "graphql", side_effect=RuntimeError("rate limited")):
                with self.assertRaisesRegex(RuntimeError, "rate limited"):
                    scan.run_scan(root, scan.GitHub(), NOW)
            self.assertEqual(report.read_text(), "last successful report")
            self.assertEqual((root / "data" / "latest.json").read_bytes(), before)

    def test_graphql_partial_error_is_not_success(self):
        response = type("Response", (), {"returncode": 0, "stdout": json.dumps({"data": {"partial": True}, "errors": [{"message": "denied"}]}), "stderr": ""})()
        with patch.object(scan.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "denied"):
                scan.GitHub().graphql("query { viewer { login } }")

    def test_upstream_title_cannot_break_markdown_table(self):
        self.assertEqual(scan.cell("a|b\n[link]<script>"), "a\\|b \\[link\\]&lt;script&gt;")


if __name__ == "__main__":
    unittest.main()
