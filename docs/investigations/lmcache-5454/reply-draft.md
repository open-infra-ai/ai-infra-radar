# LMCache #5454 回复草稿

状态：私人草稿，尚未发布。拟发布位置：
[LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454)。
发布前刷新线程与 #5255，避免重复回答已经确定的方向。

以下英文正文用于上游协作；七场景结果和完整 probe 在私有调查记录中，
公开评论不能链接只有本人可访问的证据，也不能暗示已运行正式 pytest 或 NIXL。
按用户要求，先展示完整正文；用户确认这版措辞后再发布。

---

I checked the query methods at [`1ca53a8`](https://github.com/LMCache/LMCache/blob/1ca53a8aadca1d054f171fd67350be35797cfddc/lmcache/v1/distributed/l2_adapters/p2p_l2_adapter.py#L326-L347) using the original code with mocked dependencies. I haven't run a real NIXL transfer.

If the first poll is past the deadline, the adapter returns an all-zero bitmap even when the mocked transfer is already `DONE`. It skips the status check and drops the task, so later polls never reach the transfer client's handle cleanup.

Could #5255 handle the caller's timeout while the adapter keeps polling until the transfer finishes? I can help test late completion if that's useful.
