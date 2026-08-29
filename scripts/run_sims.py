#!/usr/bin/env python3
"""Run llmfit fit --json for every Apple SKU via --profile (no BW post-scale).

Requires a llmfit build that supports hardware profiles (PR #971 / issue #969).

Usage:
  python3 scripts/run_sims.py
  python3 scripts/run_sims.py --out-dir raw/sims --only m5max128,m6_16
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from machines import DEFAULT_RAW_DIR, load_machines, profile_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_RAW_DIR)
    ap.add_argument("--llmfit", default=shutil.which("llmfit") or "llmfit")
    ap.add_argument("--only", default="", help="Comma-separated stems to run")
    args = ap.parse_args()

    # Fail fast if this llmfit is too old for --profile.
    probe = subprocess.run(
        [args.llmfit, "hardware", "list"],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        print(
            "error: llmfit has no `hardware` subcommand — install a build with "
            "PR #971 profiles (e.g. the local release from llmfit--issue-969).",
            file=sys.stderr,
        )
        return 1

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    machines = load_machines()
    if only:
        machines = [m for m in machines if m["stem"] in only]
        missing = only - {m["stem"] for m in machines}
        if missing:
            print(f"error: unknown stems: {sorted(missing)}", file=sys.stderr)
            return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    failures = 0

    for m in machines:
        stem = m["stem"]
        prof = profile_path(stem)
        out = args.out_dir / f"{stem}.json"
        err = args.out_dir / f"{stem}.err"
        cmd = [
            args.llmfit,
            "--profile",
            str(prof),
            "fit",
            "--json",
        ]
        print(
            f"{stem}: ram={m['ram_gb']}G bw={m['bandwidth_gbps']}GB/s → {out.name}",
            flush=True,
        )
        with out.open("w") as stdout, err.open("w") as stderr:
            proc = subprocess.run(cmd, stdout=stdout, stderr=stderr, check=False)
        if proc.returncode != 0 or out.stat().st_size < 1000:
            print(f"  FAIL ec={proc.returncode} stderr={err.read_text()[:300]!r}", flush=True)
            failures += 1
            continue

        data = json.loads(out.read_text())
        models = data.get("models") or []
        bw = None
        if models:
            bw = (models[0].get("estimate_basis") or {}).get("gpu_bandwidth_gbps")
        if bw != m["bandwidth_gbps"]:
            print(
                f"  FAIL expected bw={m['bandwidth_gbps']}, got {bw}",
                flush=True,
            )
            failures += 1
            continue
        print(f"  ok models={len(models)} bw={bw}", flush=True)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
