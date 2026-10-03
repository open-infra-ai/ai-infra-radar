# AI Infra Radar

私有的 AI Infra 社区参与工作台：每天发现值得阅读的 issue、Discussion 与 RFC，
结合自己的技术经历判断参与方式，记录复现、分析、评论、PR 和后续反馈。

直接打开 [最新机会报告](reports/latest.md)、[每周跟进入口](reports/weekly.md)。
优先从报告里的人工评估入口选择一项；每周深入参与 2–3 项，并持续回应已有 PR。

## 关注方向

- 主线：SGLang HiCache / KV offloading、vLLM Serving、LMCache 缓存生命周期。
- 第二线：FlashInfer 采样与 attention、llama.cpp GGUF / KV 持久化、Triton 正确性、Mooncake 传输。
- 观察：TensorRT-LLM、CUTLASS、PyTorch、Ray Serve、AIBrix。

完整的 12 仓配置、关注权重和关键词见 [config/projects.json](config/projects.json)。
初始化时本机核查为 RTX 3060 Laptop 6 GiB；CPU 测试和单卡小模型优先，原报告需要
H100/B200 或多卡的事项必须另外判断资源。参与源码分析不等于已复现 GPU 性能问题。

## 每日更新

[Daily AI Infra Radar](https://github.com/open-infra-ai/ai-infra-radar/actions/workflows/daily-scan.yml)
按北京时间 **09:17**（UTC 01:17）安排运行，也可以在 Actions 页面选择 **Run workflow**。
GitHub 的定时调度可能延迟，报告内时间戳是实际采集时间。

自动化读取公开上游，只向本私有仓的 `data/` 和 `reports/` 提交生成结果。
它不发布上游评论、不认领 issue、不自动提交上游 PR。扫描或核查失败会让工作流失败，
保留上一份成功报告；从 Actions 日志查看原因。工作流使用仓库自带 `GITHUB_TOKEN`，
无需配置个人 token 或付费模型服务。

## 本地使用

需要 Python 3.12+、GitHub CLI、Node.js 24+。扫描器本身只用 Python 标准库；
Node.js 用于工作区要求的决策笔记校验。

```bash
gh auth login
gh repo clone open-infra-ai/ai-infra-radar
cd ai-infra-radar
npm ci
npm test
npm run verify-notes
python3 scripts/scan.py
```

执行扫描会更新本地生成文件；本地变更通过正常的 Git 提交推送同步。
已登录 gh 时无需把 token 写入文件。Actions 使用的版本和提交固定在工作流中。

## 怎样判断一项机会

| 报告类别 | 建议行动 |
|---|---|
| 可尝试调查 / 复现 | 确认当前源码、最小复现、资源和贡献指南，判断是否有独立可交付任务 |
| 可参与讨论 / 分析 | 提供一个源码依据、反例或最小实验，先确认设计意图 |
| 已有工作：协作验证 / 补测试 | 阅读已有认领与 PR，补充尚未覆盖的测试或评审证据 |
| 需进一步核查 | 补齐未读取的线程、截断正文或关联 PR 的语义后再决定 |

分数是透明规则下的阅读顺序，**不是能力认证或成功率**。高分不等于可以直接修复，
零评论不等于无人负责，`good first issue` 不保证适合本机硬件。关联 PR 也不一定是
修复：只有 API 的关闭关联才明确表示合入将关闭 issue。

自动发现包括近期窗口、入门标签、三条主线的标题主题检索；重点候选会分页检查评论
与 issue 交叉引用。报告列出每个窗口的采集数和可用数，不宣称全量覆盖。
人工固定条目和上一轮机会清单持续核查，因此能观察关闭、合入和上游更新。

## 从发现到持续参与

1. 在最新报告里选择一项，打开完整线程，检查当前分支、贡献指南和正在进行的工作。
2. 固定源码 commit、环境和命令；优先完成一个 CPU / 单卡复现或边界测试。
3. 使用 [参与记录模板](tracking/participation-template.md) 组织证据，明确已验证与推断的范围。
4. 本人审阅后发布有新增信息的评论或 PR，保存上游链接，再记录反馈和跟进日期。

具体台账命令见 [参与与跟进操作](docs/participation.md)；数据字段、排序与采集边界见
[配置和数据参考](docs/reference.md)。自动扫描只读取人工台账，不改变你记录的进度。

## 文件归属

| 位置 | 内容 | 维护方式 |
|---|---|---|
| `config/projects.json` | 目标仓、技能关键词、采集预算 | 人工修改 |
| `tracking/triage.json` | 逐项适配理由、参与方式和下一步 | 人工评估，超过 14 天标记需刷新 |
| `tracking/contributions.json` | 已参与事项、证据链接与跟进日期 | 人工或 `scripts/track.py` |
| `data/latest.json` | 本轮详细来源、评论摘录、跨引用与规则结果 | 扫描生成 |
| `data/history/` | 按 UTC 日期压缩的机会快照 | 扫描生成 |
| `reports/` | 最新、每日与最近七个扫描日的复盘入口 | 扫描生成 |
| `.agents/notes/` | 行为、格式与工具链的设计理由 | 与相关代码同批维护 |

日快照同一天重跑会更新该日期文件；每次提交仍可从 Git 历史追溯。
历史快照不保留全量正文，详细数据只在 latest 和 Git 历史中保留。
本仓是个人执行材料，不加入公开技术作品状态注册表；复现实验仍放在对应技术仓或
上游分支，最终贡献证据指向上游评论、PR、CI 和 commit。
