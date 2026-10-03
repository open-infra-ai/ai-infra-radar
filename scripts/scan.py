#!/usr/bin/env python3
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
COMMON = """
id number title url body createdAt updatedAt author { login }
"""
ISSUE_FIELDS = COMMON + """
state labels(first: 30) { nodes { name } }
assignees(first: 20) { nodes { login } } comments { totalCount }
"""
DISCUSSION_FIELDS = COMMON + """
closed isAnswered category { name } comments { totalCount }
"""
PR_FIELDS = COMMON + """
state isDraft mergedAt reviewDecision comments { totalCount }
"""
CLAIM = re.compile(
    r"/claim\b|(?:i(?:'d| would| am| will|'ll|’d|’ll)?|i'm)\s+"
    r"(?:like(?: to)? work|take\b|working on|work on|happy to work)|"
    r"can i work on|i.{0,25}opened.{0,30}(?:pull request|\bpr\b)|认领|我来处理",
    re.I,
)
RELEASE = re.compile(
    r"/unclaim\b|releas\w*.{0,30}claim|not working on|"
    r"(?:don't|do not) have a pr|撤销认领|放弃认领", re.I
)
HARDWARE = re.compile(
    r"\b(?:H100|H200|B200|B300|GH200|GB200|DGX Spark|"
    r"SM[_ ]?(?:90|100|103|120|121)|TP\s*[=:]\s*[2-9])\b|"
    r"[2-9]\s*[x×]\s*(?:GPU|V100|A100|H100|H200|B200)", re.I
)
MODE_NAMES = {
    "investigate": "可尝试调查 / 复现",
    "discuss": "可参与讨论 / 分析",
    "collaborate": "已有工作：协作验证 / 补测试",
    "verify": "需进一步核查",
    "closed": "已关闭 / 已回答",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def key(item):
    return (item["repo"], item["kind"], item["number"])


class GitHub:
    def graphql(self, document, **variables):
        result = subprocess.run(
            ["gh", "api", "graphql", "--input", "-"],
            input=json.dumps({"query": document, "variables": variables}),
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "GitHub API 请求失败")
        payload = json.loads(result.stdout)
        if payload.get("errors"):
            raise RuntimeError("; ".join(error["message"] for error in payload["errors"]))
        return payload["data"]


def normalize(node, repo, kind, origin):
    body = node["body"]
    item = {
        "node_id": node["id"], "repo": repo, "kind": kind,
        "number": node["number"], "title": node["title"], "url": node["url"],
        "state": node.get("state", "CLOSED" if node.get("closed") else "OPEN"),
        "created_at": node["createdAt"], "updated_at": node["updatedAt"],
        "author": node["author"]["login"] if node["author"] else "deleted-user",
        "body_excerpt": body[:6000], "body_truncated": len(body) > 6000,
        "labels": [label["name"] for label in node.get("labels", {"nodes": []})["nodes"]],
        "assignees": [user["login"] for user in node.get("assignees", {"nodes": []})["nodes"]],
        "comment_count": node["comments"]["totalCount"],
        "origins": [origin], "detail_checked": False, "detail_complete": False,
        "comments": [], "linked_prs": [],
    }
    if kind == "discussion":
        item.update(category=node["category"]["name"], answered=node["isAnswered"])
    if kind == "pull_request":
        item.update(is_draft=node["isDraft"], merged_at=node["mergedAt"], review_decision=node["reviewDecision"])
    return item


def merge_item(items, item):
    item_key = key(item)
    if item_key in items:
        for origin in item["origins"]:
            if origin not in items[item_key]["origins"]:
                items[item_key]["origins"].append(origin)
    else:
        items[item_key] = item


def collect_project(api, project, settings):
    query = """
    query($owner: String!, $name: String!, $recent: Int!, $labelled: Int!, $threads: Int!) {
      repository(owner: $owner, name: $name) {
        nameWithOwner url isArchived hasDiscussionsEnabled
        recent: issues(first: $recent, states: OPEN, orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount pageInfo { hasNextPage } nodes { ISSUE_FIELDS }
        }
        first: issues(first: $labelled, states: OPEN, labels: ["good first issue"], orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount pageInfo { hasNextPage } nodes { ISSUE_FIELDS }
        }
        help: issues(first: $labelled, states: OPEN, labels: ["help wanted"], orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount pageInfo { hasNextPage } nodes { ISSUE_FIELDS }
        }
        discussions(first: $threads, orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount pageInfo { hasNextPage } nodes { DISCUSSION_FIELDS }
        }
      }
    }
    """.replace("ISSUE_FIELDS", ISSUE_FIELDS).replace("DISCUSSION_FIELDS", DISCUSSION_FIELDS)
    owner, name = project["repo"].split("/")
    data = api.graphql(query, owner=owner, name=name, recent=settings["recent_issues"],
                       labelled=settings["labelled_issues"], threads=settings["discussions"])
    repo = data["repository"]
    if repo is None:
        raise RuntimeError(f"无法读取配置仓库 {project['repo']}")
    items = {}
    coverage = {"repo": repo["nameWithOwner"], "archived": repo["isArchived"],
                "discussions_enabled": repo["hasDiscussionsEnabled"], "windows": {}}
    for origin in ("recent", "first", "help", "discussions"):
        connection = repo[origin]
        coverage["windows"][origin] = {
            "returned": len(connection["nodes"]), "available": connection["totalCount"],
            "has_more": connection["pageInfo"]["hasNextPage"],
        }
        kind = "discussion" if origin == "discussions" else "issue"
        for node in connection["nodes"]:
            merge_item(items, normalize(node, project["repo"], kind, origin))
    coverage["topic_searches"] = []
    for term in project.get("search_terms", []):
        query = """
        query($query: String!, $limit: Int!) {
          search(query: $query, type: ISSUE, first: $limit) {
            issueCount pageInfo { hasNextPage } nodes { ... on Issue { ISSUE_FIELDS } }
          }
        }
        """.replace("ISSUE_FIELDS", ISSUE_FIELDS)
        search = api.graphql(query, query=f"repo:{project['repo']} is:issue is:open in:title {term} sort:updated-desc",
                             limit=settings["topic_issues"])["search"]
        coverage["topic_searches"].append({"term": term, "returned": len(search["nodes"]),
                                          "available": search["issueCount"], "has_more": search["pageInfo"]["hasNextPage"]})
        for node in search["nodes"]:
            merge_item(items, normalize(node, project["repo"], "issue", "topic:" + term))
    return items, coverage


def collect_target(api, target):
    kind = target["kind"]
    field, fields = {
        "issue": ("issue", ISSUE_FIELDS), "discussion": ("discussion", DISCUSSION_FIELDS),
        "pull_request": ("pullRequest", PR_FIELDS),
    }[kind]
    owner, name = target["repo"].split("/")
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) { TARGET(number: $number) { FIELDS } }
    }
    """.replace("TARGET", field).replace("FIELDS", fields)
    node = api.graphql(query, owner=owner, name=name, number=target["number"])["repository"][field]
    if node is None:
        raise RuntimeError(f"固定条目不存在：{target['repo']} {kind} #{target['number']}")
    return normalize(node, target["repo"], kind, "tracked")


def comment_record(node):
    body = node["body"]
    return {"author": node["author"]["login"] if node["author"] else "deleted-user",
            "url": node["url"], "body": body[:4000], "body_truncated": len(body) > 4000}


def check_details(api, item, max_pages):
    cursors = {"comments": None}
    if item["kind"] == "issue":
        cursors["references"] = None
    done = set()
    content_complete = True
    for _ in range(max_pages):
        selections = []
        if "comments" not in done:
            replies = """
            replies(first: 100) { totalCount pageInfo { hasNextPage }
              nodes { body author { login } url }
            }
            """ if item["kind"] == "discussion" else ""
            selections.append("""
            comments(first: 100, after: $comments) {
              totalCount pageInfo { hasNextPage endCursor }
              nodes { body author { login } url REPLIES }
            }
            """.replace("REPLIES", replies))
        if "references" in cursors and "references" not in done:
            selections.append("""
            references: timelineItems(first: 100, after: $references, itemTypes: [CROSS_REFERENCED_EVENT]) {
              pageInfo { hasNextPage endCursor }
              nodes { ... on CrossReferencedEvent {
                willCloseTarget source { ... on PullRequest {
                  title number url state mergedAt repository { nameWithOwner }
                } }
              } }
            }
            """)
        active = [name for name in cursors if name not in done]
        declarations = ", ".join(f"${name}: String" for name in active)
        typename = {"issue": "Issue", "discussion": "Discussion", "pull_request": "PullRequest"}[item["kind"]]
        query = f"query($id: ID!, {declarations}) {{ node(id: $id) {{ ... on {typename} {{ {' '.join(selections)} }} }} }}"
        node = api.graphql(query, id=item["node_id"], **{name: cursors[name] for name in active})["node"]
        for name in active:
            connection = node[name]
            if name == "comments":
                item["comment_count"] = connection["totalCount"]
                for comment in connection["nodes"]:
                    record = comment_record(comment)
                    item["comments"].append(record)
                    content_complete &= not record["body_truncated"]
                    if item["kind"] == "discussion":
                        replies = comment["replies"]
                        content_complete &= not replies["pageInfo"]["hasNextPage"]
                        for reply in replies["nodes"]:
                            record = comment_record(reply)
                            item["comments"].append(record)
                            content_complete &= not record["body_truncated"]
            else:
                for event in connection["nodes"]:
                    source = event["source"]
                    if source:
                        item["linked_prs"].append({
                            "url": source["url"], "title": source["title"], "number": source["number"],
                            "repo": source["repository"]["nameWithOwner"], "state": source["state"],
                            "merged_at": source["mergedAt"], "will_close_target": event["willCloseTarget"],
                        })
            if connection["pageInfo"]["hasNextPage"]:
                cursors[name] = connection["pageInfo"]["endCursor"]
            else:
                done.add(name)
        if len(done) == len(cursors):
            break
    item["detail_checked"] = True
    item["detail_complete"] = len(done) == len(cursors) and content_complete
    item["detail_scope"] = "全部评论与 issue 跨引用；Discussion 回复每评论最多 100 条；PR 不含逐行 review threads"


def detect_claims(comments):
    claimants = set()
    for comment in comments:
        if RELEASE.search(comment["body"]):
            claimants.discard(comment["author"])
        elif CLAIM.search(comment["body"]):
            claimants.add(comment["author"])
    return sorted(claimants)


def score_item(item, project, profile, now):
    title = item["title"].lower()
    text = title + "\n" + item["body_excerpt"].lower()
    score = project["priority"] * 10
    topics = []
    reasons = [f"项目关注权重 {project['priority']}"]
    for topic, keywords in profile["topics"].items():
        if any(word in text for word in keywords):
            topics.append(topic)
            score += 10 if any(word in title for word in keywords) else 3
    if topics:
        reasons.append("匹配 " + "、".join(topics))
    labels = [label.lower() for label in item["labels"]]
    for label, bonus in (("good first issue", 15), ("help wanted", 8)):
        if label in labels:
            score += bonus
            reasons.append(label)
    age = (now - datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))).days
    score += 10 if age <= 14 else 5 if age <= 45 else -15 if age > 120 else 0
    hardware = sorted(set(match.group(0) for match in HARDWARE.finditer(item["title"] + "\n" + item["body_excerpt"])))
    if hardware:
        score -= 12
    if re.search(r"tracking|nightly.*failure|failure tracker|security", title):
        score -= 25
    if item["assignees"]:
        score -= 12
    claimants = [author for author in detect_claims(item["comments"]) if author != profile["username"]]
    open_prs = [pr for pr in item["linked_prs"] if pr["state"] == "OPEN"]
    closing_prs = [pr for pr in open_prs if pr["will_close_target"]]
    if claimants or closing_prs:
        score -= 18
    elif open_prs:
        score -= 8
    item.update(score=score, score_reasons=reasons, topics=topics, age_days=age,
                hardware_mentions=hardware, claimants=claimants, open_related_prs=open_prs,
                open_closing_prs=closing_prs)
    if item["state"] != "OPEN" or item.get("answered") is True:
        mode = "closed"
    elif not item["detail_complete"]:
        mode = "verify"
    elif item["kind"] == "discussion":
        mode = "discuss"
    elif item["assignees"] or claimants or closing_prs:
        mode = "collaborate"
    elif open_prs:
        mode = "verify"
    elif "rfc" in labels or re.search(r"\[rfc\]|\[discussion\]", title):
        mode = "discuss"
    else:
        mode = "investigate"
    item["mode"] = mode
    item["next_step"] = {
        "investigate": "读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。",
        "discuss": "读完整线程，提出一个有源码依据的解释、反例或最小实验。",
        "collaborate": "先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。",
        "verify": "补齐线程、关联 PR 与当前源码核查，再判断参与方式。",
        "closed": "复盘上游结论，核对是否仍有可补充的证据。",
    }[mode]
    return item


def apply_review(item, review, today):
    item["manual_review"] = review
    item["review_needs_refresh"] = (today - datetime.fromisoformat(review["reviewed_at"]).date()).days > 14
    if item["mode"] != "closed":
        if review["mode"] == "investigate" and item["mode"] in ("collaborate", "verify"):
            pass
        else:
            item["mode"] = review["mode"]
        item["next_step"] = review["next_step"]


def choose_shortlist(items, limit):
    groups = defaultdict(list)
    for item in sorted(items, key=lambda row: (-row["score"], row["repo"], row["number"])):
        if item["mode"] != "closed" and item["kind"] != "pull_request":
            groups[item["mode"]].append(item)
    selected = []
    per_repo = Counter()
    modes = ("investigate", "discuss", "collaborate", "verify")
    while len(selected) < limit:
        changed = False
        for mode in modes:
            while groups[mode] and per_repo[groups[mode][0]["repo"]] >= 5:
                groups[mode].pop(0)
            if groups[mode] and len(selected) < limit:
                item = groups[mode].pop(0)
                selected.append(item)
                per_repo[item["repo"]] += 1
                changed = True
        if not changed:
            break
    return selected


def cell(value):
    return html.escape(str(value)).replace("\n", " ").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def item_link(item):
    return f"[{cell(item['repo'])} #{item['number']}]({item['url']})"


def signals(item):
    parts = []
    if not item["detail_checked"]:
        parts.append("线程尚未核查")
    elif not item["detail_complete"]:
        parts.append("核查有分页 / 文本截断")
    else:
        parts.append("已完成配置范围内线程核查；认领仍需人工确认")
    if item["assignees"]:
        parts.append("assignee: " + ", ".join(item["assignees"]))
    if item["claimants"]:
        parts.append("评论认领信号: " + ", ".join(item["claimants"]))
    for pr in item["open_related_prs"][:3]:
        meaning = "关闭关联 PR" if pr["will_close_target"] else "相关 PR，需判断是否修复"
        parts.append(f"{meaning} [{pr['repo']} #{pr['number']}]({pr['url']})")
    if item["hardware_mentions"]:
        parts.append("原帖涉及 " + ", ".join(item["hardware_mentions"][:4]) + "；确认本机路径")
    if item["age_days"] > 120:
        parts.append("话题较旧，先确认现状")
    if item.get("review_needs_refresh"):
        parts.append("人工评估超过 14 天，需更新")
    if item["body_truncated"]:
        parts.append("正文仅保留前 6000 字符，结论需读原帖")
    return "；".join(parts)


def changes_since(previous, items):
    old = {row["url"]: row for row in previous.get("items", [])}
    changes = []
    for row in items:
        before = old.get(row["url"])
        if before is None:
            changes.append({"url": row["url"], "change": "首次采集"})
        elif before["state"] != row["state"]:
            changes.append({"url": row["url"], "change": f"{before['state']} → {row['state']}"})
        elif before["updated_at"] != row["updated_at"]:
            changes.append({"url": row["url"], "change": "上游更新"})
    return changes


def contribution_table(contributions, items, today):
    live = {key(item): item for item in items}
    lines = ["| 条目 | 本地进度 | 上游状态 | 跟进日期 | 下一步 |", "|---|---|---|---|---|"]
    for record in contributions["entries"]:
        item = live[key(record)]
        upstream = "MERGED" if item.get("merged_at") else item["state"]
        due = record["follow_up_on"] or "—"
        if record["follow_up_on"] and record["follow_up_on"] <= today.isoformat():
            due += "（到期）"
        lines.append(f"| {item_link(item)} | {cell(record['status'])} | {upstream} | {cell(due)} | {cell(record['next_step'])} |")
    return lines


def render_report(snapshot, contributions):
    items = snapshot["items"]
    shortlist = snapshot["shortlist"]
    today = datetime.fromisoformat(snapshot["scanned_at"]).date()
    lines = ["# AI Infra 贡献机会", "", f"扫描时间（UTC）：`{snapshot['scanned_at']}`。", "",
             f"覆盖 {len(snapshot['coverage'])} 个项目；去重采集 {len(items)} 个条目，深读 {sum(row['detail_checked'] for row in items)} 个线程。",
             "近期、入门标签、主线主题和固定条目构成抽样窗口，**不是全量扫描**。分数表示阅读优先级，不表示能解决的概率。",
             "认领是规则识别信号；未检出认领不代表无人工作。API 跨引用只有 `willCloseTarget` 才是关闭关联。", "",
             "## 人工评估入口", ""]
    for item in items:
        review = item.get("manual_review")
        if not review:
            continue
        lines.extend([f"### {item_link(item)}：{cell(item['title'])}", "",
                      f"参与方式：**{MODE_NAMES[item['mode']]}**；人工评估日期：`{review['reviewed_at']}`。", "",
                      review["reason"], "", "当前核查：" + signals(item), "",
                      "下一步：" + item["next_step"], ""])
    for mode in ("investigate", "discuss", "collaborate", "verify"):
        lines.extend(["## " + MODE_NAMES[mode], "",
                      "| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |", "|---|---|---|---|---|"])
        for item in shortlist:
            if item["mode"] == mode:
                lines.append(f"| {item_link(item)} | {cell(item['title'])} | {item['score']} / {cell('、'.join(item['topics']) or '待判断')} | {signals(item)} | {cell(item['next_step'])} |")
        lines.append("")
    lines.extend(["## 已有参与与跟进", ""])
    lines.extend(contribution_table(contributions, items, today))
    lines.extend(["", "本地进度由人工维护，上游状态每轮读取；已关闭且无 merged 时间的 PR 不计为合入。", "",
                  "## 采集覆盖", "", "| 项目 | 近期 issue | 入门标签 | help wanted | Discussion | 标题主题检索 |", "|---|---|---|---|---|---|"])
    for coverage in snapshot["coverage"]:
        counts = []
        for origin in ("recent", "first", "help", "discussions"):
            window = coverage["windows"][origin]
            counts.append(f"{window['returned']} / {window['available']}" + ("（还有更多）" if window["has_more"] else ""))
        topics = "；".join(f"{cell(row['term'])}: {row['returned']} / {row['available']}" + ("（还有更多）" if row['has_more'] else "")
                            for row in coverage.get("topic_searches", [])) or "—"
        lines.append(f"| {coverage['repo']} | {' | '.join(counts)} | {topics} |")
    counts = Counter(change["change"] for change in snapshot["changes"])
    lines.extend(["", "分母是 API 该窗口的可用条目数；不同窗口可能重叠。固定条目另行刷新，Discussion 关闭或已回答的条目保留数据但不列为新机会。", "",
                  "## 本轮变化", "", "、".join(f"{name} {count}" for name, count in sorted(counts.items())) or "无状态变化。", "",
                  "条目离开抽样窗口不能推导已关闭；固定条目与上一轮机会清单会继续核对状态。", ""])
    return "\n".join(lines)


def generate(root, snapshot, contributions):
    date = datetime.fromisoformat(snapshot["scanned_at"]).date().isoformat()
    report = render_report(snapshot, contributions)
    reports = root / "reports"
    (reports / "daily").mkdir(parents=True, exist_ok=True)
    (reports / "latest.md").write_text(report, encoding="utf-8")
    (reports / "daily" / f"{date}.md").write_text(report, encoding="utf-8")
    write_json(root / "data" / "latest.json", snapshot)
    compact_fields = ("repo", "kind", "number", "title", "url", "state", "updated_at", "score", "mode", "topics")
    compact = {"schema_version": 1, "scanned_at": snapshot["scanned_at"],
               "sample_count": len(snapshot["items"]), "coverage": snapshot["coverage"],
               "changes": snapshot["changes"],
               "shortlist": [{field: item[field] for field in compact_fields} for item in snapshot["shortlist"]]}
    write_json(root / "data" / "history" / f"{date}.json", compact)
    history = sorted((root / "data" / "history").glob("*.json"))[-7:]
    week = [read_json(path) for path in history]
    lines = ["# 每周参与复盘入口", "", f"当前保留最近 {len(week)} 个扫描日的概览；不等于已完成参与。", "",
             "| 扫描日期 | 抽样条目 | 机会清单 |", "|---|---|---|"]
    for row in week:
        day = datetime.fromisoformat(row["scanned_at"]).date().isoformat()
        lines.append(f"| {day} | {row['sample_count']} | [当日报告](daily/{day}.md) |")
    lines.extend(["", "## 当前跟进", ""])
    lines.extend(contribution_table(contributions, snapshot["items"], datetime.fromisoformat(snapshot["scanned_at"]).date()))
    lines.extend(["", "## 本周行动", "", "1. 从人工评估与机会清单挑 2–3 项，确认当前线程与贡献指南。",
                  "2. 先完成一个 CPU / 单卡最小复现或源码分析，记录版本、命令和原始输出。",
                  "3. 由本人审阅后给出有新证据的反馈；更新台账中的链接、反馈和跟进日期。",
                  "4. 优先回应已有 PR 的具体评审，复盘关闭原因；避免没有新增信息的催促。", ""])
    (reports / "weekly.md").write_text("\n".join(lines), encoding="utf-8")


def run_scan(root, api, now):
    config = read_json(root / "config" / "projects.json")
    reviews = read_json(root / "tracking" / "triage.json")
    contributions = read_json(root / "tracking" / "contributions.json")
    previous_path = root / "data" / "latest.json"
    previous = read_json(previous_path) if previous_path.exists() else {}
    projects = {project["repo"]: project for project in config["projects"]}
    items, coverage = {}, []
    for project in config["projects"]:
        rows, counts = collect_project(api, project, config["scan"])
        for row in rows.values():
            merge_item(items, row)
        coverage.append(counts)
        print(f"采集 {project['repo']}：{len(rows)} 个去重条目", flush=True)
    targets = reviews["entries"] + contributions["entries"] + previous.get("shortlist", [])
    fixed = set()
    for target in targets:
        target_key = key(target)
        fixed.add(target_key)
        if target_key not in items:
            merge_item(items, collect_target(api, target))
    detail_keys = set(fixed)
    for project in config["projects"]:
        rows = [score_item(item, project, config["profile"], now) for item in items.values()
                if item["repo"] == project["repo"] and item["kind"] != "pull_request"]
        rows.sort(key=lambda row: -row["score"])
        detail_keys.update(key(row) for row in rows[:config["scan"]["detail_candidates_per_repo"]])
    for index, item_key in enumerate(sorted(detail_keys), 1):
        check_details(api, items[item_key], config["scan"]["max_detail_pages"])
        if index % 10 == 0:
            print(f"已核查 {index} / {len(detail_keys)} 个重点线程", flush=True)
    review_map = {key(review): review for review in reviews["entries"]}
    for item in items.values():
        score_item(item, projects[item["repo"]], config["profile"], now)
        if key(item) in review_map:
            apply_review(item, review_map[key(item)], now.date())
    rows = sorted(items.values(), key=lambda row: (-row["score"], row["repo"], row["number"]))
    snapshot = {"schema_version": 1, "scanned_at": now.isoformat(timespec="seconds"),
                "coverage_kind": "bounded_windows_with_tracked_refresh", "coverage": coverage,
                "items": rows, "shortlist": choose_shortlist(rows, config["scan"]["report_limit"]),
                "changes": changes_since(previous, rows)}
    # 网络采集和核查全部成功后才更新生成物，人工文件始终只读。
    generate(root, snapshot, contributions)
    return snapshot


def main():
    parser = argparse.ArgumentParser(description="采集并评估 AI Infra issue / Discussion，生成私有报告。")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    try:
        snapshot = run_scan(args.root, GitHub(), now)
    except (RuntimeError, subprocess.TimeoutExpired, OSError, ValueError) as error:
        write_json(args.root / "data" / "scan-status.json", {"ok": False, "scanned_at": now.isoformat(), "error": str(error)})
        print(f"扫描失败，上次成功报告保留：{error}", file=sys.stderr)
        return 1
    write_json(args.root / "data" / "scan-status.json", {"ok": True, "scanned_at": snapshot["scanned_at"]})
    print(f"完成：{len(snapshot['items'])} 个条目，{len(snapshot['shortlist'])} 个阅读候选。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
