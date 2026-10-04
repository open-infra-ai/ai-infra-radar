import argparse
import json
from pathlib import Path

import requests
from transformers import AutoTokenizer

args_parser = argparse.ArgumentParser()
args_parser.add_argument("parser", choices=["ernie45", "hy_v4"])
args_parser.add_argument("phase", choices=["baseline", "patched"])
args_parser.add_argument("--port", type=int, default=18795)
args = args_parser.parse_args()

model_path = (
    "/home/shane/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/"
    "c1899de289a04d12100db370d81485cdf75e47ca"
)
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
body = (
    "step one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen"
)
text = "\n<think>" + body + "</think>answer"
allowed_ids = sorted(
    set(tokenizer.encode(text, add_special_tokens=False)) | {tokenizer.eos_token_id}
)
payload = {
    "model": "parser-repro",
    "messages": [{"role": "user", "content": "Copy the specified text exactly."}],
    "temperature": 0,
    "max_tokens": 80,
    "stream": True,
    "return_token_ids": True,
    "allowed_token_ids": allowed_ids,
    "structured_outputs": {"regex": text},
    "chat_template_kwargs": {"enable_thinking": True},
}
response = requests.post(
    f"http://127.0.0.1:{args.port}/v1/chat/completions",
    json=payload,
    stream=True,
    timeout=(5, 90),
)
response.raise_for_status()
chunks = []
for line in response.iter_lines():
    if not line.startswith(b"data: "):
        continue
    data = line[6:]
    if data == b"[DONE]":
        break
    chunk = json.loads(data)
    if "error" in chunk:
        raise RuntimeError(chunk["error"])
    chunks.append(chunk)

reasoning = "".join(c["choices"][0]["delta"].get("reasoning") or "" for c in chunks)
content = "".join(c["choices"][0]["delta"].get("content") or "" for c in chunks)
token_chunks = [c["choices"][0].get("token_ids") or [] for c in chunks]
start_id = tokenizer.get_vocab()["<think>"]
end_id = tokenizer.get_vocab()["</think>"]
grouped_start = any(start_id in ids and len(ids) > 1 for ids in token_chunks)
end_emitted = any(end_id in ids for ids in token_chunks)
record = {
    "parser": args.parser,
    "phase": args.phase,
    "source_base": "bd42276e1e25f540f019381c65994120158aa2a1",
    "native_wheel_commit": "f98d1fc49361cb50457f6109c3c01a5c77e415b4",
    "model": "Qwen/Qwen3-0.6B",
    "model_revision": "c1899de289a04d12100db370d81485cdf75e47ca",
    "request": payload,
    "requested_raw_text": text,
    "reasoning": reasoning,
    "content": content,
    "chunks": chunks,
    "grouped_start": grouped_start,
    "end_token_emitted": end_emitted,
    "start_marker_leaked": "<think>" in reasoning,
}
target = Path(__file__).with_name(
    f"vllm-55195-{args.phase}-serving-{args.parser}.json"
)
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: record[k] for k in ["parser", "phase", "reasoning", "content", "grouped_start", "end_token_emitted", "start_marker_leaked"]}, ensure_ascii=False))
assert grouped_start and end_emitted
assert content == "answer"
expected_reasoning = "\n" + ("<think>" if args.phase == "baseline" else "") + body
assert reasoning == expected_reasoning
