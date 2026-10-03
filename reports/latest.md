# AI Infra 贡献机会

扫描时间（UTC）：`2026-10-03T17:57:50+00:00`。

覆盖 12 个项目；去重采集 518 个条目，深读 81 个线程。
近期、入门标签、主线主题和固定条目构成抽样窗口，**不是全量扫描**。分数表示阅读优先级，不表示能解决的概率。
认领是规则识别信号；未检出认领不代表无人工作。API 跨引用只有 `willCloseTarget` 才是关闭关联。

## 人工评估入口

### [LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454)：\[Bug\] P2P load timeout can report terminal failure while the transfer is still active

参与方式：**可尝试调查 / 复现**；人工评估日期：`2026-10-04`。

与 KV buffer 生命周期研究匹配；报告含 CPU mock 测试，需先确认 terminal result 是否保证传输停止，不能直接把观察到的行为断言为数据损坏。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖

下一步：固定当前 dev，重跑 CPU 模拟测试，画出 timeout → result → unlock → reclaim 顺序；向维护者确认契约后再考虑修复。

### [ggml-org/llama.cpp #29885](https://github.com/ggml-org/llama.cpp/discussions/29885)：Restart-proof KV cache for llama-server: 40K-token TTFT 155s to 6s after reboot

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

跨重启 KV 恢复适合缓存身份、布局、持久化与正确性分析；帖子中的性能数是作者数据，未在本机验证。

当前核查：已完成配置范围内线程核查；认领仍需人工确认

下一步：阅读作者补丁，设计同前缀/变前缀、模型或 KV dtype 变化、重启与损坏快照的测试矩阵；补充真实测量后再反馈。

### [sgl-project/sglang #42070](https://github.com/sgl-project/sglang/issues/42070)：\[Bug\] HiCacheFile scans the whole store directory on every existence check, so the scheduler stalls as the store grows

参与方式：**已有工作：协作验证 / 补测试**；人工评估日期：`2026-10-04`。

HiCache file lookup 与主线匹配，但已有修复 PR #42077；适合补充复杂度、文件增长与并发修改的验证。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；关闭关联 PR [sgl-project/sglang #42077](https://github.com/sgl-project/sglang/pull/42077)

下一步：先读 #42077 当前补丁和评审，寻找尚未覆盖的回归用例；不重复认领同一修复。

### [flashinfer-ai/flashinfer #5878](https://github.com/flashinfer-ai/flashinfer/issues/5878)：bug(sampling): top_k_arr/min_p_arr are validated against input rows but indexed by output row, reading out of bounds when indices is longer than probs

参与方式：**已有工作：协作验证 / 补测试**；人工评估日期：`2026-10-04`。

采样参数的输入/输出行语义适合正确性测试，但已有修复 PR #5921，零评论不代表无人负责。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；关闭关联 PR [flashinfer-ai/flashinfer #5921](https://github.com/flashinfer-ai/flashinfer/pull/5921)；原帖涉及 B200, SM100；确认本机路径

下一步：核对 #5921 及 per-row seed/offset 语义，补充 indices 乱序、重复、长度变化的边界测试。

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
| [ggml-org/llama.cpp #17488](https://github.com/ggml-org/llama.cpp/issues/17488) | GGUF convert support for Vibevoice | 58 / Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454) | \[Bug\] P2P load timeout can report terminal failure while the transfer is still active | 56 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 固定当前 dev，重跑 CPU 模拟测试，画出 timeout → result → unlock → reclaim 顺序；向维护者确认契约后再考虑修复。 |
| [ggml-org/llama.cpp #29916](https://github.com/ggml-org/llama.cpp/issues/29916) | llama-quantize: GGML_ASSERT(size mismatch) when quantizing mmproj files containing 3D conv tensors (gemma4v audio conv1d) | 50 / Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [triton-lang/triton #11875](https://github.com/triton-lang/triton/issues/11875) | \[Robustness\]: Observations on missing defensive bounds checks in TritonGPU layout conversions | 43 / Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [flashinfer-ai/flashinfer #5724](https://github.com/flashinfer-ai/flashinfer/issues/5724) | \[Bug\] tests/attention/test_cake_fmha.py timeout B200 | 38 / Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；原帖涉及 B200；确认本机路径 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [ray-project/ray #66662](https://github.com/ray-project/ray/issues/66662) | \[Core\] Ray Client: specific-server child killed in gRPC atfork handler -- &quot;Starting Ray client server failed&quot;, empty .err, 40s to surface | 36 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [vllm-project/aibrix #1047](https://github.com/vllm-project/aibrix/issues/1047) | \[CICD\] Optimize kv cache image size | 36 / KV 与存储、Serving 与评测 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |

## 可参与讨论 / 分析

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [sgl-project/sglang #41366](https://github.com/sgl-project/sglang/discussions/41366) | llm-vram-calc: zero-dependency CLI VRAM + KV-cache calculator for LLM quantizations | 73 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [ggml-org/llama.cpp #29885](https://github.com/ggml-org/llama.cpp/discussions/29885) | Restart-proof KV cache for llama-server: 40K-token TTFT 155s to 6s after reboot | 53 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 阅读作者补丁，设计同前缀/变前缀、模型或 KV dtype 变化、重启与损坏快照的测试矩阵；补充真实测量后再反馈。 |
| [kvcache-ai/Mooncake #2703](https://github.com/kvcache-ai/Mooncake/issues/2703) | \[RFC\]: Explicit Context Caching — Guaranteed KV Cache Eviction Protection | 49 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [flashinfer-ai/flashinfer #3736](https://github.com/orgs/flashinfer-ai/discussions/3736) | Performance comparison for dense shared prefix + block-diagonal local mask: custom mask in BatchPrefillWithPagedKVCacheWrapper vs MultiLevelCascadeAttentionWrapper | 43 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [vllm-project/aibrix #2814](https://github.com/vllm-project/aibrix/issues/2814) | \[RFC\]: Agent-Aware KV Cache Affinity Scheduling and Lifecycle Management | 43 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [NVIDIA/cutlass #3657](https://github.com/NVIDIA/cutlass/discussions/3657) | CUTLASS 4.8.0 | 32 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |

## 已有工作：协作验证 / 补测试

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [LMCache/LMCache #5402](https://github.com/LMCache/LMCache/issues/5402) | \[good-first-issue\] tests: make flaky vllm_bench throughput comparisons reproducible | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10, soyeladice-svg；关闭关联 PR [LMCache/LMCache #5409](https://github.com/LMCache/LMCache/pull/5409)；正文仅保留前 6000 字符，结论需读原帖 | 先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。 |
| [LMCache/LMCache #5403](https://github.com/LMCache/LMCache/issues/5403) | \[good-first-issue\] tests: preserve phase timings for flaky long_doc_qa TTFT checks | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10, biluohq, zoushuhang0；关闭关联 PR [LMCache/LMCache #5438](https://github.com/LMCache/LMCache/pull/5438)；正文仅保留前 6000 字符，结论需读原帖 | 先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。 |
| [LMCache/LMCache #5404](https://github.com/LMCache/LMCache/issues/5404) | \[good-first-issue\] tests: retain L2 diagnostics when flaky TTFT checks fail | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10, Tao20060602, ybai08；关闭关联 PR [LMCache/LMCache #5413](https://github.com/LMCache/LMCache/pull/5413)；正文仅保留前 6000 字符，结论需读原帖 | 先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。 |
| [sgl-project/sglang #2272](https://github.com/sgl-project/sglang/issues/2272) | \[Kernel\] cuDNN attention backend | 61 / Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；assignee: ispobock, zhyncs | 先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。 |
| [vllm-project/vllm #9129](https://github.com/vllm-project/vllm/issues/9129) | \[Misc\]: CMake Clean-up / Refactor Tasks | 55 / 工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: akshatgit07, jungledesh；相关 PR，需判断是否修复 [vllm-project/vllm #53050](https://github.com/vllm-project/vllm/pull/53050)；关闭关联 PR [vllm-project/vllm #53757](https://github.com/vllm-project/vllm/pull/53757)；相关 PR，需判断是否修复 [vllm-project/vllm #54532](https://github.com/vllm-project/vllm/pull/54532) | 先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。 |
| [vllm-project/vllm #23957](https://github.com/vllm-project/vllm/issues/23957) | \[Feature\]: Support `Phi4Flash` model in V1 | 48 / Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: AmanBhattShorthillsAI, aditchawdhary；关闭关联 PR [vllm-project/vllm #44963](https://github.com/vllm-project/vllm/pull/44963) | 先读已有 PR / 认领评论，寻找未覆盖测试、复现条件或评审问题。 |

## 需进一步核查

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [LMCache/LMCache #5203](https://github.com/LMCache/LMCache/issues/5203) | \[good-first-issue\] tests: convert disagg channel logging to %-format | 66 / Serving 与评测 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [sgl-project/sglang #8072](https://github.com/sgl-project/sglang/issues/8072) | \[Feature\] Benchmark with audio input | 65 / Serving 与评测 | 已完成配置范围内线程核查；认领仍需人工确认；相关 PR，需判断是否修复 [sgl-project/sglang #41403](https://github.com/sgl-project/sglang/pull/41403) | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [sgl-project/sglang #2271](https://github.com/sgl-project/sglang/issues/2271) | \[Kernel\] Optimize triton decoding kernels for long context | 64 / Serving 与评测、Kernel 与正确性 | 线程尚未核查；assignee: HaiShaw | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [sgl-project/sglang #3050](https://github.com/sgl-project/sglang/issues/3050) | \[Bug\] Decode Throughput Inconsistency Between bench_serving and Engine Logs | 59 / Serving 与评测、Kernel 与正确性 | 线程尚未核查；assignee: zhaochenyang20；正文仅保留前 6000 字符，结论需读原帖 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [vllm-project/vllm #47161](https://github.com/vllm-project/vllm/issues/47161) | \[RFC\]: Streaming Derender for Disaggregated Serving | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 线程尚未核查；正文仅保留前 6000 字符，结论需读原帖 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [vllm-project/vllm #48020](https://github.com/vllm-project/vllm/issues/48020) | \[Bug\]: DeepSeek-V3/V3.1 tool parser drops the tool call when start+end tokens land in the same streaming delta | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |

## 已有参与与跟进

| 条目 | 本地进度 | 上游状态 | 跟进日期 | 下一步 |
|---|---|---|---|---|
| [sgl-project/sglang #36116](https://github.com/sgl-project/sglang/pull/36116) | submitted | OPEN | 2026-10-05 | 阅读当前评审和 CI，确认示例仍与 main 一致，处理具体反馈；有实质更新时再跟进。 |
| [sgl-project/sglang #36115](https://github.com/sgl-project/sglang/pull/36115) | closed | CLOSED | — | 复盘关闭原因和可迁移测试经验；不把关闭表述为合入。 |

本地进度由人工维护，上游状态每轮读取；已关闭且无 merged 时间的 PR 不计为合入。

## 采集覆盖

| 项目 | 近期 issue | 入门标签 | help wanted | Discussion | 标题主题检索 |
|---|---|---|---|---|---|
| sgl-project/sglang | 25 / 945（还有更多） | 10 / 49（还有更多） | 10 / 15（还有更多） | 6 / 413（还有更多） | hicache: 15 / 26（还有更多）；cache: 15 / 78（还有更多） |
| vllm-project/vllm | 25 / 2569（还有更多） | 10 / 21（还有更多） | 10 / 32（还有更多） | 6 / 489（还有更多） | cache: 15 / 304（还有更多）；streaming: 15 / 72（还有更多） |
| LMCache/LMCache | 25 / 225（还有更多） | 10 / 15（还有更多） | 10 / 16（还有更多） | 6 / 6 | L2: 15 / 22（还有更多）；prefetch: 2 / 2 |
| flashinfer-ai/flashinfer | 25 / 390（还有更多） | 5 / 5 | 0 / 0 | 6 / 25（还有更多） | — |
| ggml-org/llama.cpp | 25 / 869（还有更多） | 10 / 17（还有更多） | 10 / 27（还有更多） | 6 / 3725（还有更多） | — |
| triton-lang/triton | 25 / 895（还有更多） | 0 / 0 | 10 / 17（还有更多） | 6 / 175（还有更多） | — |
| kvcache-ai/Mooncake | 25 / 314（还有更多） | 2 / 2 | 1 / 1 | 6 / 7（还有更多） | — |
| NVIDIA/TensorRT-LLM | 25 / 611（还有更多） | 0 / 0 | 0 / 0 | 6 / 180（还有更多） | — |
| NVIDIA/cutlass | 25 / 464（还有更多） | 2 / 2 | 4 / 4 | 6 / 295（还有更多） | — |
| pytorch/pytorch | 25 / 14048（还有更多） | 10 / 44（还有更多） | 0 / 0 | 0 / 0 | — |
| ray-project/ray | 25 / 2840（还有更多） | 0 / 0 | 0 / 0 | 0 / 0 | — |
| vllm-project/aibrix | 25 / 352（还有更多） | 8 / 8 | 10 / 18（还有更多） | 0 / 0 | — |

分母是 API 该窗口的可用条目数；不同窗口可能重叠。固定条目另行刷新，Discussion 关闭或已回答的条目保留数据但不列为新机会。

## 本轮变化

首次采集 67

条目离开抽样窗口不能推导已关闭；固定条目与上一轮机会清单会继续核对状态。
