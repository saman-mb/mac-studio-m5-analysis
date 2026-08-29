#!/usr/bin/env python3
"""Deprecated — use scripts/build_matrix.py (forwards argv)."""

from __future__ import annotations

import sys
from pathlib import Path

print(
    "note: raw/build_matrix3.py is deprecated; forwarding to scripts/build_matrix.py",
    file=sys.stderr,
)
target = Path(__file__).resolve().parents[1] / "scripts" / "build_matrix.py"
sys.path.insert(0, str(target.parent))
sys.argv[0] = str(target)
import build_matrix  # noqa: E402

raise SystemExit(build_matrix.main())
