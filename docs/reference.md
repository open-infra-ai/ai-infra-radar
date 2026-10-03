# 配置和数据参考

## 采集窗口

`config/projects.json` 使用 `schema_version: 1`。`scan` 的默认预算如下：

| 字段 | 默认 | 含义 |
|---|---|---|
| `recent_issues` | 25 | 每仓按 updatedAt 排序的开放 issue |
| `labelled_issues` | 10 | 每仓分别采集 good first issue 和 help wanted |
| `topic_issues` | 15 | 每个标题检索词的开放 issue；三条主线各有两个词 |
| `discussions` | 6 | 每仓近期更新的 Discussion，包括已关闭条目供状态判断 |
| `detail_candidates_per_repo` | 6 | 每仓初筛高分候选的评论和跨引用核查 |
| `max_detail_pages` | 10 | 每条评论 / 跨引用 connection 最多 10 页，每页 100 条 |
| `report_limit` | 25 | 按参与方式轮转、每仓至多五项的自动机会清单 |

每轮另外读取人工 triage、贡献台账和上一轮机会清单，固定条目不受近期窗口限制。
同一 repo/kind/number 去重，`origins` 记录从哪些窗口发现。
GraphQL 的 connection 参数范围为 1–100；窗口预算不能直接作为全量覆盖声明。

项目字段：`repo` 是 GitHub owner/name，`priority` 使用 1–3，`focus` 是人工关注方向。
可选 `search_terms` 对标题作 GitHub 搜索，排序为最近更新。
`profile.topics` 维护主题与匹配词，`username` 用于区分自己与他人的认领信号。
`profile.hardware` 是有日期背景的环境说明，换机器后人工更新。

## 排序规则

初始分数 = 项目关注权重 × 10。每个匹配主题在标题出现加 10，仅正文出现加 3；
`good first issue` 加 15，`help wanted` 加 8。最近 14 天更新加 10，15–45 天加 5，
超过 120 天减 15。原帖涉及当前未确认的 Hopper/Blackwell/多卡环境减 12；
大范围 tracker、nightly failure 或 security 标题减 25；有 assignee 减 12。
检出他人认领或开放的关闭关联 PR 减 18，仅开放相关 PR 减 8。

这套规则用于控制阅读顺序；硬件词可能只出现在原报告，不能推出所有验证都需要该
硬件。尤其 CPU mock 测试仍可能可行。报告中给出词和参与方式，最终适配由人工判断。

关闭 / 已回答条目退出新机会清单。线程尚未检查或评论内容不完整归到 `verify`；
Discussion 归到 `discuss`；有 assignee、他人认领或关闭关联 PR 归到 `collaborate`；
只有普通相关 PR 归到 `verify`；无人认领信号的 RFC 归到 `discuss`；其余归到
`investigate`，仍需读取当前源码。这里的“无认领信号”仅指未检出。

## 核查边界

- 评论中的 `/claim`、I will work 等表达只构成规则信号，释放认领会撤销同一人的信号；
  间接表达、引用、管理员指派或外部协作可能无法识别。
- Issue 跨引用读取 `CrossReferencedEvent` 的 `willCloseTarget` 和来源 PR 状态，
  不将所有相关 PR 当作修复；新 PR 没有引用 issue 时也可能漏检。
- 评论分页至预算上限。正文保留前 6000 字符，评论保留前 4000 字符；截断有标记。
  认领核查存在评论截断或分页缺口时，不标记完整。
- Discussion 每个一级评论读取最多 100 条回复；超出时标记不完整。
- 已有 PR 核查顶层评论和当前状态，不读取逐行 review threads；跟进前需人工阅读评审与 CI。
- 多个 API 请求的结果不是原子快照；时间戳表示本轮采集开始时间，期间上游仍可能变化。

## 生成数据

`data/latest.json` 保存 `schema_version`、`scanned_at`、`coverage_kind`、`coverage`、
`items`、`shortlist`、`changes`。每个 item 保存来源 URL、状态、日期、正文摘录、
评论摘录、认领信号、关联 PR、分数依据、主题、参与方式和下一步。

`detail_checked` 表示尝试完成线程核查，`detail_complete` 表示在所声明范围内没有
分页 / 评论截断缺口，不表示已审查源代码。`body_truncated` 提醒打开原帖读全文。
人工判断保存在 `manual_review`，不替换上游数据。

`data/history/YYYY-MM-DD.json` 按 UTC 日期保存采集数、覆盖、变化与压缩机会清单，
不包含正文和评论。`reports/daily/` 同日重跑覆盖当日文件，每次提交可从 Git 历史追溯。
`weekly.md` 是最近七个扫描日的操作入口，不自动把浏览、草稿或采集记成实际贡献。

变化分为首次采集、上游更新和明确状态转移；条目从抽样窗口消失不推导关闭。
任一配置仓、固定条目或 API 核查失败时，本轮返回非零，保留旧成功报告。
失败说明写入 Git 忽略的 `data/scan-status.json`，Actions 日志保留具体原因。

## 运行权限

每日任务使用仓库限定的 `GITHUB_TOKEN`，公开上游查询只读，`contents: write`
用于提交本仓生成结果；没有上游写操作。并发组串行扫描；如果推送遇到另一提交，
按普通 Git 冲突失败，重新运行扫描后再提交，不强制覆盖远端。

定时任务要求工作流位于默认分支，运行时间可能延迟；细节见
[GitHub schedule 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。
Token 权限说明见 [GitHub GITHUB_TOKEN 文档](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)。
