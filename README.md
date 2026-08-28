# Mac Studio M5 / Mac mini M6 — llmfit hardware simulations

Public dataset + docs behind the blog post **"M5 Studio, M6 Mini: Which to Buy for Local AI"**.

Apple opened pre-orders (22 Sep 2026) for the M5 Mac Studio and M6 Mac mini. Before
the hardware shipped, every configuration was simulated through
[llmfit](https://github.com/alexsjones/llmfit) using its hardware-override flags, and
fit verdicts + estimated tok/s were recorded for the 24 current open-weight models
below. Model list refreshed 28 Aug 2026 against the current Hugging Face lineup;
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

- `docs/mac-studio.md` — full configuration coverage for Mac Studio (7 configs)
- `docs/mac-mini.md` — full configuration coverage for Mac mini (6 configs)
- `raw/final_matrix3.json` — per config: fit level, raw + scaled tok/s, chosen
  variant, quant and memory for all 24 models (the dataset used in the post)
- `raw/matrix4.html` — the rendered fit matrix (HTML table)
- `raw/build_matrix3.py` — the extraction script: family patterns, variant
  selection, bandwidth scaling. Re-run against fresh `fit --json` output to
  reproduce

## How it was done

llmfit detects local hardware, but `--memory`, `--ram` and `--cpu-cores` override it
to simulate any machine. Each Apple config from the published tech-specs pages was
simulated with:

```sh
llmfit --memory 16G  --ram 16G  --cpu-cores 12 fit --json > m6_16.json
llmfit --memory 24G  --ram 24G  --cpu-cores 12 fit --json > m6_24.json
llmfit --memory 32G  --ram 32G  --cpu-cores 12 fit --json > m6_32.json
llmfit --memory 24G  --ram 24G  --cpu-cores 15 fit --json > m5pro_24.json
llmfit --memory 48G  --ram 48G  --cpu-cores 15 fit --json > m5pro_48.json
llmfit --memory 64G  --ram 64G  --cpu-cores 18 fit --json > m5pro_64.json
llmfit --memory 36G  --ram 36G  --cpu-cores 18 fit --json > m5max36.json
llmfit --memory 48G  --ram 48G  --cpu-cores 18 fit --json > m5max48.json
llmfit --memory 64G  --ram 64G  --cpu-cores 18 fit --json > m5max64.json
llmfit --memory 128G --ram 128G --cpu-cores 18 fit --json > m5max128.json
llmfit --memory 96G  --ram 96G  --cpu-cores 30 fit --json > m5ultra96.json
llmfit --memory 256G --ram 256G --cpu-cores 30 fit --json > m5ultra256.json
llmfit --memory 512G --ram 512G --cpu-cores 36 fit --json > m5ultra512.json
```

## Selection methodology

For each model family, one llmfit entry is picked per config:

1. Match by family pattern (e.g. `deepseek-v4-flash`), excluding draft/speculative
   and distill variants (`DSpark`, `DFlash`, `EAGLE`, prunes, distills).
2. Drop entries whose `memory_required_gb` is below a plausibility floor (roughly a
   2-bit floor of the true parameter count). The HF-derived database contains
   mis-parsed community/MLX repos claiming e.g. 117B models at 1.2GB; without this
   gate they produce nonsense "Perfect on 16GB" verdicts.
3. Among surviving entries, prefer canonical publishers (meta-llama, deepseek-ai,
   Qwen, moonshotai, google, openai, nvidia, unsloth, mlx-community, ...) and rank
   by fit level first, then score. A usable quant beats a higher-scoring unusable
   one for a "can I run it" matrix.

## Caveats

- Fit levels (Perfect/Good/Marginal/Too Tight) are memory-driven and reliable.
- Tok/s estimates are scaled by the published memory-bandwidth ratio against the
  machine llmfit ran on (256GB/s detector). llmfit has no bandwidth override flag,
  so treat scaled tok/s as a rough guide.
- GLM-5.3 and GLM-5.3-Flash were announced but weights were not scoreable in
  llmfit's catalog at publication time, so the GLM rows use GLM-5.2 (same 743B
  base). Mistral Large 3 675B was likewise not yet scoreable.
- Specs sourced from Apple UK tech-specs pages, 28 Aug 2026.
