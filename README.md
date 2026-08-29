# Mac Studio M5 / Mac mini M6 — llmfit hardware simulations

Public dataset + docs behind the blog post **"M5 Studio, M6 Mini: Which to Buy for Local AI"**.

Apple opened pre-orders (22 Sep 2026) for the M5 Mac Studio and M6 Mac mini. Before
the hardware shipped, every configuration was simulated through
[llmfit](https://github.com/alexsjones/llmfit) **hardware profiles** (issue
[#969](https://github.com/AlexsJones/llmfit/issues/969) / PR
[#971](https://github.com/AlexsJones/llmfit/pull/971)): each SKU is a small JSON
file with published unified memory **and** memory bandwidth, so tok/s come out of
`fit --json` already on the target roofline — **no post-hoc bandwidth transpose**
against the detector machine.

Model list refreshed 28 Aug 2026 against the current Hugging Face lineup;
older releases (Llama 3.x, DeepSeek V3, Snowflake Arctic, Hermes 4, Jamba) were
dropped as obsolete.

## Model list (24)

- **Frontier:** Kimi K3 2.8T, Qwen3.8-Max 2.4T-A95B, DeepSeek V4-Pro 1.6T,
  LongCat 2.0 1.6T, Ling 2.6-1T, GLM-5.2 743B, Nemotron 3 Ultra 550B
- **Mid:** Llama 4 Maverick 400B, Qwen3.5 397B-A17B, DeepSeek V4-Flash 284B,
  MiniMax M3 427B, Kimi K2.6 1.1T, Nemotron 3 Super 120B, gpt-oss-120b,
  Llama 4 Scout 109B
- **Small:** Gemma 4 31B, Gemma 4 26B-A4B, Qwen3.8 27B, ERNIE 4.5 21B-A3B,
  Granite 4.1 30B, Nemotron 3 Nano 30B, Ministral 3 14B, Gemma 4 12B, gpt-oss-20b

## What is here

- `profiles/*.json` — one llmfit hardware profile per Apple SKU (RAM + GB/s)
- `scripts/machines.json` — machine table (RAM, bandwidth, cores provenance)
- `scripts/run_sims.py` — `llmfit --profile profiles/<sku>.json fit --json`
- `scripts/build_matrix.py` — family selection + fit matrix (uses llmfit tps as-is)
- `scripts/disk_comfort.py` — comfortable SSD sizes from `disk_size_gb`
- `docs/mac-studio.md` / `docs/mac-mini.md` — narrative coverage
- `raw/sims/*.json` — fresh fit dumps (generated; large)
- `raw/final_matrix3.json` — per-config fit + tok/s for the 24 models

## Requirements

llmfit with hardware profiles (`llmfit hardware list` must work). Build from
[PR #971](https://github.com/AlexsJones/llmfit/pull/971) or later.

## Reproduce

```sh
# 1. Simulate every SKU (writes raw/sims/<stem>.json)
python3 scripts/run_sims.py

# 2. Build the blog matrix (no BW scaling step)
python3 scripts/build_matrix.py

# 3. Comfortable SSD sizes from the same dumps
python3 scripts/disk_comfort.py --raw-dir raw/sims --out raw/disk/comfort.json --md raw/disk/comfort.md
```

One-off / debug:

```sh
llmfit --profile profiles/m5max128.json fit --json | jq '.models[0].estimate_basis'
# → gpu_bandwidth_gbps: 614
```

## How it was done (current)

Each Apple config from the published tech-specs pages is a profile under
`profiles/`:

| Profile | RAM | Bandwidth | Product |
|---|---:|---:|---|
| `m6_16` | 16 GB | 153 GB/s | Mac mini M6 |
| `m6_24` / `m6_32` | 24 / 32 GB | 170 GB/s | Mac mini M6 |
| `m5pro_24` / `_48` / `_64` | 24 / 48 / 64 GB | 307 GB/s | Mac mini M5 Pro |
| `m5max36` | 36 GB | 460 GB/s | Mac Studio M5 Max |
| `m5max48` / `_64` / `_128` | 48 / 64 / 128 GB | 614 GB/s | Mac Studio M5 Max |
| `m5ultra96` / `_256` / `_512` | 96 / 256 / 512 GB | 1200 GB/s | Mac Studio M5 Ultra |

```sh
llmfit --profile profiles/m5max128.json fit --json > raw/sims/m5max128.json
```

`--profile` hard-conflicts with `--memory/--ram/--cpu-cores` (no silent mix).

## Selection methodology

For each model family, one canonical Hugging Face variant is chosen and then reused
for every machine configuration (a family is never represented by different repos
on different machines):

1. Match by family pattern, excluding junk / draft variants (`DSpark`, `DFlash`,
   `EAGLE`, distills, slice/prune repos). llmfit itself also demotes EAGLE/DFlash/DSpark
   from ranked fits now.
2. Drop entries whose `memory_required_gb` is below a plausibility floor.
3. Arithmetic sanity gate on Perfect/Good vs available memory.
4. Canonical variant = best survivor on the tightest usable config; preferred
   publishers first (meta-llama, deepseek-ai, Qwen, moonshotai, google, openai, …).
5. Fit levels for every configuration are recomputed from that variant's memory
   footprint vs each SKU's RAM: **Perfect** ≤ 60%, **Good** ≤ 85%, **Marginal** ≤ 98%,
   else **Too Tight** (same bands llmfit uses).
6. Decode tok/s = that variant's `estimated_tps` **from the dump for that SKU**
   (profile already set the published GB/s). No detector-baseline ratio, no hand
   MoE active-param formula.

## Caveats

- Reported tok/s are llmfit roofline estimates, not measurements. Prefill/TTFT is
  only populated when a profile supplies `gpu_compute_tflops_fp16` (these Apple
  profiles omit it → honest `null`).
- Profile schema v1 has no CPU-core field; core count stays whatever the host
  reports. Decode estimates on the GPU bandwidth path are insensitive to that for
  these SKUs (≥8 cores).
- GLM-5.3 / Mistral Large 3 may still be missing from the catalog at scrape time.
- Specs sourced from Apple UK tech-specs pages, 28 Aug 2026.

## Comfortable SSD size

```sh
python3 scripts/disk_comfort.py --raw-dir raw/sims
# or live:
python3 scripts/disk_comfort.py --via-llmfit
```

Formula:  
`need = 100GB OS/apps + sum(top 3 fitting blog-model disks) + max(those) download scratch`,  
round up to an Apple SSD SKU, bump one tier if that SKU would be >85% full.
