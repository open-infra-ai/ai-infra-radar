# LMCache #5454 回复记录

状态：已由用户确认并发布，等待反馈。
公开链接：[评论](https://github.com/LMCache/LMCache/issues/5454#issuecomment-5976046346)。
发布账号：`holtwood`；时间（UTC）：`2026-10-04T03:09:26Z`。

以下为已发布正文。完整方法级 CPU mock 结果保存在私有调查记录中；
本轮未运行真实 NIXL 传输或完整上游 pytest。

---

I checked another timeout case at [`1ca53a8`](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/l2_adapters/p2p_l2_adapter.py#L326-L347) using the original query methods with mocked dependencies. I haven't run a real NIXL transfer.

Even when the transfer is already marked `DONE`, polling after the deadline returns a zero bitmap without calling `query_read_status`. The adapter removes its task, so later adapter polls return `None`. The client's `close()` still has a separate cleanup path.

This seems worth covering in the timeout tests, including cleanup of an already-completed transfer. I can help add that case if it's useful.
