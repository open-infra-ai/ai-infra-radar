# 参与与跟进操作

适用于从报告选中一个事项后，记录自己的调查与上游参与。公开反馈由本人审阅发布。

## 记录新事项

例如准备调查 LMCache 的超时契约：

```bash
python3 scripts/track.py add \
  --repo LMCache/LMCache --kind issue --number 5454 \
  --status selected \
  --summary '调查超时结果与在途传输的 buffer 生命周期' \
  --next-step '固定 dev commit，重跑 CPU mock 测试，确认 terminal result 契约' \
  --follow-up-on 2026-10-06 \
  --evidence https://github.com/LMCache/LMCache/issues/5454
```

命令只修改本地 `tracking/contributions.json`，不会创建上游 issue 或发评论。
该事项下次扫描会固定刷新，进度由你维护。先用 `list` 查找 ID：

```bash
python3 scripts/track.py list
```

## 更新进度与证据

```bash
python3 scripts/track.py update LMCache-LMCache-issue-5454 \
  --status reproducing \
  --next-step '核对模拟测试与真实传输的差异，整理结果' \
  --follow-up-on 2026-10-08
```

发布评论或 PR 后，更新为 `submitted` 或 `awaiting_feedback`，用 `--evidence` 保存
实际上游链接。完成或决定暂停时，用 `--clear-follow-up` 取消原跟进日期。
日期示例需按实际安排调整，台账不根据日期自动发消息。

本地进度可选：`selected`、`reproducing`、`analyzing`、`drafted`、`submitted`、
`awaiting_feedback`、`merged`、`closed`、`paused`。上游状态由扫描另列，发现不一致时
人工更新；没有上游 merged 证据不能把关闭 PR 记成合入。

## 写一份有依据的参与记录

复制 [模板](../tracking/participation-template.md) 到自己选定的调查文档中：

- 说明一个具体观察，列出源码版本和复现命令。
- 保存原始输出，区分实测、源码分析和待确认假设。
- 指向已经阅读的关联 PR，说明自己的证据增加了什么。
- 以一个可回答的问题或可审阅的补丁收尾，记录维护者反馈。

大模型或多卡复现不足时，可贡献 CPU 测试、接口契约、日志分析或评测方法；
明确这些证据的边界。已有修复 PR 时，优先验证补丁、补充遗漏场景。

已完成的 [LMCache #5454 调查记录](investigations/lmcache-5454/README.md) 展示了
方法级 CPU probe、源码推断与未验证假设的区分，以及已发布反馈和持续跟进的记录。

## 调整人工评估

编辑 [tracking/triage.json](../tracking/triage.json) 添加条目，填写 `repo`、`kind`、
`number`、`reviewed_at`、`mode`、`reason`、`next_step` 和 `evidence`。
`mode` 使用 `investigate`、`discuss`、`collaborate` 或 `verify`。

新评估仍受当前状态约束：关闭事项不会因人工标注重新成为开放机会，已有认领或
未完成核查不能被 `investigate` 覆盖。超过 14 天的人工判断在报告中提示刷新。
固定条目必须属于 `config/projects.json` 中的项目；日期使用 `YYYY-MM-DD`。

## 保存与复盘

```bash
python3 scripts/scan.py
npm test
npm run verify-notes
git add tracking data reports
git diff --cached --check
git commit -m 'docs(tracking): record contribution progress'
git push
```

每周查看 [weekly.md](../reports/weekly.md)：已给出的新证据、实际收到的反馈、
下一次具体行动。连续跟进一个技术问题比只增加收藏数量更有价值。
