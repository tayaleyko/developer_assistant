from __future__ import annotations
import json
from pathlib import Path

PROGRESS_FILE = Path(__file__).resolve().parent.parent / "progress.json"


def save_progress(state: dict):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_progress() -> dict | None:
    if not PROGRESS_FILE.exists():
        return None
    with open(PROGRESS_FILE, encoding="utf-8") as f:
        return json.load(f)
