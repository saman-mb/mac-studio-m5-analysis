# Blog post outline — `m5-mac-mini-studio-local-ai-guide`

Target: `~/dev/blog/src/content/posts/m5-mac-mini-studio-local-ai-guide.md`

Working title: **"How to Buy a Mac for Local AI in 2026: llmfit on the M5 Studio and M6 Mini"**

Description (frontmatter): "Apple opened pre-orders for the M5 Mac Studio and M6 Mac mini. I simulated every configuration through llmfit (13 configs, 11 flagship models, weighted to the same scale). 405B at Q8 needs the 512GB Ultra at ~£15k. Qwen3-235B fits every mini config via MoE offload. Choose by model class, not chip name."

Tags: `["AI", "hardware", "local-inference", "agentic", "infrastructure"]`

Data backing (NOT guestimation, all llmfit sims):
- `~/dev/mac-studio-m5-analysis/raw/scaled_full.json` — 13 configs × 11 models, fit + raw t/s + scaled t/s
- `~/dev/mac-studio-m5-analysis/raw/m5max48.json` etc. — full DB per config
- Bandwidth scale factors: detector 256GB/s → ×0.6 (M6 16GB), ×0.66 (M6 24/32GB), ×1.2 (M5 Pro), ×1.8 (Max 36GB), ×2.4 (Max 48/64/128GB), ×4.7 (Ultra)

---

## Section 1 — The claim, first

Open with the decision and verdict matrix. "Apple opened pre-orders for the M5 Mac Studio and M6 Mac mini this week. I simulated all 13 configurations through llmfit, weighted the scaled t/s numbers against the detection box's 256GB/s, and the verdict surprised me. Here's the working."

Mention: pre-order now, availability 22 Sep, 512GB Ultra late Oct. Sources: [Apple UK tech-specs Studio](https://www.apple.com/uk/mac-studio/specs/), [Mini](https://www.apple.com/uk/mac-mini/specs/). Price anchors from checkout screenshots: Max 128GB+4TB £6,899, Ultra 256GB+4TB £10,999.

Frontload verdict: skip 36GB Max / 16GB Mini / 96GB Ultra (worst tier). Frontload verdict matrix. Either scroll for the full fit table, or jump to your model class.

## Section 2 — Method: llmfit's actual math, not marketing

- LLM fit on Apple Silicon = unified memory capacity + memory bandwidth. Everything
  else (Neural Engine, "Neural Accelerators") is irrelevant to whether a given model
  loads and decodes at usable t/s.
- llmfit checks every model in the HF database for weight + KV cache fit at a given
  quant, and estimates t/s from memory-bandwidth roofline.
- Simulate mode: `llmfit --memory X --ram X --cpu-cores N fit --json`.
- Sanity-checked the simulator against my Strix Halo box (128GB, 256GB/s). Numbers
  tracked. Then same flags against every Apple config from the tech-specs pages.
- Note for prose review: llmfit is the measurement tool, not the subject. Walk
  through the numbers it produced, don't praise it.

## Section 3 — New lineup (Apple UK, verified)

Mini ships **M6** (not M5) plus **M5 Pro** upgrade — that surprised me.

Two tables, all configs from spec pages:

Studio: Max 36/48/64/128GB, Ultra 96/256/512GB (36c CPU upgrade gate on 256+512).
Mini: M6 16/24/32GB, M5 Pro 24/48/64GB (18c CPU upgrade option).

Dry-wit line candidate: "Apple spec pages list 'Neural Accelerators' like it's a
number you can plan around. It is not. Memory bandwidth is the number."

## Section 4 — Fit by model class (the centrepiece, data-grounded)

Pulls directly from `raw/scaled_full.json` (13 configs × 11 models). For each class,
table every config's fit + scaled t/s + headroom comment. Choose by class:

1. **Small (7–30B dense + gpt-oss-120b + GLM-4.5)** — everything except base 16GB Mini.
2. **Mid (32–70B dense: Qwen3-32B, Llama-3.1/3.3-70B)** — Max 36GB Studio handles the
   32B class (Perfect Q6_K). 70B needs 48GB+ Pro / 128GB+ Studio for Perfect quants.
3. **MoE (Qwen3-235B, DeepSeek V3, R1 0528 distill)** — fits every config via partial
   offload. Dry line: "MoE is the cheat code."
4. **Mid-large dense (mistral-large 123B)** — Marginal on Max 48-64GB, Perfect on Max
   128GB and Ultra 256GB+.
5. **Frontier dense (Llama-3.1-405B, Qwen3-Coder-480B, Llama 4 Maverick)** — Ultra
   256GB gets NVFP4/Marginal fits. Perfect fits need Ultra 512GB. Only class where
   512GB unlocks anything.
6. **1T-class (Ling-1T, GLM-5 754-785B, MiniMax-M1)** — Ultra 512GB only. GLM-5.1-AWQ
   at 767B does ~23 t/s (largest at reading speed). Ling-1T runs at ~2-3 t/s.

## Section 5 — Price per model class

Link class → config → price:
- **Casual (7–30B + MoE)** → M6 32GB mini (cheapest sensible floor)
- **Real 70B daily driver** → M5 Pro 64GB mini
- **Mid-large 123B** → Max 128GB Studio (~£6.9k at 4TB)
- **Frontier 405B + full R1** → Ultra 512GB (~£15-16k est, late Oct)
- Surprise line: Ultra 256GB and Max 128GB tie on everything sub-405B. 512GB exists
  for 405B + full R1 alone. If you don't run those, upsell not worth it.

Price-estimate workings (user screenshots): Max 128+4TB £6,899, Ultra 256+4TB £10,999.
In-die 96→256 RAM jump at checkout = −£4,000 line. 512 est = £15-16k, flagged as
inference from tier pricing, not published.

## Section 6 — What I'm buying, and why

Bridge from the Framework desktop I already own (Strix Halo 128GB, 256GB/s). Why
128GB didn't cut it (405B, GLM-5, full R1 locked out) and why 512GB Ultra is the
actual upgrade. Flagged inference: scaled t/s uses the detector-box ratio, llmfit
has no bandwidth override — real decode depends on GPU cores too, not just bandwidth.

## Section 7 — Reproduce it yourself

Short code block with the 13 `llmfit --memory ... fit --json` commands + link to
GitHub repo `mac-studio-m5-analysis` with all raw JSONs. Close on an insight, not
a summary.

---

## Pre-publish checklist (CLAUDE.md §10)

- `npm run build` ✅
- `npx serve dist -l 4323` + `node check-links.cjs`
- Verify Apple UK tech-specs + llmfit repo links resolve
- draft: true until ready
- All em dashes removed in prose review; check raw tables for accidental — characters
