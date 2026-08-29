#!/usr/bin/env python3
"""Compute comfortable internal SSD size per Mac config from llmfit disk_size_gb.

llmfit already publishes on-disk weight size as `disk_size_gb` on every fit row
(see `llmfit info <model> --json` and the `raw/*.json` dumps from
`llmfit --memory … --ram … fit --json`). This script does not guess those
sizes. It only:

1. Looks up a fixed list of canonical Hugging Face model IDs in each config dump
2. Keeps rows that fit (Perfect / Good / Marginal)
3. Applies a documented reserve formula
4. Rounds up to the next Apple SSD SKU

Formula (constants below are policy, not model sizes):
  need_gb = OS_APPS_GB
          + sum(disk_size_gb of the KEEP_N largest fitting blog models)
          + max(those disks)   # download scratch for one more model
  comfortable_ssd = smallest Apple SKU >= need_gb

Usage:
  python3 scripts/disk_comfort.py
  python3 scripts/disk_comfort.py --raw-dir raw --out raw/disk/comfort.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# --- policy constants (not model sizes) ---
OS_APPS_GB = 100.0  # macOS + apps + caches; conservative desk-machine reserve
KEEP_N = 3  # models kept on disk at once for comfortable switching
FIT_OK = {"Perfect", "Good", "Marginal"}

# Apple configure-to-order SSD options used on mini / Studio (GB)
APPLE_SSD_SKUS_GB = (256, 512, 1024, 2048, 4096, 8192, 16384)

# Config dumps produced by llmfit overrides (filename stem -> display)
CONFIGS = [
    ("m6_16", "Entry: Mac mini M6 16GB"),
    ("m6_24", "Compact-: Mac mini M6 24GB"),
    ("m6_32", "Compact: Mac mini M6 32GB"),
    ("m5pro_24", "Pro mini: M5 Pro 24GB"),
    ("m5pro_48", "Pro mini: M5 Pro 48GB"),
    ("m5pro_64", "Pro mini: M5 Pro 64GB"),
    ("m5max36", "Studio Max 36GB"),
    ("m5max48", "Studio Max 48GB"),
    ("m5max64", "Studio Max 64GB"),
    ("m5max128", "Sweet spot: Studio Max 128GB"),
    ("m5ultra96", "Studio Ultra 96GB"),
    ("m5ultra256", "Frontier-adjacent: Studio Ultra 256GB"),
    ("m5ultra512", "Full frontier: Studio Ultra 512GB"),
]

# Canonical HF IDs matching the blog matrix. Prefer upstream orgs.
# disk_size_gb comes from llmfit for the best_quant it picks on that machine.
BLOG_MODELS: list[tuple[str, str]] = [
    ("Kimi K3 2.8T", "moonshotai/Kimi-K3"),
    ("DeepSeek V4-Pro 1.6T", "deepseek-ai/DeepSeek-V4-Pro-0813"),
    ("LongCat 2.0 1.6T", "meituan-longcat/LongCat-2.0"),
    ("Ling 2.6 1T", "inclusionAI/Ling-2.6-1T"),
    ("GLM-5.2 743B", "zai-org/GLM-5.2"),
    ("Nemotron 3 Ultra 550B", "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16"),
    ("Llama 4 Maverick 400B", "meta-llama/Llama-4-Maverick-17B-128E-Instruct"),
    ("Qwen3.5 397B-A17B", "Qwen/Qwen3.5-397B-A17B"),
    ("DeepSeek V4-Flash 284B", "deepseek-ai/DeepSeek-V4-Flash-0731"),
    ("MiniMax M3 427B", "MiniMaxAI/MiniMax-M3"),
    ("Kimi K2.6 1.1T", "moonshotai/Kimi-K2.6"),
    ("Nemotron 3 Super 120B", "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"),
    ("gpt-oss-120b 117B", "openai/gpt-oss-120b"),
    ("Llama 4 Scout 109B", "meta-llama/Llama-4-Scout-17B-16E-Instruct"),
    ("Gemma 4 31B", "google/gemma-4-31B-it"),
    ("Gemma 4 26B-A4B", "google/gemma-4-26B-A4B-it"),
    ("Qwen3.8 27B", "Qwen/Qwen3.8-27B"),
    ("ERNIE 4.5 21B-A3B", "baidu/ERNIE-4.5-21B-A3B-Thinking"),
    ("Granite 4.1 30B", "ibm-granite/granite-4.1-30b"),
    ("Nemotron 3 Nano 30B", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"),
    ("Gemma 4 12B", "unsloth/gemma-4-12b-it"),
    ("gpt-oss-20b 21B", "openai/gpt-oss-20b"),
]


def round_up_apple_ssd(need_gb: float) -> int:
    for sku in APPLE_SSD_SKUS_GB:
        if sku >= need_gb:
            return sku
    return APPLE_SSD_SKUS_GB[-1]


def with_free_headroom(need_gb: float, max_fill: float = 0.85) -> int:
    """Bump one Apple SKU if `need_gb` would fill more than max_fill of the floor SKU."""
    floor = round_up_apple_ssd(need_gb)
    if need_gb / floor <= max_fill:
        return floor
    idx = APPLE_SSD_SKUS_GB.index(floor)
    if idx + 1 < len(APPLE_SSD_SKUS_GB):
        return APPLE_SSD_SKUS_GB[idx + 1]
    return floor


def load_index(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text())
    models = data["models"] if isinstance(data, dict) else data
    return {m["name"]: m for m in models}


def load_index_via_llmfit(memory_gb: int, cpu_cores: int) -> dict[str, dict]:
    """Query llmfit info for each canonical model under a simulated machine.

    Prefer committed raw/*.json dumps when available; this path exists so the
    script can regenerate without multi-megabyte fit dumps in git.
    """
    import subprocess

    index: dict[str, dict] = {}
    for _label, hf_id in BLOG_MODELS:
        cmd = [
            "llmfit",
            f"--memory={memory_gb}G",
            f"--ram={memory_gb}G",
            f"--cpu-cores={cpu_cores}",
            "info",
            hf_id,
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            continue
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue
        models = payload.get("models") or []
        if not models:
            continue
        m = models[0]
        index[m.get("name") or hf_id] = m
        # Also key by requested id so exact lookups work when name matches.
        index[hf_id] = m
    return index


# Memory/CPU for --via-llmfit mode (matches Apple configs used in the blog).
CONFIG_SPECS: dict[str, tuple[int, int]] = {
    "m6_16": (16, 12),
    "m6_24": (24, 12),
    "m6_32": (32, 12),
    "m5pro_24": (24, 15),
    "m5pro_48": (48, 15),
    "m5pro_64": (64, 18),
    "m5max36": (36, 18),
    "m5max48": (48, 18),
    "m5max64": (64, 18),
    "m5max128": (128, 18),
    "m5ultra96": (96, 30),
    "m5ultra256": (256, 30),
    "m5ultra512": (512, 36),
}


def fitting_disks(index: dict[str, dict]) -> list[dict]:
    rows = []
    for label, hf_id in BLOG_MODELS:
        m = index.get(hf_id)
        if m is None:
            rows.append(
                {
                    "label": label,
                    "hf_id": hf_id,
                    "found": False,
                    "fit_level": None,
                    "disk_size_gb": None,
                    "best_quant": None,
                    "memory_required_gb": None,
                }
            )
            continue
        fit = m.get("fit_level")
        disk = m.get("disk_size_gb")
        rows.append(
            {
                "label": label,
                "hf_id": hf_id,
                "found": True,
                "fit_level": fit,
                "disk_size_gb": disk,
                "best_quant": m.get("best_quant"),
                "memory_required_gb": m.get("memory_required_gb"),
                "fits": fit in FIT_OK and disk is not None,
            }
        )
    return rows


def comfort_for_config(rows: list[dict]) -> dict:
    fitting = [r for r in rows if r.get("fits")]
    # Worst-case keep set: the KEEP_N largest on-disk models that fit.
    fitting_sorted = sorted(fitting, key=lambda r: r["disk_size_gb"], reverse=True)
    keep = fitting_sorted[:KEEP_N]
    keep_sum = sum(r["disk_size_gb"] for r in keep)
    scratch = max((r["disk_size_gb"] for r in keep), default=0.0)
    need = OS_APPS_GB + keep_sum + scratch
    return {
        "fitting_count": len(fitting),
        "keep_n": KEEP_N,
        "os_apps_gb": OS_APPS_GB,
        "keep_models": [
            {
                "label": r["label"],
                "hf_id": r["hf_id"],
                "disk_size_gb": r["disk_size_gb"],
                "fit_level": r["fit_level"],
                "best_quant": r["best_quant"],
            }
            for r in keep
        ],
        "keep_sum_gb": round(keep_sum, 2),
        "download_scratch_gb": round(scratch, 2),
        "need_gb": round(need, 2),
        "comfortable_ssd_gb": with_free_headroom(need),
        "floor_ssd_gb": round_up_apple_ssd(need),
        "all_fitting": [
            {
                "label": r["label"],
                "hf_id": r["hf_id"],
                "disk_size_gb": r["disk_size_gb"],
                "fit_level": r["fit_level"],
                "best_quant": r["best_quant"],
            }
            for r in fitting_sorted
        ],
    }


def fmt_ssd(gb: int) -> str:
    if gb >= 1024:
        tb = gb / 1024
        return f"{tb:g}TB" if tb == int(tb) else f"{tb:.1f}TB"
    return f"{gb}GB"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--raw-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "raw",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "raw" / "disk" / "comfort.json",
    )
    ap.add_argument("--md", type=Path, default=None, help="Optional markdown summary path")
    ap.add_argument(
        "--via-llmfit",
        action="store_true",
        help="Query llmfit info live instead of reading raw/*.json dumps",
    )
    args = ap.parse_args()

    report = {
        "source": (
            "llmfit info --json (live)"
            if args.via_llmfit
            else "llmfit disk_size_gb from raw/* fit JSON dumps"
        ),
        "formula": (
            f"need_gb = {OS_APPS_GB:g} (OS/apps) + sum(top {KEEP_N} fitting "
            f"disk_size_gb) + max(those) download scratch; "
            "round up to Apple SSD SKU; if that SKU would be >85% full, bump one tier"
        ),
        "fit_levels_counted": sorted(FIT_OK),
        "models": [{"label": a, "hf_id": b} for a, b in BLOG_MODELS],
        "configs": {},
    }

    missing_files = []
    for stem, title in CONFIGS:
        if args.via_llmfit:
            mem, cores = CONFIG_SPECS[stem]
            print(f"llmfit {stem} ({mem}G, {cores} cores)…", file=sys.stderr)
            index = load_index_via_llmfit(mem, cores)
            source_file = f"llmfit info --memory={mem}G --cpu-cores={cores}"
        else:
            path = args.raw_dir / f"{stem}.json"
            if not path.exists():
                missing_files.append(str(path))
                continue
            index = load_index(path)
            source_file = path.name
        rows = fitting_disks(index)
        comfort = comfort_for_config(rows)
        report["configs"][stem] = {
            "title": title,
            "source_file": source_file,
            **comfort,
            "model_rows": rows,
        }

    if missing_files:
        print("Missing raw dumps:", *missing_files, sep="\n  ", file=sys.stderr)
        print(
            "Hint: pass --via-llmfit to query llmfit live, or point --raw-dir at fit JSON dumps.",
            file=sys.stderr,
        )
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")

    md_path = args.md or args.out.with_suffix(".md")
    lines = [
        "# Comfortable SSD sizes (from llmfit `disk_size_gb`)",
        "",
        report["formula"] + ".",
        "",
        "| Config | Fitting blog models | Keep set (largest 3) | Need (GB) | Floor SSD | Comfortable SSD |",
        "|---|---:|---|---:|---|---|",
    ]
    for stem, title in CONFIGS:
        c = report["configs"][stem]
        keep = ", ".join(
            f"{k['label']} ({k['disk_size_gb']:.1f}GB)" for k in c["keep_models"]
        ) or "—"
        lines.append(
            f"| {title} (`{stem}`) | {c['fitting_count']} | {keep} | "
            f"{c['need_gb']:.0f} | {fmt_ssd(c['floor_ssd_gb'])} | "
            f"**{fmt_ssd(c['comfortable_ssd_gb'])}** |"
        )
    lines += [
        "",
        "## Per-model disk sizes on Ultra 512GB dump",
        "",
        "Taken from `m5ultra512.json` (llmfit best_quant for that machine).",
        "",
        "| Model | HF ID | disk_size_gb | fit | quant |",
        "|---|---|---:|---|---|",
    ]
    for r in report["configs"]["m5ultra512"]["model_rows"]:
        disk = f"{r['disk_size_gb']:.2f}" if r.get("disk_size_gb") is not None else "—"
        lines.append(
            f"| {r['label']} | `{r['hf_id']}` | {disk} | {r.get('fit_level') or 'missing'} | "
            f"{r.get('best_quant') or '—'} |"
        )
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n")

    # stdout summary for humans / CI
    print(f"Wrote {args.out}")
    print(f"Wrote {md_path}")
    print()
    for stem, title in CONFIGS:
        c = report["configs"][stem]
        print(
            f"{stem:12}  need={c['need_gb']:8.1f}GB  "
            f"floor={fmt_ssd(c['floor_ssd_gb']):6}  "
            f"comfortable={fmt_ssd(c['comfortable_ssd_gb'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
