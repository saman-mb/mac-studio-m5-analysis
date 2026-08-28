# Mac Studio M5 — LLM fit analysis (pre-release hardware simulation)

Simulated which Mac Studio M5 configuration is worth buying for local LLM work,
using [llmfit](https://github.com/alexsjones/llmfit) v1.1.12 with `--memory/--ram/--cpu-cores`
overrides, against Apple's official published specs.

Specs verified against:
- [Mac Studio — Tech Specs (Apple UK)](https://www.apple.com/uk/mac-studio/specs/)
- [Buy Mac Studio (Apple UK)](https://www.apple.com/uk/xc/product/MACSTUDIO_2026_COLLECTION)

Status as of 2026-08-28: **pre-order, available 22.09.**

## Published configurations

### M5 Max (18-core CPU)
- 32-core GPU, 460GB/s — 36GB unified RAM (base)
- 40-core GPU, 614GB/s — 48/64/128GB unified RAM (upgrade gate: 128GB only on the 40-core die)

### M5 Ultra (30-core CPU base / 36-core upgrade)
- 64-core GPU, 1.2TB/s — 96GB unified RAM (base)
- 80-core GPU, 1.2TB/s — 96/256/512GB unified RAM (256GB and 512GB need the 80-core die)
- **512GB listed but not orderable yet — UK store shows "512GB memory option for M5 Ultra coming late October"**

Media engine same both — Neural Accelerators, hw-accelerated ray tracing, AV1 decode.

## What llmfit says per config

Simulated with `llmfit --memory X --ram X --cpu-cores N fit --json` for each
orderable config (+ the coming 512GB option).

| Model | 36GB Max | 64GB Max | 128GB Max | 96GB Ultra | 256GB Ultra | 512GB Ultra |
|---|---|---|---|---|---|---|
| llama-3.1-70b | Good (Q2_K) | Good (AWQ) | Perfect | Perfect | Perfect | Perfect |
| llama-3.3-70b | Good (Q2_K) | Perfect | Perfect | Perfect | Perfect | Perfect |
| qwen3-32b | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |
| qwen3-235b (A22B MoE) | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* | Perfect (full Q8 ~120GB) |
| deepseek-v3 | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* | Perfect* |
| gpt-oss-120b | Perfect | Perfect | Perfect | Perfect | Perfect | Perfect |
| mistral-large 123B | Too Tight | Marginal | **Perfect** | Marginal | **Perfect** | **Perfect** |

*MoE partial offload — only some experts resident.

**Fit levels independent of bandwidth; TPS values from llmfit were calibrated
against the detecting machine's 256GB/s and cannot represent the Max (460/614GB/s)
or Ultra (1.2TB/s) — llmfit has no bandwidth override flag. Real decode TPS on M5
Max ≈ 1.8–2.4×, M5 Ultra ≈ 4.7× the raw values in `raw/`.**

## Verdict (updated — target = best local models, single machine)

User constraint: 128GB already insufficient (current Framework Desktop = Strix Halo,
128GB, 256GB/s). Wants frontier local models on one box.

**Claim-type audit (user asked "nothing made up"):**
- Sourced + verified against Apple tech-specs/store pages: all chip/RAM gating, "512GB late Oct"
- llmfit fit levels (+ raw `raw/*.json`): all model tables below
- llmfit TPS values: unreliable (no bandwidth override → uses this box's 256GB/s); do not quote
- "4.7× bandwidth" / "RAM 4×": published spec ratios, quoted as such
- KV/context headroom commentary: standard GGUF rule of thumb, flagged as such

Verified just now against the raw JSONs (misclaim caught + corrected):

| Frontier model | 256GB Ultra (best-scoring hit) | 512GB Ultra (best-scoring hit) |
|---|---|---|
| Llama 3.1 405B | Marginal (AWQ-4bit, 213GB) | **Perfect (Q8, 440GB)** |
| Llama 4 Maverick | Good (FP8, 206GB) | **Perfect** |
| Qwen3-Coder-480B | **Perfect (NVFP4, 123GB)** — corrected from earlier "Marginal" | Perfect (AWQ, 246GB) |
| Qwen3-235B | Perfect (120GB) | Perfect (120GB) |
| DeepSeek R1 0528 (671B full) | Good–Perfect (NVFP4 ~203GB, or full Q5_K_M 351GB won't fit) | **Good (Q5_K_M 351GB) / Perfect (NVFP4 ~202GB)** |
| Mistral Large | Perfect | Perfect |
| llama-3.1-70b | Perfect | Perfect |
| llama-3.3-70b | Perfect | Perfect |
| MiniMax-M2.7 | Perfect | Perfect |
| GLM-4.5 | Perfect | Perfect |

So 512GB specifically buys you: 405B at Q8, R1 671B at reasonable quants, Maverick Q8.
Everything else was already Perfect at 256GB — pick 512 only for the frontier tier,
or for guaranteed headroom on KV+context when serving several models concurrently.

(Coffee-rule for KV math: KV per model ≈ 0.5–2GB per 8k ctx across listed dense models,
tiny vs weights; "headroom" commentary is inference, not llmfit output.)

## Recommendation (final, llmfit-grounded)

For "best local models on 1 machine": **wait for 512GB.** The delta between 256 and
512 at llmfit levels = 405B Q8 + full DeepSeek R1 671B. That is the entire reason
to buy the bigger box; without those, 256GB and even the 40c/128GB M5 Max tie.

(Note: 512GB RAM is on UK's page but hidden until late Oct, per your screenshot.)

## Price estimate (512GB, UK)

Anchors (user screenshots, Apple UK checkout):
- M5 Max **128GB + 4TB = £6,899**
- M5 Ultra **256GB + 4TB = £10,999** (30c/64c die)
- 96GB → 256GB upgrade on Ultra (same die): **−£4,000** line shown at checkout

Reading:
- Max 128GB → Ultra 256GB at 4TB = £4,100, but bundles Max→Ultra die upgrade + CPU/GPU
  jumps + 128GB RAM — not a clean RAM-price signal.
- The clean signal is the within-die 96→256 jump = £4,000 for +160GB.

Estimate:
- 256GB → 512GB on the upgraded Ultra die (36c/80c) ≈ **+£4,000–£5,000** (1.6× the GB of
  the 96→256 step, and Apple keeps tier pricing flat-to-slightly-higher at top tiers).
- **512GB + 4TB (Ultra, 36c/80c) ≈ £14,999–£15,999**.

Caveat: 512GB forces the 36c/80c die upgrade (per UK tech-specs page) — that upgrade is
already included in the 256GB price above, so the 512 number assumes same die, RAM only.
Late-Oct reveal confirms.

## Reproduce

```sh
pipx install llmfit   # or: uv tool install llmfit
# each config:
llmfit --memory 36G  --ram 36G  --cpu-cores 18  fit --json > raw/m5max36.json
llmfit --memory 64G  --ram 64G  --cpu-cores 18  fit --json > raw/m5max64.json
llmfit --memory 128G --ram 128G --cpu-cores 18  fit --json > raw/m5max128.json
llmfit --memory 96G  --ram 96G  --cpu-cores 30  fit --json > raw/m5ultra96.json
llmfit --memory 256G --ram 256G --cpu-cores 30  fit --json > raw/m5ultra256.json
llmfit --memory 512G --ram 512G --cpu-cores 36  fit --json > raw/m5ultra512.json
```

`raw/flagship.json` holds the per-config summary for the flagship models above.

## Caveats

- llmfit's `fit_level` is memory-driven and reliable; `estimated_tps` here is based
  on the detecting machine and must be scaled, not quoted literally.
- llmfit DB contains junk HF entries; flagship names above were queried explicitly.
- Pricing was not scraped (UK store pages render client-side). Grab price at order time.
- Unreleased hardware — real perf may differ from bandwidth-scaled estimates.
