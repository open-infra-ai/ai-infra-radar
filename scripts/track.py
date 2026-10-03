#!/usr/bin/env python3
import argparse
from datetime import date
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("selected", "reproducing", "analyzing", "drafted", "submitted", "awaiting_feedback", "merged", "closed", "paused")


def day(value):
    return date.fromisoformat(value).isoformat()


def main():
    parser = argparse.ArgumentParser(description="在本地维护贡献台账；不向上游发消息。")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="添加一个参与事项")
    add.add_argument("--repo", required=True)
    add.add_argument("--kind", choices=("issue", "discussion", "pull_request"), required=True)
    add.add_argument("--number", type=int, required=True)
    add.add_argument("--summary", required=True)
    update = commands.add_parser("update", help="更新一个已有事项")
    update.add_argument("id")
    for command in (add, update):
        command.add_argument("--status", choices=STATUSES, required=True)
        command.add_argument("--next-step", required=True)
        command.add_argument("--evidence", action="append", default=[])
        dates = command.add_mutually_exclusive_group()
        dates.add_argument("--follow-up-on", type=day)
        dates.add_argument("--clear-follow-up", action="store_true")
    commands.add_parser("list", help="列出已有事项")
    args = parser.parse_args()
    path = ROOT / "tracking" / "contributions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if args.command == "list":
        for row in data["entries"]:
            print(f"{row['id']}: {row['status']} | 跟进 {row['follow_up_on'] or '—'} | {row['next_step']}")
        return
    if args.command == "add":
        projects = json.loads((ROOT / "config" / "projects.json").read_text(encoding="utf-8"))
        if args.repo not in {project["repo"] for project in projects["projects"]}:
            parser.error("请先把项目加入 config/projects.json，再记录参与事项。")
        if args.number <= 0:
            parser.error("number 必须为正整数。")
        record_id = f"{args.repo.replace('/', '-')}-{args.kind}-{args.number}"
        if any(row["id"] == record_id for row in data["entries"]):
            parser.error(f"条目 {record_id} 已存在，请用 update。")
        record = {"id": record_id, "repo": args.repo, "kind": args.kind, "number": args.number,
                  "summary": args.summary, "follow_up_on": None, "evidence": []}
        data["entries"].append(record)
    else:
        record = next((row for row in data["entries"] if row["id"] == args.id), None)
        if record is None:
            parser.error(f"未找到条目 {args.id}。")
    record.update(status=args.status, next_step=args.next_step, last_action_at=date.today().isoformat())
    if args.follow_up_on or args.clear_follow_up:
        record["follow_up_on"] = args.follow_up_on
    for url in args.evidence:
        if url not in record["evidence"]:
            record["evidence"].append(url)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已更新本地台账：{record['id']}；提交推送后才同步到 GitHub。")


if __name__ == "__main__":
    main()
