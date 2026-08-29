# Mac Studio M5 — full configuration coverage

*Specs verified against [Apple UK tech-specs](https://www.apple.com/uk/mac-studio/specs/).*
*Fit levels + tok/s from llmfit hardware profiles (`profiles/*.json`, issue #969) — published RAM **and** GB/s per SKU; no detector-BW post-scale.*

## Every config (Apple UK, verified)

| Config | Chip | CPU | GPU | RAM | Bandwidth | Storage |
|---|---|---|---|---|---|---|
| Max 36GB base | M5 Max | 18c | 32c | 36GB | 460GB/s | 512GB |
| Max 48GB | M5 Max | 18c | 40c* | 48GB | 614GB/s | 512GB+ |
| Max 64GB | M5 Max | 18c | 40c | 64GB | 614GB/s | 1TB |
| Max 128GB | M5 Max | 18c | 40c | 128GB | 614GB/s | 1TB+ |
| Ultra 96GB base | M5 Ultra | 30c | 64c | 96GB | 1.2TB/s | 1TB |
| Ultra 96GB upgraded | M5 Ultra | 36c | 80c | 96GB | 1.2TB/s | 1TB+ |
| Ultra 256GB | M5 Ultra | 36c | 80c | 256GB | 1.2TB/s | 1TB+ |
| Ultra 512GB | M5 Ultra | 36c | 80c | 512GB | 1.2TB/s | late Oct |

*48GB needs the 40-core GPU die upgrade (Apple specs page).

Pre-order open, availability 22 Sep. 512GB listed but checkout-hidden until late Oct.

## What each config can and can't run

### Max 36GB (460GB/s)
- **CAN:** gpt-oss-120b (Perfect), qwen3-32b (Perfect Q6_K), qwen3-235b MoE* (Perfect),
  deepseek-v3* (Perfect), deepseek-r1-0528 distill (Perfect), glm-4.5 (Perfect),
  llama-3.1-70b (Good Q2_K), llama-3.3-70b (Good Q2_K), minimax-m2 (Good)
- **CAN'T:** mistral-large 123B (Too Tight), llama-3.1-405b, qwen3-coder-480b,
  llama-4-maverick (all Too Tight)

### Max 48GB (614GB/s)
- **CAN:** everything above + llama-3.3-70b Perfect, mistral-large (Marginal Q2_K, low
  quality)
- **CAN'T:** llama-3.1-405b, qwen3-coder-480b, llama-4-maverick

### Max 64GB (614GB/s)
- **CAN:** everything above at higher quants (mistral-large Marginal Q3_K_M)
- **CAN'T:** llama-3.1-405b, qwen3-coder-480b, llama-4-maverick

### Max 128GB (614GB/s)
- **CAN:** mistral-large 123B (Perfect Q6_K, 103GB), qwen3-coder-480b (Marginal 3bit),
  everything smaller at high quants (llama-3.3-70b Perfect Q8, glm-4.5 55GB Q8)
- **CAN'T:** llama-3.1-405b, qwen3-coder-480b (good quants), llama-4-maverick,
  deepseek-r1-0528 full 671B

### Ultra 96GB (1.2TB/s)
- **CAN:** glm-4.5 55GB (Good Q6_K), gpt-oss-120b, everything ≤70B at good quants
- **CAN'T:** mistral-large 123B (Marginal Q5_K_M), llama-3.1-405b, qwen3-coder-480b,
  llama-4-maverick, deepseek-r1-0528 full
- Weird position: more bandwidth than Max 128GB but less RAM. llmfit rates 96GB below
  Max 128GB on model fit. Skip this tier.

### Ultra 256GB (1.2TB/s)
- **CAN:** llama-3.1-405b (Marginal AWQ-4bit ~213GB), qwen3-coder-480b (Perfect NVFP4
  ~123GB), llama-4-maverick (Good Q4_K_M ~206GB), mistral-large 123B (Perfect Q8),
  deepseek-r1-0528 (NVFP4 Good ~203GB), everything smaller Perfect
- **CAN'T:** llama-3.1-405b (Perfect Q8, needs 440GB), deepseek-r1-0528 full Q5_K_M
  (351GB), llama-4-maverick Perfect Q8

### Ultra 512GB (1.2TB/s) — late Oct
- **CAN:** llama-3.1-405b (Perfect Q8, 440GB), qwen3-coder-480b (Perfect AWQ ~246GB),
  llama-4-maverick (Perfect Q8 ~206GB), deepseek-r1-0528 full (Good Q5_K_M 351GB /
  Perfect NVFP4 ~202GB), mistral-large 123B (Perfect Q8 133GB), every flagship at
  highest quants
- **CAN'T:** nothing in llmfit's DB. GLM-5.1-AWQ 767B Good (393GB), Ling-1T 1.0T
  Good (403-414GB), MiniMax-M1-80k 456B Perfect (494GB) all fit.

* MoE partial offload: only active experts resident; listed memory is per-token
  working set, not full weights.

## Bandwidth scaling vs detector box

Tok/s already use each profile's published GB/s (no scale step):

| Config | Bandwidth | Scale factor |
|---|---|---|
| Max 36GB | 460GB/s | ×1.8 |
| Max 48/64/128GB | 614GB/s | ×2.4 |
| Ultra (all) | 1.2TB/s | ×4.7 |

Fit levels (Perfect/Good/Marginal/Too Tight) are memory-driven and don't need scaling.

## Price anchors (user screenshots, Apple UK)

- Max 128GB + 4TB = £6,899
- Ultra 256GB + 4TB = £10,999
- Ultra in-die RAM 96→256 jump = −£4,000
- Estimated Ultra 512GB + 4TB ≈ £15,000–£16,000

## Verdict

- **For daily-driver 30-70B dense, max quality:** Max 128GB. Cheapest config where
  mistral-large 123B Perfect. ~£6.9k.
- **For Qwen3-Coder-480B / Maverick / R1 NVFP4 partial:** Ultra 256GB. ~£11k.
- **For 405B Q8 + full R1 671B + frontier 1T-class:** Ultra 512GB. Wait for late Oct.
  ~£15-16k.
- **Skip:** 36GB (can't run 70B), 48GB (weird middle), 96GB (Ultra's worst tier,
  beaten by Max 128GB).

## Reproduce

```sh
python3 scripts/run_sims.py   # or: llmfit --profile profiles/<sku>.json fit --json
```

Full per-model detail in `raw/studio_complete.json`.
