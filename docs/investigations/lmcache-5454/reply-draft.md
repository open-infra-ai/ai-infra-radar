# LMCache #5454 回复草稿

状态：私人草稿，尚未发布。拟发布位置：
[LMCache/LMCache #5454](https://github.com/LMCache/LMCache/issues/5454)。
发布前刷新线程与 #5255，避免重复回答已经确定的方向。

以下英文正文用于上游协作；七场景结果和完整 probe 在私有调查记录中，
公开评论不能链接只有本人可访问的证据，也不能暗示已运行正式 pytest 或 NIXL。

---

I traced this on `dev` at `1ca53a8aadca1d054f171fd67350be35797cfddc` and checked
the control flow using a deterministic CPU probe that executes the unchanged
`query_load_result` and `query_read_status` method bodies with mocked dependencies.
This was a method-level check, not the upstream pytest suite or a real NIXL transfer.

One additional boundary case may be useful for the eventual regression tests:
if the first poll happens after the deadline, even a mocked `DONE` transfer is
reported as an all-zero result without querying its status. The adapter drops its
task, while the transfer client's task remains and its normal handle-release path
is not reached. Before the deadline, the same `DONE` case is queried and the handle
is released once. A `PROC -> timeout -> DONE` sequence also stops polling after
the timeout. None of this demonstrates actual KV corruption.

This suggests two separate checks: a late result should still be collected, and
buffers/locks must not be reusable while a transfer can still access them.
Polling once before the deadline check would address the already-terminal case,
but would not by itself settle ownership for an in-flight read.

Since you have offered to work on the fix, would additional late-completion tests
be useful once the intended contract is agreed? Should a non-`None` adapter result
guarantee that the transfer no longer accesses its buffers, with the caller's
deadline handled separately along the lines of #5255?
