# vLLM #55195：Ernie45 与 HYV4 独立解析器补充验证

调查日期：2026-10-05（北京时间）。当前为本地补丁与公开草稿，尚未发布评论或 PR。

本轮针对 [#55195](https://github.com/vllm-project/vllm/issues/55195) 中两个独立实现：
`Ernie45ReasoningParser` 与 `HYV4ReasoningExtractor`。当起始标记和正文处于同一个
流式 delta 时，两者会把起始标记交给客户端。补丁只调整这两个解析器，补充正式
回归测试，并用真实 tokenizer 与 GPU HTTP/SSE 服务验证。

## 结果与证据

| 验证 | 旧源码 | 补丁后 | 能支持的结论 |
|---|---|---|---|
| 同一组 23 项正式 pytest | 5 failed，18 passed | 23 passed | 原生 tokenizer 的分组边界与字面标记保留 |
| GPU SSE，显式 `ernie45` | 起始标记泄漏 | 标记移除，正文完整 | 该受约束请求通过真实服务与 parser 路径 |
| GPU SSE，显式 `hy_v4` | 起始标记泄漏 | 标记移除，正文完整 | 该受约束请求通过真实服务与 parser 路径 |

两个旧源码 SSE 记录都包含 `grouped_start=true`、`end_token_emitted=true`、
`start_marker_leaked=true`；补丁后的两组记录中前两项保持为真，第三项为假。
最终 `content` 为 `answer`，合并的 reasoning 保留全部指定正文与前导换行。
这不是仅根据请求意图判断覆盖：保存的每个 SSE chunk 同时记录返回 token IDs。

正式测试复用现有 Ernie 文件，新增 8 个参数 case；HYV4 没有相邻专用测试文件，
新增 7 个参数 case。总计 23 项包含 Ernie 原有 8 项。两次运行使用正常的仓库根
conftest 与同一组测试，各有 14 条 `torch.jit.script_method` 弃用警告。
测试使用真实 tokenizer；为验证
`skip_special_tokens` 路径，部分 case 将起始 token 标记为 special，这属于测试设置，
不表示原生 tokenizer 默认会隐藏该标记。

## 补丁选择

- 两者都要求此前文本仅为空白，且当前文本去掉前导空白后以结构起始标记开头，
  才使用 `split(start_token, 1)[-1]` 清理。Ernie 还要求当前 delta 含起始 ID，
  此前没有起始或结束 ID。HYV4 的清理限定在“当前有起始 ID、没有结束 ID”分支。
- 初始 `quote <think> here`、省略起始标记的隐式 reasoning 后引用、显式起始后的
  引用，以及 Ernie content 内的引用都有回归覆盖，避免将正文中的标记当作边界。
- 若 tokenizer 已从解码文本中隐藏起始标记，文本条件不成立，保留解码正文。
  HYV4 现有“起始与结束同 delta”的分支未扩展。

没有修改通用 base parser、Olmo3、tokenizer、调度器或 GPU kernel，也不把本轮
补丁表述为关闭整个 #55195。

## 固定版本与验证边界

| 项目 | 本轮配置 |
|---|---|
| vLLM Python 源码 base | `bd42276e1e25f540f019381c65994120158aa2a1` |
| 本地补丁分支 | `fix/55195-independent-reasoning-parsers` |
| 本地补丁 commit | `4ed36e2e4dc86cc5bb4d43f54d0cc8efd07a1ce1`，仅本地提交 |
| 官方预编译 native wheel commit | `f98d1fc49361cb50457f6109c3c01a5c77e415b4`，cu130 |
| GPU | NVIDIA GeForce RTX 3060 Laptop GPU，6 GiB |
| Python / PyTorch | 3.12.3 / 2.13.0+cu130 |
| transformers / tokenizers | 5.18.0 / 0.23.2 |
| pytest / pre-commit / ruff | 9.1.1 / 4.6.2 / 0.14.0 |
| xgrammar / GPU driver | 0.2.8 / 610.88 |
| GPU 服务 checkpoint | `Qwen/Qwen3-0.6B`，`c1899de289a04d12100db370d81485cdf75e47ca` |
| Ernie 测试 tokenizer | `baidu/ERNIE-4.5-21B-A3B-Thinking`，`4341bb42644d5422859509fa25d41544c57181f8` |
| HYV4 测试 tokenizer | `tencent/Hy4-preview`，`705d81ee51566a186d645b74c974d642ef2828fe` |

HY4 原生结构标记为 `<think:opensource>` / `</think:opensource>`，ID 分别为
120029 / 120030；正式测试通过
parser 暴露的标记访问它们。GPU 服务中的 Qwen tokenizer 使用 `<think>` / `</think>`，
显式选择两种 parser，验证的是它们的流式集成路径。

GPU 请求通过 xgrammar 的 `enable_in_reasoning`、正则与 `allowed_token_ids`
约束生成，在 `--stream-interval 8` 下稳定形成含起始 token 和正文的 delta。
这是实际 GPU 生成与 HTTP/SSE 测试，但不是原生 ERNIE/HY4 大模型的生成质量评测，
也不是 speculative decoding、吞吐或全部 marker 组合的覆盖。
Python 源码与 native wheel 来自不同 commit，不能称为从该 base 完整编译的 vLLM。

完整 pre-commit 对四个改动文件运行完成，退出码为 0，包含适用的 ruff、format、
默认 mypy 与 test-tethering 检查。发布 PR 前仍须由人类逐行审阅、理解补丁并运行相关测试；
本轮代理执行不能替代这些提交者要求。

## 与已有工作的关系

本轮最终刷新时仍开放的 [#55210](https://github.com/vllm-project/vllm/pull/55210) 与
[#56262](https://github.com/vllm-project/vllm/pull/56262) 修改通用 base 与 Olmo3，
未覆盖这两个独立 parser。补丁作为补充，发布前仍应刷新 PR diff 与状态，确认分工。
原帖已有独立实现分析，公开草稿只补充新增验证结果与协作请求。

[#48386](https://github.com/vllm-project/vllm/pull/48386) 的 Ernie response-end index
修复不在本轮范围；[#39044](https://github.com/vllm-project/vllm/pull/39044) 的
end token/text 同步问题也不同。[#58412](https://github.com/vllm-project/vllm/pull/58412)
针对 HunyuanA13B，不等同于 HYV4。

## 文件索引

- [results.json](results.json)：环境、版本、命令、结果与证据校验信息。
- [environment.json](environment.json)：详细运行环境。
- [parser.patch](parser.patch)：两个生产文件与正式测试的完整补丁。
- [复现说明](reproduce.md)、[serving-probe.py](serving-probe.py)：执行方法与保存的 SSE probe。
- 正式 pytest：[旧源码日志](baseline-pytest.log)、[补丁日志](patched-pytest.log)、
  [旧源码 JUnit](baseline.junit.xml)、[补丁 JUnit](patched.junit.xml)。
- Ernie SSE：[旧源码](baseline-serving-ernie45.json)、[补丁](patched-serving-ernie45.json)。
- HYV4 SSE：[旧源码](baseline-serving-hy_v4.json)、[补丁](patched-serving-hy_v4.json)。
- [tokenizer 元数据](tokenizers.json)、[旧源码原生 tokenizer 复现](baseline-real-tokenizers.json)、
  [pre-commit 日志](pre-commit.log)。
- 服务启动日志：[旧源码 Ernie](baseline-ernie45-server.log)、
  [补丁 Ernie](patched-ernie45-server.log)、[旧源码 HYV4](baseline-hy_v4-server.log)、
  [补丁 HYV4](patched-hy_v4-server.log)；[决策记录](decision-note.md)。
- [英文评论草稿](reply-draft.md)、[英文 PR 草稿](pr-draft.md)：供人类审阅，未经发布。
- [独立审查](review.md)、[本地提交检查](source-commit.log)。

四组服务结果均已完成；补丁后的两组服务使用最终源码重新启动后验证。
