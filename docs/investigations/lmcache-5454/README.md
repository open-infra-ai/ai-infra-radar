# LMCache #5454：P2P 超时与传输资源生命周期

调查日期：2026-10-04（北京时间）。本地进度：`drafted`，尚未公开反馈。

适合参与的方式是补充边界验证、协助确定契约，再与作者确认测试分工。
[原帖](https://github.com/LMCache/LMCache/issues/5454) 作者 `0andy` 已表达愿意修复；
零评论和没有 assignee 不能推出无人工作。

## 本轮新增证据

固定 LMCache `dev` 的 `1ca53a8aadca1d054f171fd67350be35797cfddc`，将生产源码中
两个查询方法的 AST 原样编译执行，模拟时钟、Bitmap、NIXL agent 和任务初始状态。
七个场景均符合当前控制流的预期；这表示观察已复核，不表示行为满足安全契约。

| 首次查询条件 | 返回结果 | 传输状态查询次数 | 任务与 handle 的观察 |
|---|---|---|---|
| 截止前，模拟 `PROC` | `None` | 1 | adapter 和传输任务保留 |
| 恰好截止时，模拟 `PROC` | `None` | 1 | 使用严格 `>`，仍继续轮询 |
| 截止后，模拟 `PROC` | `[false]` | 0 | adapter 删除任务，传输任务保留 |
| 截止前，模拟 `DONE` | `[true]` | 1 | 传输任务删除，handle 释放一次 |
| 截止后，模拟 `DONE` | `[false]` | 0 | 已模拟为完成，仍不查询状态或释放 handle |
| 截止前，模拟 `ERR` | `[false]` | 1 | 传输任务删除，handle 释放一次 |
| `PROC` → 超时 → 模拟 `DONE` | `None` → `[false]` → `None` | 累计始终为 1 | 后续 adapter 轮询不能收割该传输 |

可补充到原帖的边界是：**截止时间之后才第一次轮询时，即使传输已经完成，仍走
未查询状态的失败路径**。它同时影响结果和正常 handle 清理路径；仅把状态查询
移到 deadline 判断前，仍不能解决 `PROC` 在途情况下的 buffer 所有权问题。

原始输出见 [results.json](results.json)，包含版本、源码与 probe 的 SHA-256、
逐次查询和断言结果。完整执行方法见 [复现说明](reproduce.md)。实验脚本位于本地
上游分支 `investigate/5454-deadline-control-flow`，没有修改生产实现或推送上游。

## 源码链路与证据等级

1. **方法级 CPU 验证**：[adapter 查询](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/l2_adapters/p2p_l2_adapter.py#L326-L347)
   的超时分支直接删除任务并返回零 Bitmap；
   [NIXL client 查询](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/transfer_channel/impl/nixl_impl.py#L158-L191)
   在轮询到 terminal 状态后才执行正常的任务删除与 handle 释放。
2. **源码分析**：[controller](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/storage_controllers/prefetch_controller.py#L1394-L1425)
   对非 `None` 结果处理失败 key 的 `finish_write_and_delete`，随后 `submit_unlock`；
   [P2P unlock](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/l2_adapters/p2p_l2_adapter.py#L277-L282)
   会向远端发送 unlock。此链路本轮没有执行 controller / L1 manager 测试。
3. **待验证假设**：真实在途传输会否在资源复用后访问原 buffer，以及影响到实际 KV
   数据的条件。本轮没有运行 NIXL、双实例传输、GPU 测试或观察到真实数据损坏。

probe 没有导入完整 LMCache 包，没有运行构造器、提交路径、原生 Bitmap 或上游
pytest。任务字典由测试夹具预置，agent 返回值是模拟状态。实际 `close()` 会尝试
释放剩余 handle，但“调用释放”不能直接表述为“取消已成功、内存可安全复用”。

## 已有工作的当前状态

以下是 2026-10-04 本轮读取 GitHub API 的状态，发布反馈前需要再刷新。

- [#5454](https://github.com/LMCache/LMCache/issues/5454)：开放；作者有条件性的修复意愿；
  当时没有评论、assignee 或已检出的开放关闭关联 PR。
- [#5255](https://github.com/LMCache/LMCache/pull/5255)：开放、尚未合入；读取时 head 为
  `8831de680565e1ca687a1647ed62e222b30416e9`。作者提出 controller 的调用方 deadline
  与 I/O 资源生命周期分离，需确认 P2P 是否应沿用该模型；本轮未验证该 PR 的测试声明。
- [#5263](https://github.com/LMCache/LMCache/issues/5263)：相关 shutdown / TTL 所有权讨论。
- [NIXL #2209](https://github.com/ai-dynamo/nixl/pull/2209)、
  [#2044](https://github.com/ai-dynamo/nixl/pull/2044)：读取时均已关闭且未合入，
  不能依赖其提供可用的 per-task cancellation。

## 下一步与退出条件

先审阅 [回复草稿](reply-draft.md)，明确授权后才向上游发布。询问作者和维护者：
adapter 的非 `None` 结果是否承诺传输已停止访问 buffer，是否倾向采用 #5255 的
controller deadline 模型，以及是否需要协助补充 late-completion 回归测试。

获得分工和契约答复后，才在上游分支实现补丁与正式公开接口测试。应验证
pending → terminal、晚到成功 / 错误、超时后锁和 staging buffer 保留、每个 handle
只释放一次，以及真实取消失败的回退行为。资源不足时请求协作验证，保持证据边界。

跟进日期设为 2026-10-06；该日期仅是个人审阅提醒，不自动发消息。尚未发布时
不记为 `submitted`，作者已有修复时转向验证与补测试。
