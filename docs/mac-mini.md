# Mac mini — M6 / M5 Pro — full configuration coverage

*Specs verified against [Apple UK tech-specs](https://www.apple.com/uk/mac-mini/specs/).*
*All fit levels from llmfit v1.1.12 with `--memory/--ram/--cpu-cores` simulation.*

**Note: 2026 Mac mini ships M6 (not M5), plus M5 Pro option.** No M5 Max/Ultra.

## Every config (Apple UK, verified)

| Model | Chip | CPU | GPU | RAM (config) | Bandwidth | Storage |
|---|---|---|---|---|---|---|
| 1 | M6 | 12c (2S+4P+6E) | 12c | 16GB (cfg 24/32) | 153GB/s | 256GB |
| 2 | M6 | 12c | 12c | 16GB (cfg 24/32) | 153GB/s | 512GB |
| 3 | M6 | 12c | 12c | 24GB (cfg 32) | 170GB/s | 512GB |
| 4 | M5 Pro | 15c (5S+10P) → cfg 18c | 16c → cfg 20c | 24GB (cfg 48/64) | 307GB/s | 512GB |

Models 1 and 2 differ only in storage. Model 4 has an 18c/20c die upgrade option.

## What each config can and can't run

### M6 16GB (153GB/s)
- **CAN:** gpt-oss-120b (Perfect), qwen3-235b MoE* (Perfect), deepseek-v3* (Perfect),
  deepseek-r1-0528 distill (Perfect), glm-4.5 (Perfect), minimax-m2 (Perfect),
  llama-3.3-70b (Perfect*), ~14-16B dense (Phi-3-medium 14B Q8, gemma-4 31B MXFP4)
- **CAN'T:** llama-3.1-70b (Too Tight), qwen3-32b (Marginal Q2_K), mistral-large,
  llama-3.1-405b, qwen3-coder-480b, llama-4-maverick (all Too Tight)
- **Verdict:** useless for serious local LLM work. Best you get is ~14B dense.

### M6 24GB (170GB/s)
- **CAN:** everything above + llama-3.1-70b (Marginal Q3_K_M), qwen3-32b (Marginal
  Q4_K_M), ~22B dense (ERNIE-4.5-21B Q8, Qwen3.5-27B Q8 edge)
- **CAN'T:** mistral-large, llama-3.1-405b, qwen3-coder-480b, llama-4-maverick
- **Verdict:** entry-level. OK for 20B-class and MoE partial. Skip for anything bigger.

### M6 32GB (170GB/s)
- **CAN:** qwen3-32b (Perfect Q6_K), gemma-2-27b (Perfect Q8), ~28-30B dense,
  everything smaller at high quants
- **CAN'T:** mistral-large, llama-3.1-405b, qwen3-coder-480b, llama-4-maverick
- **Verdict:** sweet spot for "small but real" local LLMs. Cheapest sensible floor.

### M5 Pro 24GB (307GB/s)
- **CAN:** same as M6 24GB (die bump, same RAM)
- **CAN'T:** same as M6 24GB
- **Verdict:** pointless for LLM. Paying for CPU/GPU you don't need.

### M5 Pro 48GB (307GB/s)
- **CAN:** llama-3.1-70b (Good AWQ), llama-3.3-70b (Perfect), qwen3-32b (Perfect Q8),
  ~40-42B dense (Qwen2.5-72B NVFP4, Llama-3.3-70B NVFP4), mistral-large (Marginal Q2_K)
- **CAN'T:** llama-3.1-405b, qwen3-coder-480b, llama-4-maverick, mistral-large (good quants)
- **Verdict:** only mini tier that fits 70B at Q8-equivalent (via NVFP4). Mistral-large
  goes Marginal at Q2_K (low quality).

### M5 Pro 64GB (307GB/s)
- **CAN:** ~57-68B dense (Llama-65B Q6_K, Jamba-Mini 51B Q8), mistral-large (Marginal
  Q3_K_M), everything smaller at high quants
- **CAN'T:** llama-3.1-405b, qwen3-coder-480b, llama-4-maverick, mistral-large (good quants)
- **Verdict:** best-of-the-minis but caps out at ~70B. Does not reach frontier.

* MoE partial offload: only active experts resident; listed memory is per-token
  working set, not full weights.

## Bandwidth scaling vs detector box

llmfit detected this box's GPU at 256GB/s. Scale raw t/s:

| Config | Bandwidth | Scale factor |
|---|---|---|
| M6 16GB | 153GB/s | ×0.6 |
| M6 24/32GB | 170GB/s | ×0.66 |
| M5 Pro (all) | 307GB/s | ×1.2 |

Fit levels (Perfect/Good/Marginal/Too Tight) are memory-driven and don't need scaling.

## Verdict vs Mac Studio M5

- If goal is frontier local (405B dense, full R1, GLM-5): **mini can't do it. Studio M5 Ultra 512GB required.**
- If goal is mid-size daily driver (30-70B dense, Qwen3-235B MoE, GLM-4.5): **M5 Pro 64GB mini** is enough and far cheaper.
- If goal is casual coding assistant (7-30B): **M6 32GB** is the cheapest sensible floor.
- **Skip:** M6 16GB (too small), M5 Pro 24GB (paying for die you don't need).

## Reproduce

```sh
llmfit --memory 16G --ram 16G --cpu-cores 12 fit --json > raw/m6_16.json
llmfit --memory 24G --ram 24G --cpu-cores 12 fit --json > raw/m6_24.json
llmfit --memory 32G --ram 32G --cpu-cores 12 fit --json > raw/m6_32.json
llmfit --memory 24G --ram 24G --cpu-cores 15 fit --json > raw/m5pro_24.json
llmfit --memory 48G --ram 48G --cpu-cores 15 fit --json > raw/m5pro_48.json
llmfit --memory 64G --ram 64G --cpu-cores 18 fit --json > raw/m5pro_64.json
```

Full per-model detail in `raw/mini_flagship.json`.
