# Blog post outline — `local-ai-guide-to-m5-mac-lineup`

Target: `~/dev/blog/src/content/posts/m5-mac-mini-studio-local-ai-guide.md`

Working title: **"How to Buy a Mac for Local AI in 2026: llmfit on the M5 Studio and M6 Mini"**

Description (frontmatter): "Apple opened pre-orders for the M5 Mac Studio and M6 Mac mini. I used llmfit's hardware simulation mode to estimate fit and cost per model class. 405B needs the 512GB Ultra at ~£15k. Qwen3-235B fits every mini config. Choose by model class, not chip name."

Tags: `["AI", "hardware", "local-inference", "agentic", "infrastructure"]`

---

## Section 1 — The claim, first

Open with the decision. Lead with what llmfit said and what to buy. Something like:

"Apple opened pre-orders for the M5 Mac Studio and M6 Mac mini this week. I ran every
configuration through llmfit's simulate mode to work out which model classes fit, and
the answer surprised me. Here's the working."

Mention: pre-order now, available 22 Sep. Sources: [Apple UK tech-specs Studio](https://www.apple.com/uk/mac-studio/specs/), [Mini](https://www.apple.com/uk/mac-mini/specs/). Pre-order anchors: Max 128GB+4TB £6,899, Ultra 256GB+4TB £10,999, wait for 512GB in late Oct.

Frontload the verdict matrix. Click — either scroll for the full fit table, or jump to
the section on your model class.

## Section 2 — Why guessing RAM is a scam (llmfit pitch)

- Apple CPU/GPU marketing tells you nothing about LLM fit. The only thing that matters
  for a given model: unified memory capacity + memory bandwidth. Everything else is
  detail.
- llmfit checks every model in the HF database for weight + KV cache fit at a given
  quant, and estimates t/s from memory-bandwidth roofline.
- Simulate mode: `--memory X --ram X --cpu-cores N fit --json` — works on any box.
  Verified against my actual Strix Halo 128GB box (grounded check).
- British English + **no em dashes** — review prose carefully.

## Section 3 — The new lineup (Apple UK, verified)

Mini ships **M6** (not M5) plus **M5 Pro** — that surprised me. Table the 4 mini
configs (M6 12c/12c 16–32GB at 153–170GB/s, M5 Pro 15–18c 24–64GB at 307GB/s) and 2
Studio chips (M5 Max 18c 36–128GB at 460/614GB/s, M5 Ultra 30–36c 96–512GB at 1.2TB/s).

Dry-wit line candidate: "Apple keeps publishing 'Neural Accelerators' on the spec sheet
like it's a useful marketing term. It is not. Memory bandwidth is the number."

## Section 4 — Fit by model class

This is the post's centrepiece. Table every config, with llmfit `fit_level`, against
11 flagship models (from `raw/flagship.json` and `raw/mini_flagship.json`).

Classes:
1. **Small** (7–30B dense) — any config except base 16GB mini.
2. **Mid** (32–70B dense) — Pro 64GB mini or Max 128GB Studio.
3. **MoE big** (Qwen3-235B, DeepSeek V3) — fits every config via partial offload. Dry
   line: "MoE is the cheat code. It fits on anything."
4. **Frontier dense** (Llama 3.1 405B, Qwen3-Coder-480B, Maverick) — 512GB Studio only.
5. **Full 1T-class** (R1 671B, Ling-1T, GLM-5) — 512GB Studio, 1.4–23 t/s scaled. GLM-5
   class is the only thing doing ~20 t/s at that size.

## Section 5 — The price classes

Link class to config:
- **Casual coder (7-30B)** → M6 32GB mini, cheapest sensible.
- **Daily driver 30-70B** → M5 Pro 64GB mini.
- **MoE cheat** → any (incl. base 16GB minis since partial offload).
- **405B Q8 + R1 671B** → Studio Ultra 512GB (~£15-16k with 4TB).
- Surprise line: Ultra 256GB and Max 128GB tie on everything sub-405B. 512GB exists
  for 405B + R1 alone.

## Section 6 — What I bought / would buy

Bridge from the framework desktop I already own (Strix Halo 128GB, 256GB/s). Why 128GB
didn't cut it (405B, GLM-5, R1 locked out) and why the 512GB Ultra is the actual
upgrade. Skip the softmax — this is the original human angle. End with the honest
anchor.

## Section 7 — How to reproduce

One short code block + link to the GitHub repo with all raw JSON
(`mac-studio-m5-analysis` on GitHub). Closing insight line, not a summary.

---

## Pre-publish checklist targets (CLAUDE.md §10)

- `npm run build` ✅
- `npx serve dist -l 4323`
- `node check-links.cjs` — verify Apple UK tech-specs + newsroom URLs, llmfit repo link,
  Math with `$$` only if used (won't be)
- draft: true until launch day
