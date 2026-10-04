# LMCache #5454 回复草稿

状态：私人草稿，尚未发布。拟发布位置：
[LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454)。
发布前刷新线程与 #5255，避免重复回答已经确定的方向。

以下英文正文用于上游协作；七场景结果和完整 probe 在私有调查记录中，
公开评论不能链接只有本人可访问的证据，也不能暗示已运行正式 pytest 或 NIXL。
按用户要求，先展示完整正文；用户确认这版措辞后再发布。

---

I checked another timeout case at [`1ca53a8`](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/l2_adapters/p2p_l2_adapter.py#L326-L347) using the original query methods with mocked dependencies. I haven't run a real NIXL transfer.

Even when the transfer is already marked `DONE`, polling after the deadline returns a zero bitmap without calling `query_read_status`. The adapter removes its task, so later adapter polls return `None`. The client's `close()` still has a separate cleanup path.

This seems worth covering in the timeout tests, including cleanup of an already-completed transfer. I can help add that case if it's useful.
