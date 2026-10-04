## Overview

Strip the initial reasoning marker from grouped streaming deltas in the independent Ernie45 and HYV4 parsers. Related to [#55195](https://github.com/vllm-project/vllm/issues/55195); complements [#55210](https://github.com/vllm-project/vllm/pull/55210) and [#56262](https://github.com/vllm-project/vllm/pull/56262), whose reviewed diffs change the base and Olmo3 parsers.

## Claims

- Remove the structural start marker without dropping the first reasoning text when it shares a delta with other tokens.
- Preserve text already decoded without the marker, initial quoted markers, and quoted markers after implicit reasoning; preserve Ernie quotes after an explicit start or in content.
- Keep the change within two independent parser implementations; no base parser or Olmo3 changes.

## Validation

Python source base: `bd42276e1e25f540f019381c65994120158aa2a1`. Serving uses the official cu130 native wheel from `f98d1fc49361cb50457f6109c3c01a5c77e415b4`, not a native build of that source base.

```bash
HF_HUB_OFFLINE=1 VLLM_TARGET_DEVICE=empty .venv/bin/python -m pytest \
  tests/reasoning/test_ernie45_reasoning_parser.py \
  tests/reasoning/test_hy_v4_reasoning_parser.py -q
```

| Check | Baseline | Patched |
|---|---|---|
| Same 23 parser tests | 5 failed, 18 passed | 23 passed |
| GPU HTTP/SSE, `ernie45` | Start marker leaked | Marker removed, body and content preserved |
| GPU HTTP/SSE, `hy_v4` | Start marker leaked | Marker removed, body and content preserved |

The tests use the real ERNIE-4.5-21B-A3B-Thinking and Hy4-preview tokenizers, with revisions `4341bb42644d5422859509fa25d41544c57181f8` and `705d81ee51566a186d645b74c974d642ef2828fe`. They add eight Ernie parameter cases and seven HYV4 cases, keeping the existing eight Ernie cases. Both runs use the normal root conftest and report 14 torch.jit deprecation warnings. Some cases deliberately mark the start token as special to exercise decoding with the marker hidden.

Serving validation runs Qwen3-0.6B revision `c1899de289a04d12100db370d81485cdf75e47ca` on an RTX 3060 Laptop GPU (6 GiB), explicitly selecting each parser. Xgrammar constraints and stream interval 8 produce a delta containing the start token and reasoning text; saved SSE token IDs confirm that boundary. This validates real GPU generation and parser integration, not native ERNIE/HY4 model quality or speculative decoding. Those model evaluations remain outstanding.

The full pre-commit run on all four changed files exits 0, including applicable ruff, formatting, default mypy and test-tethering hooks. Before submission, the human submitter must review every changed line and run the relevant tests. The patch, probe and logs are currently private; there is no public artifact link yet.

## Details

The two implementations can return raw `delta_text` when a start token arrives with reasoning text. Both now remove the first marker only when previous text is blank and the delta starts with that marker after leading whitespace. Ernie also requires the start token ID in the delta and no previous start/end ID. HYV4 applies the change only in its start-without-end branch. These guards preserve quoted markers, including after reasoning that began without an explicit start. Text with the start marker already hidden by decoding is left unchanged.

This deliberately avoids a parser refactor and leaves Ernie's response-end handling and HYV4's remaining state branches unchanged. It does not claim to resolve all of #55195. Existing PR scope and author coordination must be refreshed before publishing.

AI assistance was used to prepare the patch, tests, validation scripts and this draft. Human review and test execution are pending.

---

<details>
<summary> Pull Request Checklist </summary>

- [x] I used vLLM's `/pr-checklist` skill. (Mandatory for agents, optional for humans).
- [x] AI assistance was used during the creation of this PR.

- [x] **Design Fit:** Minimizes impact on core components, reuses existing functionality, and justifies added complexity.
- [ ] **Testing and Validation:** Validates the change and ensures any added tests are meaningful and reliable, with CI coverage or documented CI resource constraints and validation performed outside CI.
- [ ] **Code Quality and Style:** Keeps code and comments clear and concise, and updates relevant documentation and examples.
- [ ] **Pull Request Contents:** Includes a brief summary and relevant links, supports claims with evidence, explains root causes and implementation trade-offs, and follows the contributing guide.
</details>

**BEFORE SUBMITTING, PLEASE READ <https://docs.vllm.ai/en/latest/contributing>** (anything written below this line will be removed by GitHub Actions)
