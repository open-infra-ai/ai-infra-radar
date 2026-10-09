# AI Infra 贡献机会

扫描时间（UTC）：`2026-10-09T07:23:44+00:00`。

覆盖 12 个项目；去重采集 531 个条目，深读 88 个线程。
近期、入门标签、主线主题和固定条目构成抽样窗口，**不是全量扫描**。分数表示阅读优先级，不表示能解决的概率。
认领是规则识别信号；未检出认领不代表无人工作。API 跨引用只有 `willCloseTarget` 才是关闭关联。

## 人工评估入口

### [ggml-org/llama.cpp #29885](https://github.com/ggml-org/llama.cpp/discussions/29885)：Restart-proof KV cache for llama-server: 40K-token TTFT 155s to 6s after reboot

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

跨重启 KV 恢复适合缓存身份、布局、持久化与正确性分析；帖子中的性能数是作者数据，未在本机验证。

当前核查：已完成配置范围内线程核查；认领仍需人工确认

下一步：阅读作者补丁，设计同前缀/变前缀、模型或 KV dtype 变化、重启与损坏快照的测试矩阵；补充真实测量后再反馈。

### [LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454)：\[Bug\] P2P load timeout can report terminal failure while the transfer is still active

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-04`。

作者 0andy 在完整正文末尾表示愿意修复。已固定 dev 并完成七场景方法级 CPU mock，补充截止后 DONE 仍不轮询的边界；没有运行完整 pytest 或真实 NIXL，也没有复现 KV 损坏。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；作者 0andy 表达工作意愿（需确认是否已开工）: If maintainers agree this is a contract gap, I&#x27;m happy to work on the fix. I&#x27;d especially appreciate guidance on whether the preferred direction is to keep timed-out reads pending until terminal, add a TransferChannel cancell；相关 PR，需判断是否修复 [LMCache/LMCache #5482](https://github.com/LMCache/LMCache/pull/5482)；正文仅保留前 6000 字符，结论需读原帖

下一步：已发布晚轮询测试建议；等待作者反馈，确认分工和预期契约后补充回归测试。

### [sgl-project/sglang #42070](https://github.com/sgl-project/sglang/issues/42070)：\[Bug\] HiCacheFile scans the whole store directory on every existence check, so the scheduler stalls as the store grows

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-04`。

HiCache file lookup 与主线匹配，但已有修复 PR #42077；适合补充复杂度、文件增长与并发修改的验证。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；关闭关联 PR [sgl-project/sglang #42077](https://github.com/sgl-project/sglang/pull/42077)

下一步：先读 #42077 当前补丁和评审，寻找尚未覆盖的回归用例；不重复认领同一修复。

### [flashinfer-ai/flashinfer #5878](https://github.com/flashinfer-ai/flashinfer/issues/5878)：bug(sampling): top_k_arr/min_p_arr are validated against input rows but indexed by output row, reading out of bounds when indices is longer than probs

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-04`。

采样参数的输入/输出行语义适合正确性测试，但已有修复 PR #5921，零评论不代表无人负责。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；原帖涉及 B200, SM100；确认本机路径

下一步：核对 #5921 及 per-row seed/offset 语义，补充 indices 乱序、重复、长度变化的边界测试。

### [vllm-project/vllm #55195](https://github.com/vllm-project/vllm/issues/55195)：\[Bug\]: Reasoning parsers mishandle markers in multi-token streaming deltas

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-05`。

#55210/#56262 已修改基础与 Olmo3 解析器，但未覆盖独立的 Ernie45/HYV4。本轮仅补这两条路径；同一组测试旧源码 5 失败、18 通过，修复后 23 通过；小 Qwen 显式选择解析器的 GPU HTTP/SSE 对照通过，不是原生大模型评测。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；关闭关联 PR [vllm-project/vllm #55210](https://github.com/vllm-project/vllm/pull/55210)；关闭关联 PR [vllm-project/vllm #56262](https://github.com/vllm-project/vllm/pull/56262)；相关 PR，需判断是否修复 [vllm-project/vllm #60195](https://github.com/vllm-project/vllm/pull/60195)；正文仅保留前 6000 字符，结论需读原帖

下一步：先审阅英文评论和具体补丁，再向现有作者确认是否纳入其 PR 或独立补充；不重复认领整个 issue。

### [LMCache/LMCache #5146](https://github.com/LMCache/LMCache/discussions/5146)：Should LMCacheMPConnector honor kv_transfer_config.kv_role — or is MP mode intentionally always-kv_both?

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

MP connector 的 producer/consumer 角色是跨模块语义问题，可用源码与单元测试参与，不要求先拥有原报告的多卡硬件。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；原帖涉及 8×V100；确认本机路径

下一步：对照当前 vLLM 的 kv_role 和 LMCache 单进程/MP connector，列出读写行为差异及 CPU 测试；先确认维护者设计意图。

### [flashinfer-ai/flashinfer #4402](https://github.com/orgs/flashinfer-ai/discussions/4402)：What is the first practical limit of persistent KV across Agent steps?

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

持久化 KV 的模型、tokenizer、adapter 与布局失效边界契合现有经历；话题较旧，评论前重读全线程。

当前核查：已完成配置范围内线程核查；认领仍需人工确认

下一步：提供一个可运行的最小失效案例或测试规范，区分 cache identity、数值兼容和调度影响。

## 可尝试调查 / 复现

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [vllm-project/vllm #59548](https://github.com/vllm-project/vllm/issues/59548) | \[Performance\]: spec-decode boot-to-boot throughput dispersion on L4 (CV up to 13.92%), resolved in 0.30.0 | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [vllm-project/vllm #60703](https://github.com/vllm-project/vllm/issues/60703) | \[Bug\]: glm47 streaming parser silently swallows the rest of the stream (including the real tool call) after a stray `&lt;tool_call&gt;` token in prose | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [ggml-org/llama.cpp #17488](https://github.com/ggml-org/llama.cpp/issues/17488) | GGUF convert support for Vibevoice | 58 / Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [ggml-org/llama.cpp #29498](https://github.com/ggml-org/llama.cpp/issues/29498) | bug: a client-set `X-Conversation-Id` disables disconnect-cancellation and accumulates uncapped resumable-stream sessions, can cause memory DoS | 56 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [triton-lang/triton #12137](https://github.com/triton-lang/triton/issues/12137) | Assertion in TritonAMDGPUCanonicalizePointers: &quot;expected then yield to report fat ptr indices&quot; on a pointer select inside a runtime scf.if | 53 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [ggml-org/llama.cpp #29916](https://github.com/ggml-org/llama.cpp/issues/29916) | llama-quantize: GGML_ASSERT(size mismatch) when quantizing mmproj files containing 3D conv tensors (gemma4v audio conv1d) | 50 / Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [pytorch/pytorch #74809](https://github.com/pytorch/pytorch/issues/74809) | Incorrect results for `torch.distributed.gather` for tensor created from permuted NumPy array | 41 / Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |

## 可参与讨论 / 分析

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [sgl-project/sglang #41366](https://github.com/sgl-project/sglang/discussions/41366) | llm-vram-calc: zero-dependency CLI VRAM + KV-cache calculator for LLM quantizations | 73 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [ggml-org/llama.cpp #29885](https://github.com/ggml-org/llama.cpp/discussions/29885) | Restart-proof KV cache for llama-server: 40K-token TTFT 155s to 6s after reboot | 53 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 阅读作者补丁，设计同前缀/变前缀、模型或 KV dtype 变化、重启与损坏快照的测试矩阵；补充真实测量后再反馈。 |
| [kvcache-ai/Mooncake #1998](https://github.com/kvcache-ai/Mooncake/issues/1998) | \[RFC\]: Radix Tree Index — Prefix-Aware KV Cache Management and Cascading Eviction | 46 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [flashinfer-ai/flashinfer #3736](https://github.com/orgs/flashinfer-ai/discussions/3736) | Performance comparison for dense shared prefix + block-diagonal local mask: custom mask in BatchPrefillWithPagedKVCacheWrapper vs MultiLevelCascadeAttentionWrapper | 43 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [kvcache-ai/Mooncake #2750](https://github.com/kvcache-ai/Mooncake/issues/2750) | \[RFC\]: EPD Disaggregation and Cooperative Scheduling for Agentic Multimodal Inference（CCF 赛题四） | 43 / KV 与存储、Serving 与评测 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [vllm-project/aibrix #2814](https://github.com/vllm-project/aibrix/issues/2814) | \[RFC\]: Agent-Aware KV Cache Affinity Scheduling and Lifecycle Management | 43 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |

## 先确认协作 / 补充验证

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [LMCache/LMCache #5402](https://github.com/LMCache/LMCache/issues/5402) | \[good-first-issue\] tests: make flaky vllm_bench throughput comparisons reproducible | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10；关闭关联 PR [LMCache/LMCache #5493](https://github.com/LMCache/LMCache/pull/5493)；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [LMCache/LMCache #5403](https://github.com/LMCache/LMCache/issues/5403) | \[good-first-issue\] tests: preserve phase timings for flaky long_doc_qa TTFT checks | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10, biluohq, zoushuhang0；关闭关联 PR [LMCache/LMCache #5438](https://github.com/LMCache/LMCache/pull/5438)；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [LMCache/LMCache #5404](https://github.com/LMCache/LMCache/issues/5404) | \[good-first-issue\] tests: retain L2 diagnostics when flaky TTFT checks fail | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10, Tao20060602, ybai08；关闭关联 PR [LMCache/LMCache #5413](https://github.com/LMCache/LMCache/pull/5413)；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [sgl-project/sglang #3050](https://github.com/sgl-project/sglang/issues/3050) | \[Bug\] Decode Throughput Inconsistency Between bench_serving and Engine Logs | 59 / Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；assignee: zhaochenyang20；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [sgl-project/sglang #2272](https://github.com/sgl-project/sglang/issues/2272) | \[Kernel\] cuDNN attention backend | 56 / Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；assignee: ispobock, zhyncs | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [vllm-project/vllm #9129](https://github.com/vllm-project/vllm/issues/9129) | \[Misc\]: CMake Clean-up / Refactor Tasks | 55 / 工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: akshatgit07, jungledesh；相关 PR，需判断是否修复 [vllm-project/vllm #53050](https://github.com/vllm-project/vllm/pull/53050)；关闭关联 PR [vllm-project/vllm #53757](https://github.com/vllm-project/vllm/pull/53757)；相关 PR，需判断是否修复 [vllm-project/vllm #54532](https://github.com/vllm-project/vllm/pull/54532) | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |

## 需进一步核查

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [sgl-project/sglang #36333](https://github.com/sgl-project/sglang/issues/36333) | \[Bug\] Disconnected streaming client leaves a zombie request that decodes to max_tokens and floods &quot;state was deleted in TokenizerManager&quot; (regression from #34160 revert) | 70 / Serving 与评测、Kernel 与正确性、工程与测试 | 核查有分页 / 文本截断 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [sgl-project/sglang #8072](https://github.com/sgl-project/sglang/issues/8072) | \[Feature\] Benchmark with audio input | 65 / Serving 与评测 | 已完成配置范围内线程核查；认领仍需人工确认；相关 PR，需判断是否修复 [sgl-project/sglang #41403](https://github.com/sgl-project/sglang/pull/41403) | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [LMCache/LMCache #5185](https://github.com/LMCache/LMCache/issues/5185) | \[good-first-issue\] examples: convert token_dropping experiment logging to %-format | 61 / Serving 与评测 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [LMCache/LMCache #5187](https://github.com/LMCache/LMCache/issues/5187) | \[good-first-issue\] logging: convert top-level LMCache utility logging to %-format | 61 / Serving 与评测 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [vllm-project/vllm #41515](https://github.com/vllm-project/vllm/issues/41515) | \[Bug\]:  \[kv_offload+HMA\] Fails on chat subsequent request | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 核查有分页 / 文本截断；正文仅保留前 6000 字符，结论需读原帖 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [vllm-project/vllm #59738](https://github.com/vllm-project/vllm/issues/59738) | \[Bug\]: \[Bug\]: deepseek_r1 streaming reasoning deltas are not detokenized (byte-level BPE glyphs) | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 线程尚未核查；正文仅保留前 6000 字符，结论需读原帖 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |

## 已有参与与跟进

| 条目 | 本地进度 | 上游状态 | 跟进日期 | 下一步 |
|---|---|---|---|---|
| [vllm-project/vllm #55195](https://github.com/vllm-project/vllm/issues/55195) | review_pending | OPEN | 2026-10-06（到期） | 用户审阅评论正文；确认后向现有 PR 作者提出补充分工。公开 PR 前逐行理解补丁、运行相关测试，并重新核查上游已有工作。 |
| [LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454) | awaiting_feedback | OPEN | 2026-10-06（到期） | 响应具体反馈；确认测试分工和预期契约后，在上游分支补充晚轮询与 handle 清理的回归测试。 |
| [sgl-project/sglang #36116](https://github.com/sgl-project/sglang/pull/36116) | submitted | OPEN | 2026-10-05（到期） | 阅读当前评审和 CI，确认示例仍与 main 一致，处理具体反馈；有实质更新时再跟进。 |
| [sgl-project/sglang #36115](https://github.com/sgl-project/sglang/pull/36115) | closed | CLOSED | — | 复盘关闭原因和可迁移测试经验；不把关闭表述为合入。 |

本地进度由人工维护，上游状态每轮读取；已关闭且无 merged 时间的 PR 不计为合入。

## 采集覆盖

| 项目 | 近期 issue | 入门标签 | help wanted | Discussion | 标题主题检索 |
|---|---|---|---|---|---|
| sgl-project/sglang | 25 / 948（还有更多） | 10 / 48（还有更多） | 10 / 14（还有更多） | 6 / 414（还有更多） | hicache: 15 / 29（还有更多）；cache: 15 / 76（还有更多） |
| vllm-project/vllm | 25 / 2588（还有更多） | 10 / 20（还有更多） | 10 / 30（还有更多） | 6 / 489（还有更多） | cache: 15 / 308（还有更多）；streaming: 15 / 72（还有更多） |
| LMCache/LMCache | 25 / 223（还有更多） | 10 / 14（还有更多） | 10 / 15（还有更多） | 6 / 6 | L2: 15 / 21（还有更多）；prefetch: 1 / 1 |
| flashinfer-ai/flashinfer | 25 / 353（还有更多） | 5 / 5 | 0 / 0 | 6 / 25（还有更多） | — |
| ggml-org/llama.cpp | 25 / 832（还有更多） | 10 / 17（还有更多） | 10 / 27（还有更多） | 6 / 3749（还有更多） | — |
| triton-lang/triton | 25 / 894（还有更多） | 0 / 0 | 10 / 17（还有更多） | 6 / 176（还有更多） | — |
| kvcache-ai/Mooncake | 25 / 328（还有更多） | 2 / 2 | 1 / 1 | 6 / 7（还有更多） | — |
| NVIDIA/TensorRT-LLM | 25 / 627（还有更多） | 0 / 0 | 0 / 0 | 6 / 180（还有更多） | — |
| NVIDIA/cutlass | 25 / 463（还有更多） | 2 / 2 | 4 / 4 | 6 / 295（还有更多） | — |
| pytorch/pytorch | 25 / 14083（还有更多） | 10 / 43（还有更多） | 0 / 0 | 0 / 0 | — |
| ray-project/ray | 25 / 2855（还有更多） | 0 / 0 | 0 / 0 | 0 / 0 | — |
| vllm-project/aibrix | 25 / 346（还有更多） | 8 / 8 | 10 / 18（还有更多） | 0 / 0 | — |

分母是 API 该窗口的可用条目数；不同窗口可能重叠。固定条目另行刷新，Discussion 关闭或已回答的条目保留数据但不列为新机会。

## 本轮变化

上游更新 37、首次采集 150

条目离开抽样窗口不能推导已关闭；固定条目与上一轮机会清单会继续核对状态。
