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
128GB, 256GB/s). Wants frontier local models on one box. Changes the calculus —
the frontier tier is all >200GB weights:

| Frontier model | 256GB Ultra | 512GB Ultra |
|---|---|---|
| Llama 3.1 405B | Marginal (AWQ 4bit, ~213GB) | **Perfect (Q8, 440GB)** |
| Qwen3-Coder-480B | Marginal (3bit MLX, ~246GB) | **Perfect (AWQ/Q8, 246GB)** |
| Llama 4 Maverick (17B-128E) | Good (Q4_K_M) | **Perfect (Q8)** |
| Qwen3-235B-A22B | Perfect (120GB Q8) | Perfect (120GB Q8) |
| DeepSeek R1 0528 (671B) | can't (350GB+ full) | Good (Q5_K_M, 351GB) |
| MiniMax-M2.7 | Perfect (4bit) | Perfect (4bit) |
| GLM-4.5-Air | Perfect | Perfect |

- 256GB gates 405B-class dense to 4-bit marginal, leaves no headroom for KV + context.
- 512GB fits 405B at Q8 **and** leaves ~70GB for context/KV/OS.
- DeepSeek R1 671B still won't fit comfortable at 512 (350GB Q5_K_M = Good but tight with KV); Qwen3-235B and Qwen3-Coder-480B are the sweet spot frontier models for 512GB.
- M5 Ultra 512GB requires the 36c CPU / 80c GPU die upgrade (per UK tech-specs page) — factor that into cost.
- 1.2TB/s bandwidth + 512GB unified = only consumer Mac that runs 405B-class dense locally without multi-node.
- Bandwidth gain vs current Strix Halo box: **4.7×**, RAM gain: **4×**.

## Recommendation (final)

**Wait for M5 Ultra 512GB (late Oct), with the 36c CPU / 80c GPU die.** It is the
only config that unlocks 405B-class dense at decent quants on a single Mac.

If buying before Oct: M5 Ultra 256GB gets you Qwen3-235B/Qwen3-Coder-480B perfect
fits now, with 405B-class at marginal 4-bit. But you already have a 128GB box —
256 is a lateral move for your stated goal; 512 is the actual upgrade.

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
