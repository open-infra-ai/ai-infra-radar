# 方法级 CPU probe 的复现说明

此 probe 提取固定提交中的两个真实查询方法并原样编译执行，使用模拟的 Bitmap、
时钟和 NIXL agent；传输结果的数据类型直接加载上游标准库文件。它没有导入完整
LMCache 包，没有执行构造器或 submit，没有运行原生扩展、controller 或网络传输。

只需要 Python 3.12、Git 与网络。以下命令新建临时检出，不改已有技术仓。
本轮实际运行位置是 `.local/upstream/LMCache/contribution_probe/p2p_deadline.py`，
输出保存为本目录 `results.json`；下方代码与实际脚本逐字一致，SHA-256 已保存在结果中。

```bash
case_dir=$(mktemp -d /tmp/lmcache-5454.XXXXXX)
git -C "$case_dir" init
git -C "$case_dir" remote add origin https://github.com/LMCache/LMCache.git
git -C "$case_dir" fetch --depth 1 origin 1ca53a8aadca1d054f171fd67350be35797cfddc
git -C "$case_dir" checkout --detach FETCH_HEAD
mkdir -p "$case_dir/contribution_probe"
cat > "$case_dir/contribution_probe/p2p_deadline.py" <<'PY_PROBE'
# SPDX-License-Identifier: Apache-2.0
# Standard
import __future__
import ast
import hashlib
import json
import platform
from pathlib import Path
import runpy
import subprocess
import threading
from types import MethodType, SimpleNamespace
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]
P2P = ROOT / "lmcache/v1/distributed/l2_adapters/p2p_l2_adapter.py"
NIXL = ROOT / "lmcache/v1/distributed/transfer_channel/impl/nixl_impl.py"
API = ROOT / "lmcache/v1/distributed/transfer_channel/api.py"
SOURCES: list[dict[str, object]] = []


class ProbeBitmap:
    def __init__(self, size: int) -> None:
        self.bits = [False] * size

    def set(self, index: int) -> None:
        self.bits[index] = True


def load_method(path: Path, class_name: str, name: str, bindings: dict[str, object]) -> object:
    tree = ast.parse(path.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    SOURCES.append({
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "method": f"{class_name}.{name}",
        "lines": [method.lineno, method.end_lineno],
    })
    # Keep the production method body unchanged; defer its type annotations.
    module = ast.Module(body=[method], type_ignores=[])
    exec(compile(module, str(path), "exec", flags=__future__.annotations.compiler_flag), bindings)
    return bindings[name]


api = runpy.run_path(str(API))
query_read_status = load_method(NIXL, "NixlTransferChannelClient", "query_read_status", {
    "TransferChannelReadResult": api["TransferChannelReadResult"], "logger": MagicMock(),
})
clock = SimpleNamespace(monotonic=MagicMock())
query_load_result = load_method(P2P, "P2PL2Adapter", "query_load_result", {
    "Bitmap": ProbeBitmap, "time": clock, "logger": MagicMock(),
})


def make_adapter(status: str) -> tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace]:
    agent = SimpleNamespace(
        check_xfer_state=MagicMock(return_value=status), release_xfer_handle=MagicMock(),
    )
    client = SimpleNamespace(
        _ctx=SimpleNamespace(agent=agent), _lock=threading.Lock(),
        _tasks={7: ("mock-handle", [api["TransferChannelAddress"](offset=0, size=16)])},
    )
    client.query_read_status = MethodType(query_read_status, client)
    adapter = SimpleNamespace(
        _load_tasks={1: SimpleNamespace(keys=["mock-key"], read_task_id=7, deadline=10.0, failed=False)},
        _tc_client=client,
    )
    adapter.query_load_result = MethodType(query_load_result, adapter)
    return adapter, client, agent


def poll(adapter: SimpleNamespace, client: SimpleNamespace, agent: SimpleNamespace,
         now: float, status: str) -> dict[str, object]:
    clock.monotonic.return_value = now
    agent.check_xfer_state.return_value = status
    result = adapter.query_load_result(1)
    return {
        "now": now, "mock_transfer_status": status,
        "result": None if result is None else result.bits,
        "adapter_task_retained": 1 in adapter._load_tasks,
        "transfer_task_retained": 7 in client._tasks,
        "status_checks": agent.check_xfer_state.call_count,
        "handle_releases": agent.release_xfer_handle.call_count,
    }


def main() -> None:
    cases = []
    scenarios = [
        ("pending_before_deadline", 9.0, "PROC", None, True, True, 2, 0),
        ("pending_at_deadline", 10.0, "PROC", None, True, True, 2, 0),
        ("pending_after_deadline", 10.001, "PROC", [False], False, True, 0, 0),
        ("done_before_deadline", 9.0, "DONE", [True], False, False, 1, 1),
        ("done_after_deadline", 10.001, "DONE", [False], False, True, 0, 0),
        ("error_before_deadline", 9.0, "ERR", [False], False, False, 1, 1),
    ]
    for name, now, status, expected_result, adapter_retained, tc_retained, checks, releases in scenarios:
        adapter, client, agent = make_adapter(status)
        first = poll(adapter, client, agent, now, status)
        second = poll(adapter, client, agent, now, status)
        assert first["result"] == expected_result, name
        assert second["result"] is None, name
        assert second["adapter_task_retained"] == adapter_retained, name
        assert second["transfer_task_retained"] == tc_retained, name
        assert second["status_checks"] == checks, name
        assert second["handle_releases"] == releases, name
        cases.append({"name": name, "passed": True, "polls": [first, second]})

    adapter, client, agent = make_adapter("PROC")
    sequence = [poll(adapter, client, agent, now, status) for now, status in
                ((9.0, "PROC"), (10.001, "PROC"), (11.0, "DONE"))]
    assert [row["result"] for row in sequence] == [None, [False], None]
    assert [row["status_checks"] for row in sequence] == [1, 1, 1]
    assert sequence[-1]["transfer_task_retained"] is True
    assert sequence[-1]["handle_releases"] == 0
    cases.append({"name": "pending_then_timeout_then_done", "passed": True, "polls": sequence})

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    print(json.dumps({
        "scope": "CPU method-level control-flow probe; unchanged production method bodies, mocked dependencies",
        "upstream_commit": commit, "python": platform.python_version(), "platform": platform.platform(),
        "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": SOURCES,
        "transfer_api_sha256": hashlib.sha256(API.read_bytes()).hexdigest(),
        "limits": ["No package import or constructor/submit path", "No native Bitmap", "No real NIXL or GPU transfer",
                   "No PrefetchController/L1 manager execution", "Not the upstream pytest suite"],
        "cases": cases, "passed": len(cases),
    }, indent=2))


if __name__ == "__main__":
    main()
PY_PROBE
python3 "$case_dir/contribution_probe/p2p_deadline.py" > "$case_dir/results.json"
cat "$case_dir/results.json"
```

`passed: 7` 表示七个场景都符合对当前控制流的预期，没有证明契约安全。
检查每个场景的 `polls`：`status_checks` 和 `handle_releases` 是累计调用次数，
`transfer_task_retained` 只观察模拟客户端字典；不要把它写成真实 NIXL handle 泄漏测量。
默认同一 key 在第二次查询已完成任务时返回 `None`，pending 场景继续查询。

后续正式回归测试需要正常导入完整包，使用真实 Bitmap 并通过公开提交路径构造任务；
controller 的资源所有权还需要独立测试。此脚本是调查夹具，未作为上游测试提交。
