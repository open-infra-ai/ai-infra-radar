# AI Infra 贡献机会

扫描时间（UTC）：`2026-10-19T06:12:54+00:00`。

覆盖 12 个项目；去重采集 539 个条目，深读 92 个线程。
近期、入门标签、主线主题和固定条目构成抽样窗口，**不是全量扫描**。分数表示阅读优先级，不表示能解决的概率。
认领是规则识别信号；未检出认领不代表无人工作。API 跨引用只有 `willCloseTarget` 才是关闭关联。

## 人工评估入口

### [sgl-project/sglang #42070](https://github.com/sgl-project/sglang/issues/42070)：\[Bug\] HiCacheFile scans the whole store directory on every existence check, so the scheduler stalls as the store grows

参与方式：**已关闭 / 已回答**；人工评估日期：`2026-10-04`。

HiCache file lookup 与主线匹配，但已有修复 PR #42077；适合补充复杂度、文件增长与并发修改的验证。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；人工评估超过 14 天，需更新

下一步：复盘上游结论，核对是否仍有可补充的证据。

### [LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454)：\[Bug\] P2P load timeout can report terminal failure while the transfer is still active

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-04`。

作者 0andy 在完整正文末尾表示愿意修复。已固定 dev 并完成七场景方法级 CPU mock，补充截止后 DONE 仍不轮询的边界；没有运行完整 pytest 或真实 NIXL，也没有复现 KV 损坏。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；作者 0andy 表达工作意愿（需确认是否已开工）: If maintainers agree this is a contract gap, I&#x27;m happy to work on the fix. I&#x27;d especially appreciate guidance on whether the preferred direction is to keep timed-out reads pending until terminal, add a TransferChannel cancell；相关 PR，需判断是否修复 [LMCache/LMCache #5482](https://github.com/LMCache/LMCache/pull/5482)；人工评估超过 14 天，需更新；正文仅保留前 6000 字符，结论需读原帖

下一步：已发布晚轮询测试建议；等待作者反馈，确认分工和预期契约后补充回归测试。

### [ggml-org/llama.cpp #29885](https://github.com/ggml-org/llama.cpp/discussions/29885)：Restart-proof KV cache for llama-server: 40K-token TTFT 155s to 6s after reboot

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

跨重启 KV 恢复适合缓存身份、布局、持久化与正确性分析；帖子中的性能数是作者数据，未在本机验证。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；人工评估超过 14 天，需更新

下一步：阅读作者补丁，设计同前缀/变前缀、模型或 KV dtype 变化、重启与损坏快照的测试矩阵；补充真实测量后再反馈。

### [vllm-project/vllm #55195](https://github.com/vllm-project/vllm/issues/55195)：\[Bug\]: Reasoning parsers mishandle markers in multi-token streaming deltas

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-05`。

#55210/#56262 已修改基础与 Olmo3 解析器，但未覆盖独立的 Ernie45/HYV4。本轮仅补这两条路径；同一组测试旧源码 5 失败、18 通过，修复后 23 通过；小 Qwen 显式选择解析器的 GPU HTTP/SSE 对照通过，不是原生大模型评测。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；关闭关联 PR [vllm-project/vllm #55210](https://github.com/vllm-project/vllm/pull/55210)；关闭关联 PR [vllm-project/vllm #56262](https://github.com/vllm-project/vllm/pull/56262)；相关 PR，需判断是否修复 [vllm-project/vllm #60195](https://github.com/vllm-project/vllm/pull/60195)；正文仅保留前 6000 字符，结论需读原帖

下一步：先审阅英文评论和具体补丁，再向现有作者确认是否纳入其 PR 或独立补充；不重复认领整个 issue。

### [flashinfer-ai/flashinfer #5878](https://github.com/flashinfer-ai/flashinfer/issues/5878)：bug(sampling): top_k_arr/min_p_arr are validated against input rows but indexed by output row, reading out of bounds when indices is longer than probs

参与方式：**先确认协作 / 补充验证**；人工评估日期：`2026-10-04`。

采样参数的输入/输出行语义适合正确性测试，但已有修复 PR #5921，零评论不代表无人负责。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；相关 PR，需判断是否修复 [flashinfer-ai/flashinfer #6730](https://github.com/flashinfer-ai/flashinfer/pull/6730)；原帖涉及 B200, SM100；确认本机路径；人工评估超过 14 天，需更新

下一步：核对 #5921 及 per-row seed/offset 语义，补充 indices 乱序、重复、长度变化的边界测试。

### [flashinfer-ai/flashinfer #4402](https://github.com/orgs/flashinfer-ai/discussions/4402)：What is the first practical limit of persistent KV across Agent steps?

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

持久化 KV 的模型、tokenizer、adapter 与布局失效边界契合现有经历；话题较旧，评论前重读全线程。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；人工评估超过 14 天，需更新

下一步：提供一个可运行的最小失效案例或测试规范，区分 cache identity、数值兼容和调度影响。

### [LMCache/LMCache #5146](https://github.com/LMCache/LMCache/discussions/5146)：Should LMCacheMPConnector honor kv_transfer_config.kv_role — or is MP mode intentionally always-kv_both?

参与方式：**可参与讨论 / 分析**；人工评估日期：`2026-10-04`。

MP connector 的 producer/consumer 角色是跨模块语义问题，可用源码与单元测试参与，不要求先拥有原报告的多卡硬件。

当前核查：已完成配置范围内线程核查；认领仍需人工确认；原帖涉及 8×V100；确认本机路径；人工评估超过 14 天，需更新

下一步：对照当前 vLLM 的 kv_role 和 LMCache 单进程/MP connector，列出读写行为差异及 CPU 测试；先确认维护者设计意图。

## 可尝试调查 / 复现

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [LMCache/LMCache #5848](https://github.com/LMCache/LMCache/issues/5848) | \[Feature Request\]\[MP\] Concurrent multi-turn benchmark for memory-budget-aware KV offload and retrieval | 63 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [sgl-project/sglang #44786](https://github.com/sgl-project/sglang/issues/44786) | \[RFC / Feature\] SPICY-KV: 28.6x–50x Pre-RoPE Algebraic Multigrid KV Compression for RadixAttention &amp; Long-CoT (91.7%–100% RULER Recall &amp; 100% Shared-Prefix Multi-Query Reuse) | 63 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [flashinfer-ai/flashinfer #6305](https://github.com/flashinfer-ai/flashinfer/issues/6305) | \[Bug\]\[v0.7.2rc2\] tests/attention/test_cudnn_wrapper_regressions.py::test_paged_prefill_default_scale_layout_lse\[True-ln-NHD\] AssertionError: Tensor-likes are not close!  Mismatched elements: 4985 / 5120 (97.4%) | 60 / Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [vllm-project/vllm #59548](https://github.com/vllm-project/vllm/issues/59548) | \[Performance\]: spec-decode boot-to-boot throughput dispersion on L4 (CV up to 13.92%), resolved in 0.30.0 | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [vllm-project/vllm #60581](https://github.com/vllm-project/vllm/issues/60581) | \[Usage\]: ROCm gfx950: MXFP4 activation quant not fused into GEMM; Quark INT4 W4A16 uses a very slow Triton kernel | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [ggml-org/llama.cpp #30793](https://github.com/ggml-org/llama.cpp/issues/30793) | ### Regression: first-inference TTFT 10s → 60s+ with large CPU-resident MoE weights after #30449 | 56 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |
| [ggml-org/llama.cpp #29078](https://github.com/ggml-org/llama.cpp/issues/29078) | convert_hf_to_gguf.py: very large models need either the full model in RAM or 2x its size on disk (streaming two-pass mode?) | 53 / Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读当前源码与贡献指南，验证最小复现和测试范围，再确认是否有重复工作。 |

## 可参与讨论 / 分析

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [sgl-project/sglang #41366](https://github.com/sgl-project/sglang/discussions/41366) | llm-vram-calc: zero-dependency CLI VRAM + KV-cache calculator for LLM quantizations | 68 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [ggml-org/llama.cpp #29885](https://github.com/ggml-org/llama.cpp/discussions/29885) | Restart-proof KV cache for llama-server: 40K-token TTFT 155s to 6s after reboot | 48 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；人工评估超过 14 天，需更新 | 阅读作者补丁，设计同前缀/变前缀、模型或 KV dtype 变化、重启与损坏快照的测试矩阵；补充真实测量后再反馈。 |
| [kvcache-ai/Mooncake #2898](https://github.com/kvcache-ai/Mooncake/issues/2898) | \[RFC\]: Parallelize long-running Mooncake Store unit tests | 46 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [kvcache-ai/Mooncake #2953](https://github.com/kvcache-ai/Mooncake/issues/2953) | \[RFC\]: \[Store\] Recoverable client liveness states and asynchronous offboarding | 46 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [kvcache-ai/Mooncake #3786](https://github.com/kvcache-ai/Mooncake/issues/3786) | \[RFC\]: Add GDS offload for mooncake-store based on existing TENT gds transport | 46 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；正文仅保留前 6000 字符，结论需读原帖 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |
| [flashinfer-ai/flashinfer #3736](https://github.com/orgs/flashinfer-ai/discussions/3736) | Performance comparison for dense shared prefix + block-diagonal local mask: custom mask in BatchPrefillWithPagedKVCacheWrapper vs MultiLevelCascadeAttentionWrapper | 43 / KV 与存储、Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认 | 读完整线程，提出一个有源码依据的解释、反例或最小实验。 |

## 先确认协作 / 补充验证

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [LMCache/LMCache #5402](https://github.com/LMCache/LMCache/issues/5402) | \[good-first-issue\] tests: make flaky vllm_bench throughput comparisons reproducible | 68 / KV 与存储、Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10；关闭关联 PR [LMCache/LMCache #5493](https://github.com/LMCache/LMCache/pull/5493)；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [sgl-project/sglang #3050](https://github.com/sgl-project/sglang/issues/3050) | \[Bug\] Decode Throughput Inconsistency Between bench_serving and Engine Logs | 59 / Serving 与评测、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；assignee: zhaochenyang20；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [LMCache/LMCache #5313](https://github.com/LMCache/LMCache/issues/5313) | \[good-first-issue\] tests: stabilize flaky CI tests from recent PRs | 58 / Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: VinsmokeSanji33, Zhou-Kan；正文仅保留前 6000 字符，结论需读原帖 | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [vllm-project/vllm #32335](https://github.com/vllm-project/vllm/issues/32335) | \[Feature\]: Extract KV-Cache update from all attention backends | 53 / KV 与存储、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；assignee: VedantMadane, pragun-ananda, Mohit-Gaur, Prathmesh234, adityakamat24, Etelis, dorhuri123, dw2761, Kare0638；评论认领信号: Etelis, Kare0638, kaushik-rohit；相关 PR，需判断是否修复 [vllm-project/vllm #33405](https://github.com/vllm-project/vllm/pull/33405)；相关 PR，需判断是否修复 [vllm-project/vllm #41270](https://github.com/vllm-project/vllm/pull/41270) | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [LMCache/LMCache #3372](https://github.com/LMCache/LMCache/issues/3372) | \[Onboarding 2026\] Good first issues — start contributing to LMCache in one PR | 51 / Serving 与评测、工程与测试 | 已完成配置范围内线程核查；认领仍需人工确认；评论认领信号: MANVIS10, maobaolong；相关 PR，需判断是否修复 [LMCache/LMCache #4110](https://github.com/LMCache/LMCache/pull/4110)；相关 PR，需判断是否修复 [LMCache/LMCache #4695](https://github.com/LMCache/LMCache/pull/4695)；相关 PR，需判断是否修复 [LMCache/LMCache #4792](https://github.com/LMCache/LMCache/pull/4792) | 先读作者意愿、认领评论与相关 PR，确认分工后补充测试、复现或评审证据。 |
| [flashinfer-ai/flashinfer #5878](https://github.com/flashinfer-ai/flashinfer/issues/5878) | bug(sampling): top_k_arr/min_p_arr are validated against input rows but indexed by output row, reading out of bounds when indices is longer than probs | 38 / KV 与存储、Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；相关 PR，需判断是否修复 [flashinfer-ai/flashinfer #6730](https://github.com/flashinfer-ai/flashinfer/pull/6730)；原帖涉及 B200, SM100；确认本机路径；人工评估超过 14 天，需更新 | 核对 #5921 及 per-row seed/offset 语义，补充 indices 乱序、重复、长度变化的边界测试。 |

## 需进一步核查

| 条目 | 标题 | 分数 / 主题 | 核查与资源 | 下一步 |
|---|---|---|---|---|
| [LMCache/LMCache #4937](https://github.com/LMCache/LMCache/issues/4937) | \[good-first-issue\] serde: convert f-string log calls in cachegen_basics.py to %-format | 63 / 待判断 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [sgl-project/sglang #45000](https://github.com/sgl-project/sglang/issues/45000) | \[Bug\] FP8 block-quantized checkpoint on SM86 (FP8 Marlin) intermittently gives wrong tokens with the overlap scheduler; exact without it | 63 / KV 与存储、Serving 与评测、Kernel 与正确性 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [sgl-project/sglang #19612](https://github.com/sgl-project/sglang/issues/19612) | \[Feature\] Unified JIT / Precompilation Cache Directory | 61 / Serving 与评测、Kernel 与正确性 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [vllm-project/vllm #49004](https://github.com/vllm-project/vllm/issues/49004) | \[Bug\]: DBRX MoE weight loading crashes with KeyError after FusedMoE/MoERunner inversion refactor (#41184) — dbrx.py missed by follow-up fix #45054 | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 线程尚未核查；正文仅保留前 6000 字符，结论需读原帖 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [vllm-project/vllm #49261](https://github.com/vllm-project/vllm/issues/49261) | \[Bug\]: Persistent KV offload cache is not namespaced by model revision | 59 / KV 与存储、Serving 与评测、Kernel 与正确性、工程与测试 | 线程尚未核查 | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |
| [ggml-org/llama.cpp #17488](https://github.com/ggml-org/llama.cpp/issues/17488) | GGUF convert support for Vibevoice | 55 / Kernel 与正确性 | 已完成配置范围内线程核查；认领仍需人工确认；相关 PR，需判断是否修复 [ggml-org/llama.cpp #30530](https://github.com/ggml-org/llama.cpp/pull/30530) | 补齐线程、关联 PR 与当前源码核查，再判断参与方式。 |

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
| sgl-project/sglang | 25 / 934（还有更多） | 10 / 46（还有更多） | 10 / 14（还有更多） | 6 / 416（还有更多） | hicache: 15 / 30（还有更多）；cache: 15 / 79（还有更多） |
| vllm-project/vllm | 25 / 2651（还有更多） | 10 / 18（还有更多） | 10 / 28（还有更多） | 6 / 489（还有更多） | cache: 15 / 322（还有更多）；streaming: 15 / 71（还有更多） |
| LMCache/LMCache | 25 / 241（还有更多） | 9 / 9 | 10 / 11（还有更多） | 6 / 7（还有更多） | L2: 15 / 25（还有更多）；prefetch: 3 / 3 |
| flashinfer-ai/flashinfer | 25 / 427（还有更多） | 5 / 5 | 0 / 0 | 6 / 25（还有更多） | — |
| ggml-org/llama.cpp | 25 / 787（还有更多） | 10 / 17（还有更多） | 10 / 27（还有更多） | 6 / 3785（还有更多） | — |
| triton-lang/triton | 25 / 912（还有更多） | 0 / 0 | 10 / 17（还有更多） | 6 / 177（还有更多） | — |
| kvcache-ai/Mooncake | 25 / 349（还有更多） | 2 / 2 | 1 / 1 | 6 / 7（还有更多） | — |
| NVIDIA/TensorRT-LLM | 25 / 669（还有更多） | 0 / 0 | 0 / 0 | 6 / 180（还有更多） | — |
| NVIDIA/cutlass | 25 / 458（还有更多） | 2 / 2 | 4 / 4 | 6 / 295（还有更多） | — |
| pytorch/pytorch | 25 / 14114（还有更多） | 10 / 41（还有更多） | 0 / 0 | 0 / 0 | — |
| ray-project/ray | 25 / 2855（还有更多） | 0 / 0 | 0 / 0 | 0 / 0 | — |
| vllm-project/aibrix | 25 / 321（还有更多） | 8 / 8 | 10 / 15（还有更多） | 0 / 0 | — |

分母是 API 该窗口的可用条目数；不同窗口可能重叠。固定条目另行刷新，Discussion 关闭或已回答的条目保留数据但不列为新机会。

## 本轮变化

上游更新 42、首次采集 201

条目离开抽样窗口不能推导已关闭；固定条目与上一轮机会清单会继续核对状态。
