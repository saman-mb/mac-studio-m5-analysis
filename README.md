# Mac Studio M5 / Mac mini M6 — llmfit hardware simulations

Public dataset + docs behind the blog post **"M5 Studio, M6 Mini: Which to Buy for Local AI"**.

Apple opened pre-orders (22 Sep 2026) for the M5 Mac Studio and M6 Mac mini. Before
the hardware shipped, every configuration was simulated through
[llmfit](https://github.com/alexsjones/llmfit) using its hardware-override flags, and
fit verdicts were recorded for 18 flagship open-weight models.

## What is here

- `docs/mac-studio.md` — full configuration coverage for Mac Studio (7 configs)
- `docs/mac-mini.md` — full configuration coverage for Mac mini (6 configs)
- `raw/*.json` — derived llmfit results:
  - `final_matrix2.json` — the 13-config × 18-model fit matrix used in the post
  - `data.json` / `balanced_models.json` — best-scoring variant per model family
  - `scaled_full.json` — raw + bandwidth-scaled tok/s per config
  - `flagship.json`, `mini_flagship.json`, `studio_complete.json`, `new_models.json`

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

## Caveats

- Fit levels (Perfect/Good/Marginal/Too Tight) are memory-driven and reliable.
- Tok/s estimates are scaled by the published memory-bandwidth ratio against the
  machine llmfit ran on (256GB/s detector). llmfit has no bandwidth override flag,
  so treat scaled tok/s as a rough guide.
- Specs sourced from Apple UK tech-specs pages, 28 Aug 2026.
