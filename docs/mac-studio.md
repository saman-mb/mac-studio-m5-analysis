# Mac Studio M5 — Local LLM guide

*Consolidated from the root README — kept for context.*

## Published configurations (Apple UK tech-specs, verified)

### M5 Max (18-core CPU)
- 32-core GPU, 460GB/s — 36GB unified RAM (base)
- 40-core GPU, 614GB/s — 48/64/128GB (128GB gated to 40-core die)

### M5 Ultra (30c base / 36c upgraded)
- 64-core GPU, 1.2TB/s — 96GB (base)
- 80-core GPU, 1.2TB/s — 96/256/512GB (256 & 512 gated to 80-core die)
- **512GB hidden at checkout, "coming late October"** (your screenshot)

Pre-order now, available 22.09.

## Fit table (llmfit sims with memory override)

| Model | 36GB Max | 64GB Max | 128GB Max | 96GB Ultra | 256GB Ultra | 512GB Ultra |
|---|---|---|---|---|---|---|
| llama-3.1-70b | Good (Q2_K) | Good (AWQ) | Perfect | Perfect | Perfect | Perfect |
| llama-3.3-70b | Good (Q2_K) | Perfect | Perfect | Perfect | Perfect | Perfect |
| qwen3-32b | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |
| qwen3-235b (MoE) | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* | Perfect |
| deepseek-v3 | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* | Perfect |
| gpt-oss-120b | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |
| mistral-large 123B | Too Tight | Marginal | **Perfect** | Marginal | **Perfect** | **Perfect** |
| **Frontier:** | | | | | | |
| llama-3.1-405b | Too Tight | Too Tight | Too Tight | Too Tight | Marginal (AWQ 4bit) | **Perfect (Q8)** |
| llama-4-maverick | Too Tight | Too Tight | Too Tight | Too Tight | Good (FP8) | **Perfect (Q8)** |
| qwen3-coder-480b | Too Tight | Too Tight | Too Tight | Too Tight | Perfect (NVFP4 ~123GB) | **Perfect (AWQ ~246GB)** |
| deepseek-r1-0528 full | Too Tight | Too Tight | Too Tight | Too Tight | NVFP4 Good ~203GB | **Good Q5_K_M ~351GB** |

* MoE partial offload.

**Fit levels** = llmfit memory-check, reliable.
**Raw TPS values** in `raw/m5*.json` come from this box's 256GB/s detector and
must be scaled: M5 Max ≈ ×1.8–2.4 (460/614GB/s), M5 Ultra ≈ ×4.7 (1.2TB/s).

## Largest models that work on 512GB

llmfit raw values, scaled by 4.7:

| Model | Params | fit | ~t/s | mem |
|---|---|---|---|---|
| GLM-5.1-AWQ (cyankiwi) | 767B | Good | ~23 | 393GB |
| GLM-5 (zai-org FP8) | 754B | Good | ~20 | 386GB |
| GLM-5.2-NVFP4 | 779B | Good | ~9 | 399GB |
| QuantTrio GLM-5.2 | 785B | Good | ~9 | 402GB |
| Ling-1T | 1.0T | Good | ~3 | 403GB |
| Ling-2.5-1T | 1.0T | Good | ~3 | 408GB |
| Ling-2.6-1T | 1.0T | Good | ~2.3 | 414GB |
| Llama-3.1-405B FP8 | 406B | Perfect | ~1.4 | 440GB |
| DeepSeek-V3.2-NVFP4 | 395B | Perfect | ~1.9 | 428GB |
| MiniMax-M1-80k | 456B | Perfect | ~1.4 | 494GB |

GLM-5/5.1-class at 4-bit = largest that clears ~20 tok/s.

## Recommendation (for "best frontier models on one machine")

**Wait for M5 Ultra 512GB (late Oct), with the 36c/80c die.** 405B Q8 and full
DeepSeek R1 671B only fit at 512GB. If those don't matter, 128GB Max ties with
256GB Ultra for everything smaller, and is cheaper.

## Price estimates (UK)

Anchors from your screenshots:
- M5 Max **128GB + 4TB = £6,899**
- M5 Ultra **256GB + 4TB = £10,999**
- Ultra 96→256 RAM line = **−£4,000** at checkout (in-die RAM jump)

Estimated:
- **512GB + 4TB Ultra ≈ £15,000–£16,000** (+£4-5k over £10,999 for the 256→512 tier)
- Caveat: inference from tier pattern, not published

## Reproduce

```sh
llmfit --memory 36G  --ram 36G  --cpu-cores 18 fit --json > raw/m5max36.json
llmfit --memory 64G  --ram 64G  --cpu-cores 18 fit --json > raw/m5max64.json
llmfit --memory 128G --ram 128G --cpu-cores 18 fit --json > raw/m5max128.json
llmfit --memory 96G  --ram 96G  --cpu-cores 30 fit --json > raw/m5ultra96.json
llmfit --memory 256G --ram 256G --cpu-cores 30 fit --json > raw/m5ultra256.json
llmfit --memory 512G --ram 512G --cpu-cores 36 fit --json > raw/m5ultra512.json
```
