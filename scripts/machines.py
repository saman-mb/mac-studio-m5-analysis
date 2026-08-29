"""Shared Apple SKU table for llmfit --profile simulations."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACHINES_PATH = Path(__file__).with_name("machines.json")
PROFILES_DIR = ROOT / "profiles"
DEFAULT_RAW_DIR = ROOT / "raw" / "sims"


def load_machines() -> list[dict]:
    data = json.loads(MACHINES_PATH.read_text())
    return data["machines"]


def profile_path(stem: str) -> Path:
    return PROFILES_DIR / f"{stem}.json"
