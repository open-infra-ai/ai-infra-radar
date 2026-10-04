# 复现 Ernie45 / HYV4 分组流式标记问题

本指南面向能运行 vLLM 的开发者，复现同一组测试的旧源码/补丁差异，以及真实
GPU HTTP/SSE 中起始标记泄漏。版本与结论边界见 [README](README.md)。

## 1. 准备源码与依赖

在专用 vLLM 检出目录操作。旧源码和补丁测试应使用相同测试文件；不要在有其它
工作改动的目录直接回退文件。以下使用两份独立 worktree：

```bash
BASE=bd42276e1e25f540f019381c65994120158aa2a1
EVIDENCE=/home/shane/github/open-infra-ai/ai-infra-radar/docs/investigations/vllm-55195
git worktree add --detach ../vllm-55195-baseline "$BASE"
git worktree add --detach ../vllm-55195-patched "$BASE"
git -C ../vllm-55195-baseline apply "$EVIDENCE/parser.patch"
git -C ../vllm-55195-baseline restore --source="$BASE" -- \
  vllm/reasoning/ernie45_reasoning_parser.py \
  vllm/reasoning/hy_v4_reasoning_parser.py
git -C ../vllm-55195-patched apply "$EVIDENCE/parser.patch"
```

分别进入两份 worktree，建立虚拟环境并安装依赖。本次可成功安装的组合是 Python
base 源码加下面固定的官方 native wheel，不是从 base 自行编译：

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python \
  -r requirements/build/cuda.txt --torch-backend=cu130
VLLM_USE_PRECOMPILED=1 \
VLLM_PRECOMPILED_WHEEL_COMMIT=f98d1fc49361cb50457f6109c3c01a5c77e415b4 \
uv pip install --python .venv/bin/python -e . \
  --no-build-isolation --torch-backend=cu130
uv pip install --python .venv/bin/python -r requirements/test/cuda.in
```

现有满足依赖的虚拟环境可直接复用。首次需要下载测试 tokenizer。为复核本轮
结果，核对缓存 snapshot revision 与
[tokenizers.json](tokenizers.json) 一致；测试文件本身使用 model ID，不锁定远端
revision，因此未来重新下载可能得到不同版本。

## 2. 同一组正式 pytest

在两份 worktree 各运行一次：

```bash
HF_HUB_OFFLINE=1 VLLM_TARGET_DEVICE=empty .venv/bin/python -m pytest \
  tests/reasoning/test_ernie45_reasoning_parser.py \
  tests/reasoning/test_hy_v4_reasoning_parser.py \
  -q --junitxml=55195.junit.xml
```

两次应各收集 23 项。旧源码实测为 `5 failed, 18 passed`，补丁为 `23 passed`，
各有 14 条 torch.jit 弃用警告。上述离线命令要求 tokenizer 已缓存；首次先联网
下载固定 tokenizer revision。原始结果见 [baseline-pytest.log](baseline-pytest.log)
与 [patched-pytest.log](patched-pytest.log)。
覆盖分组起始标记、被隐藏的起始文本、起始/结束同 delta，以及 Ernie 后续字面
标记，以及省略起始标记的隐式 reasoning 后引用不应被清理。

## 3. 启动真实 GPU 服务

本轮硬件为 RTX 3060 Laptop GPU（6 GiB）。下载固定的小模型到本地缓存：

```bash
.venv/bin/python -c 'from huggingface_hub import snapshot_download; print(snapshot_download("Qwen/Qwen3-0.6B", revision="c1899de289a04d12100db370d81485cdf75e47ca"))'
```

probe 保存了本机 snapshot 绝对路径；在其它机器运行时，复制 probe 到工作目录，
将 `model_path` 改为上述下载结果。保留原始归档 probe，避免覆盖证据。下列服务
命令的模型路径也应同步调整。

分别在旧源码/补丁 worktree 中启动服务；每次只运行一份，结束前台进程后再切换。
对 `ernie45` 和 `hy_v4` 各执行一次：

```bash
MODEL_PATH=/home/shane/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca
PARSER=ernie45
.venv/bin/vllm serve "$MODEL_PATH" --served-model-name parser-repro \
  --host 127.0.0.1 --port 18795 \
  --reasoning-parser "$PARSER" --stream-interval 8 \
  --dtype float16 --max-model-len 256 --max-num-seqs 1 \
  --gpu-memory-utilization 0.5 --enforce-eager \
  --attention-backend TRITON_ATTN \
  --structured-outputs-config '{"backend":"xgrammar","enable_in_reasoning":true}'
```

## 4. 执行保存的 SSE probe

在第二终端，使用服务 worktree 的虚拟环境执行复制出来的脚本。`baseline` /
`patched` 参数是断言预期与结果标签；它不会自动切换生产源码。

```bash
cp "$EVIDENCE/serving-probe.py" ./vllm-55195-serving-probe.py
.venv/bin/python ./vllm-55195-serving-probe.py ernie45 baseline --port 18795
```

补丁服务改为 `ernie45 patched`；HYV4 服务对应 `hy_v4 baseline` 和 `hy_v4 patched`。
脚本将 JSON 保存到脚本旁的 `vllm-55195-{phase}-serving-{parser}.json`，包含请求、
全部 chunks、token IDs、合并的 reasoning/content 和断言观察。

请求通过 regex 与允许 token ID 集合约束生成指定文本。成功复现要求返回 token
IDs 证明起始 token 与正文处于同一 chunk，并实际生成结束 token；仅出现标记文本
而没有这些覆盖条件不算本轮等价复现。

旧源码断言期望 reasoning 中含一个结构 `<think>`，补丁断言期望去掉该标记且保留
完整正文，二者均要求 `content == "answer"`。这是 parser 路径的受约束 GPU 测试，
不能用于宣称原生 ERNIE/HY4 checkpoint 已完成模型评测。
