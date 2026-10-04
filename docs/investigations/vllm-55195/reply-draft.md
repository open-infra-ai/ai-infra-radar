I have a small local patch for the independent Ernie45 and HYV4 paths, complementing #55210 and #56262. With the ERNIE-4.5 and Hy4-preview tokenizers, the same 23 parser tests give 5 failures before the patch and all pass afterward, including checks that preserve quoted markers.

GPU-backed HTTP/SSE with Qwen3-0.6B, each parser explicitly selected, and constrained generation at stream interval 8 reproduces the leak in both parsers. Both preserve the full body and remove the initial marker after the patch. This checks parser integration, not native ERNIE/HY4 model quality.

Would either PR author prefer to include these changes, or keep them in a separate complementary PR?
