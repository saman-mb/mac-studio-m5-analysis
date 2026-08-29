#!/usr/bin/env python3
"""Build the blog fit matrix from llmfit --profile dumps.

Tok/s come straight from each dump's `estimated_tps` — no detector-BW ratio
and no hand MoE formula. Fit levels are recomputed from the canonical
variant's memory footprint vs each SKU's RAM (60/85/98%) so rows stay
monotonic across machine sizes.

Usage:
  python3 scripts/build_matrix.py
  python3 scripts/build_matrix.py --raw-dir raw/sims --out raw/final_matrix3.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from machines import DEFAULT_RAW_DIR, ROOT, load_machines

FAM = [
    ("frontier", "Kimi K3 2.8T", "CN", r"kimi-k3", r"dspark|dflash|eagle|draft|pruned|0\.40b|abliterated|uncensored|derisked|k2\.|distill", ["moonshotai/", "unsloth/", "mlx-community/", "lmstudio-community/"]),
    ("frontier", "Qwen3.8-Max 2.4T", "CN", r"qwen3\.8-2\.4", r"dspark|pruned|distill", ["qwen/", "amd/", "mlx-community/"]),
    ("frontier", "DeepSeek V4-Pro 1.6T", "CN", r"deepseek-v4-pro", r"qwen3\.5|distill|spark", ["deepseek-ai/", "unsloth/", "mlx-community/", "intel/", "nvidia/", "redhatai/"]),
    ("frontier", "LongCat 2.0 1.6T", "CN", r"longcat-2\.0", r"uncensored|heretic", ["meituan-longcat/", "mlx-community/", "intel/"]),
    ("frontier", "Ling 2.6 1T", "CN", r"ling-2\.6-1t", r"-base", ["inclusionai/", "mlx-community/"]),
    ("frontier", "GLM-5.2 743B", "CN", r"glm-5\.2", r"dspark|speculator|sparkulator|vision|distill|dflash", ["zai-org/", "unsloth/", "mlx-community/", "redhatai/"]),
    ("frontier", "Nemotron 3 Ultra 550B", "US", r"nemotron-3-ultra", r"abliterated|uncensored|reap", ["nvidia/", "redhatai/", "unsloth/", "mlx-community/"]),
    ("mid", "Llama 4 Maverick 400B", "US", r"llama-4-maverick", r"", ["meta-llama/", "redhatai/"]),
    ("mid", "Qwen3.5 397B-A17B", "CN", r"qwen3\.5-397b", r"", ["qwen/", "amd/", "mlx-community/", "unsloth/"]),
    ("mid", "DeepSeek V4-Flash 284B", "CN", r"deepseek-v4-flash", r"qwen3\.5|distill|dspark", ["deepseek-ai/", "unsloth/", "mlx-community/", "crusoeai/", "amd/", "redhatai/"]),
    ("mid", "MiniMax M3 427B", "CN", r"minimax-m3", r"eagle|dspark", ["minimaxai/", "nvidia/", "mlx-community/", "cyankiwi/"]),
    ("mid", "Kimi K2.6 1.1T", "CN", r"kimi-k2\.6", r"dflash|dspark|eagle|distill|qwopus|healed", ["moonshotai/", "unsloth/", "mlx-community/", "lmstudio-community/", "nvidia/", "novita/", "z-lab/"]),
    ("mid", "Nemotron 3 Super 120B", "US", r"nemotron-3-super", r"reap|math|abliterated|uncensored", ["nvidia/", "cyankiwi/", "mlx-community/", "unsloth/"]),
    ("mid", "gpt-oss-120b 117B", "US", r"gpt-oss-120b", r"vision|eagle|bf16|fp16|-f16", ["openai/", "unsloth/", "mlx-community/", "lmstudio-community/", "nvidia/", "redhatai/"]),
    ("mid", "Llama 4 Scout 109B", "US", r"llama-4-scout", r"abliterated", ["meta-llama/", "redhatai/"]),
    ("small", "Gemma 4 31B", "US", r"gemma-4-31b", r"heretic|abliterated|uncensored|deckard|opus|scotoma|novelist|eclipse|roleplay", ["google/", "unsloth/", "mlx-community/", "lmstudio-community/", "redhatai/", "quanttrio/", "cyankiwi/"]),
    ("small", "Gemma 4 26B-A4B", "US", r"gemma-4-26b-a4b", r"heretic|abliterated|uncensored|sompoa|pawarshardul", ["google/", "nvidia/", "unsloth/", "mlx-community/", "lmstudio-community/", "redhatai/"]),
    ("small", "Qwen3.8 27B", "CN", r"qwen3\.8-27b", r"heretic|abliterated|distill|jang|crack|minitron|fable", ["qwen/", "unsloth/", "mlx-community/", "lmstudio-community/", "amd/", "ulkaa/"]),
    ("small", "ERNIE 4.5 21B-A3B", "CN", r"ernie-4\.5-21b", r"", ["baidu/", "lmstudio-community/", "cyankiwi/", "mlx-community/"]),
    ("small", "Granite 4.1 30B", "US", r"granite-4\.1-30b", r"", ["ibm-granite/", "mlx-community/", "nightmedia/"]),
    ("small", "Nemotron 3 Nano 30B", "US", r"nemotron-3-nano-30b", r"omni|-base", ["nvidia/", "unsloth/", "mlx-community/", "lmstudio-community/"]),
    ("small", "Ministral 3 14B", "EU", r"ministral-3-14b", r"", ["mistralai/", "ccharnkij/", "automatosx/"]),
    ("small", "Gemma 4 12B", "US", r"gemma-4-12b", r"heretic|abliterated|esper|guardpoint|mlponly", ["google/", "unsloth/", "mlx-community/", "lmstudio-community/", "mattbucci/"]),
    ("small", "gpt-oss-20b 21B", "US", r"gpt-oss-20b", r"vision|internvl|codegpt|heretic|bf16|fp16|-f16", ["openai/", "unsloth/", "mlx-community/", "lmstudio-community/", "nvidia/", "onnx-community/"]),
]

MIN_GB = {
    "Kimi K3 2.8T": 600,
    "Qwen3.8-Max 2.4T": 550,
    "DeepSeek V4-Pro 1.6T": 350,
    "LongCat 2.0 1.6T": 350,
    "Ling 2.6 1T": 220,
    "GLM-5.2 743B": 160,
    "Nemotron 3 Ultra 550B": 120,
    "Llama 4 Maverick 400B": 90,
    "Qwen3.5 397B-A17B": 90,
    "MiniMax M3 427B": 95,
    "Kimi K2.6 1.1T": 250,
    "Nemotron 3 Super 120B": 28,
    "gpt-oss-120b 117B": 28,
    "Llama 4 Scout 109B": 25,
    "DeepSeek V4-Flash 284B": 65,
    "Gemma 4 31B": 9,
    "Gemma 4 26B-A4B": 7,
    "Qwen3.8 27B": 7.5,
    "ERNIE 4.5 21B-A3B": 5.5,
    "Granite 4.1 30B": 8,
    "Nemotron 3 Nano 30B": 8,
    "Ministral 3 14B": 4,
    "Gemma 4 12B": 3.5,
    "gpt-oss-20b 21B": 5.5,
}

JUNK = re.compile(r"slice|reap|prune|pct$|-\d+pct|fragm|draft|-\d+b$")
RANK = {"Perfect": 0, "Good": 0, "Marginal": 1, "Too Tight": 2}


def sane(m: dict) -> bool:
    mem = m.get("memory_required_gb") or 0
    avail = m.get("memory_available_gb") or 0
    fit = m.get("fit_level")
    if fit in ("Perfect", "Good") and avail and mem > avail * 0.98:
        return False
    if JUNK.search(m["name"].lower()):
        return False
    return True


def candidates(models: list[dict], inc: str, exc: str, min_gb: float) -> list[dict]:
    pool = [
        m
        for m in models
        if re.search(inc, m["name"].lower())
        and not (exc and re.search(exc, m["name"].lower()))
        and (m.get("memory_required_gb") or 0) >= min_gb
        and sane(m)
    ]
    return pool


def choose_canonical(by_cfg: dict[str, list[dict]], prefs: list[str], stems: list[str]):
    def best(pool: list[dict]):
        if not pool:
            return None

        def key(m):
            is_pref = 0 if any(m["name"].lower().startswith(p) for p in prefs) else 1
            return (
                is_pref,
                RANK.get(m["fit_level"], 9),
                -(m.get("score") or 0),
                m.get("memory_required_gb") or 0,
            )

        return min(pool, key=key)

    for stem in stems:
        got = best([m for m in by_cfg.get(stem, []) if RANK.get(m["fit_level"], 9) <= 1])
        if got and RANK.get(got["fit_level"], 9) <= 1:
            return got, stem
    for stem in reversed(stems):
        got = best(by_cfg.get(stem, []))
        if got:
            return got, stem
    return None, None


def fit_by_memory(mem: float, avail: float) -> str:
    if mem <= 0.60 * avail:
        return "Perfect"
    if mem <= 0.85 * avail:
        return "Good"
    if mem <= 0.98 * avail:
        return "Marginal"
    return "Too Tight"


def index_by_name(models: list[dict]) -> dict[str, dict]:
    return {m["name"]: m for m in models}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    ap.add_argument("--out", type=Path, default=ROOT / "raw" / "final_matrix3.json")
    args = ap.parse_args()

    machines = load_machines()
    stems = [m["stem"] for m in machines]
    ram = {m["stem"]: float(m["ram_gb"]) for m in machines}
    bw = {m["stem"]: float(m["bandwidth_gbps"]) for m in machines}

    dumps: dict[str, list[dict]] = {}
    indexes: dict[str, dict[str, dict]] = {}
    for stem in stems:
        path = args.raw_dir / f"{stem}.json"
        if not path.exists():
            print(f"error: missing dump {path} — run scripts/run_sims.py first", file=sys.stderr)
            return 1
        models = json.loads(path.read_text())["models"]
        # Sanity: profile bandwidth must be what we asked for.
        got_bw = (models[0].get("estimate_basis") or {}).get("gpu_bandwidth_gbps")
        if got_bw != bw[stem]:
            print(
                f"error: {stem} dump bw={got_bw}, profile expects {bw[stem]}",
                file=sys.stderr,
            )
            return 1
        dumps[stem] = models
        indexes[stem] = index_by_name(models)

    out: dict = {}
    audit: dict = {}

    for grp, disp, _region, inc, exc, prefs in FAM:
        by_cfg = {
            stem: candidates(dumps[stem], inc, exc, MIN_GB[disp]) for stem in stems
        }
        canon, canon_cfg = choose_canonical(by_cfg, prefs, stems)
        if canon is None:
            for stem in stems:
                out.setdefault(stem, {})[disp] = {
                    "fit": "Missing",
                    "raw_tps": 0,
                    "scaled_tps": 0,
                    "mem": 0,
                    "variant": None,
                    "quant": None,
                    "tps_method": "missing",
                    "bandwidth_gbps": bw[stem],
                }
            audit[disp] = {"canonical": None, "chosen_on": None}
            continue

        mem = canon["memory_required_gb"]
        for stem in stems:
            row = indexes[stem].get(canon["name"])
            # Prefer the live estimate on this SKU (correct BW + quant for that pool).
            if row is not None:
                tps = row.get("estimated_tps") or 0
                quant = row.get("best_quant")
            else:
                tps = 0
                quant = canon.get("best_quant")
            fam = {
                "fit": fit_by_memory(mem, ram[stem]),
                "raw_tps": round(tps, 2),
                "scaled_tps": round(tps, 2),  # kept for HTML/docs compat; equals raw
                "mem": mem,
                "variant": canon["name"],
                "quant": quant,
                "chosen_on": canon_cfg,
                "tps_method": "llmfit-profile",
                "bandwidth_gbps": bw[stem],
                "estimate_confidence": (row or {}).get("estimate_confidence"),
            }
            out.setdefault(stem, {})[disp] = fam
        audit[disp] = {"canonical": canon["name"], "chosen_on": canon_cfg, "mem": mem}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n")

    print("canonical picks:")
    for disp, a in audit.items():
        print(f"  {disp:26} {a['chosen_on'] or '-':10} {a['canonical'] or '-'}")
    print("\nfit matrix (fit | llmfit tps @ profile BW):")
    for grp, disp, *_ in FAM:
        row = " ".join(
            f"{out[stem][disp]['fit'][:4]:>4}/{out[stem][disp]['scaled_tps'] or 0:>6.1f}"
            for stem in stems
        )
        print(f"{grp:8} {disp:24} {row}")
    missing = [
        (stem, d)
        for stem in stems
        for d in out[stem]
        if out[stem][d]["fit"] == "Missing"
    ]
    print("MISSING:", missing)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
