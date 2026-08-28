# Mac mini — M6 / M5 Pro — Local LLM guide

*Specs verified against [Apple UK tech-specs](https://www.apple.com/uk/mac-mini/specs/).*

**Note: 2026 Mac mini ships M6 (not M5), plus M5 Pro option.** No M5 Max/Ultra.

## Published configurations

| Model | Chip | CPU | GPU | RAM (config) | Bandwidth |
|---|---|---|---|---|---|
| 1 | M6 | 12c (2S+4P+6E) | 12c | 16GB (cfg 24/32) | 153GB/s |
| 2 | M6 | 12c | 12c | 16GB (cfg 24/32) | 153GB/s |
| 3 | M6 | 12c | 12c | 24GB (cfg 32) | 170GB/s |
| 4 | M5 Pro | 15c (5S+10P) → cfg 18c | 16c → cfg 20c | 24GB (cfg 48/64) | 307GB/s |

Media engine same on all: H.264/HEVC/ProRes/ProRes RAW hw-accel, AV1 decode.

## llmfit sims (memory/CPU override)

Simulated 16/24/32GB M6 (12 cores) and 24/48/64GB M5 Pro (15–18 cores).

### Fit table — flagship models

| Model | 16GB M6 | 24GB M6 | 32GB M6 | 24GB Pro | 48GB Pro | 64GB Pro |
|---|---|---|---|---|---|---|
| llama-3.1-70b | Too Tight | Marginal (Q3_K_M) | Marginal (Q2_K) | Marginal (Q3_K_M) | Good (AWQ) | Good (AWQ) |
| llama-3.3-70b | Perfect* | Perfect* | Perfect* | Perfect* | Perfect | Perfect |
| qwen3-32b | Marginal (Q2_K) | Marginal (Q4_K_M) | **Perfect (Q6_K)** | Marginal (Q4_K_M) | **Perfect (Q8)** | **Perfect (Q8)** |
| qwen3-235b (MoE) | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* |
| deepseek-r1-0528 distill | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |
| deepseek-v3 | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* |
| gpt-oss-120b | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |
| mistral-large 123B | Too Tight | Too Tight | Too Tight | Too Tight | Marginal (Q2_K) | Marginal (Q3_K_M) |
| llama-3.1-405b | Too Tight | Too Tight | Too Tight | Too Tight | Too Tight | Too Tight |
| qwen3-coder-480b | Too Tight | Too Tight | Too Tight | Too Tight | Too Tight | Too Tight |
| llama-4-maverick | Too Tight | Too Tight | Too Tight | Too Tight | Too Tight | Too Tight |
| minimax-m2 | Perfect | Good | Perfect | Good | Perfect | Perfect |
| glm-4.5 | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |

* MoE partial offload.

**Bandwidth scaling** vs this detector box (256GB/s):
- M6 153GB/s ≈ ×0.6
- M6 170GB/s ≈ ×0.66
- M5 Pro 307GB/s ≈ ×1.2

So raw t/s in `raw/m6_*.json` and `raw/m5pro_*.json` are optimistic for M6 configs and
slightly conservative for M5 Pro.

### Largest models by tier (llmfit, Perfect fits)

| Config | Largest fitting | Notes |
|---|---|---|
| M6 16GB | ~14-16B dense (Phi-3-medium 14B Q8) | gemma-4 31B MXFP4 fits at ~16GB exactly |
| M6 24GB | ~22B dense (ERNIE-4.5-21B Q8) | Qwen3.5-27B needs Q8 edge |
| M6 32GB | ~28-30B dense (gemma-2-27b Q8) | Qwen3-32B hits Perfect at Q6_K |
| Pro 24GB | same as M6 24GB | die bump, same RAM |
| Pro 48GB | ~40-42B dense (Qwen2.5-72B NVFP4, Llama-3.3-70B NVFP4) | 70B at NVFP4 fits |
| Pro 64GB | ~57-68B dense (Llama-65B Q6_K, Jamba-Mini 51B Q8) | mistral-large 123B still Marginal |

## Reading this for LLM use

**M6 16GB (models 1 & 2):** useless for serious local LLM work. Best you get is
~14B dense, MoE trickles, GPT-OSS-120B via aggressive offload. Avoid.

**M6 24GB (model 3 base):** entry-level, OK for 20B-class and MoE partial. Fine for
chat with 7B-20B models. Skip for anything bigger.

**M6 32GB (model 3 upgraded):** Qwen3-32B Perfect at Q6_K, gemma-2-27b Perfect.
Sweet spot for "small but real" local LLMs. Cheap.

**M5 Pro 48GB:** the only mini tier that fits **70B at Q8-equivalent** (via NVFP4
fits, llmfit "Perfect"). Mistral-large goes Marginal at Q2_K.

**M5 Pro 64GB:** 57-68B dense at Q6_K/Q8 fit Perfect. Mistral-large 123B Marginal
at Q3_K_M (not great quality). Best-of-the-minis but caps out at ~70B — does not
reach frontier (405B+, full DeepSeek R1 671B).

## Verdict vs Mac Studio M5

- If goal is frontier local (405B dense, full R1, GLM-5): **mini can't do it. Studio M5 Ultra 512GB required.**
- If goal is mid-size daily driver (30-70B dense, Qwen3-235B MoE, GLM-4.5): **M5 Pro 64GB mini** is enough and far cheaper.
- If goal is casual coding assistant (7-30B): **M6 32GB** is the cheapest sensible floor.

## Reproduce

```sh
llmfit --memory 16G --ram 16G --cpu-cores 12 fit --json > raw/m6_16.json
llmfit --memory 24G --ram 24G --cpu-cores 12 fit --json > raw/m6_24.json
llmfit --memory 32G --ram 32G --cpu-cores 12 fit --json > raw/m6_32.json
llmfit --memory 24G --ram 24G --cpu-cores 15 fit --json > raw/m5pro_24.json
llmfit --memory 48G --ram 48G --cpu-cores 15 fit --json > raw/m5pro_48.json
llmfit --memory 64G --ram 64G --cpu-cores 18 fit --json > raw/m5pro_64.json
```

## Caveats

- Pricing not in this doc — Apple store pages render client-side, need browser.
- Fit levels from llmfit are memory-driven and reliable; TPS values need scaling
  by bandwidth ratio (noted per section).
- llmfit database includes junk entries; tables above filtered to known model families.
- M6 chip is new, real-world perf may differ from bandwidth-scaled estimates.
