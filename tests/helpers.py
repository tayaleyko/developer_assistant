"""Общие пути и фикстуры для тестов."""
from __future__ import annotations

import io
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
MODEL_DIR = ROOT / "models"
QUESTIONS_PATH = ROOT / "questions.json"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


SAMPLE_WEBSITE_ANSWERS = {
    "w2": "landing",
    "w3": "russia",
    "w5": "1",
    "w6": "1month",
    "w7": "50k",
    "w8": "1k",
    "w12": "no",
    "w13": "no",
    "w_fe3": "ssg",
    "w_fe4": "react",
    "w14": "no",
    "w15": "no",
    "w_be3": "unknown",
    "w16": "no",
    "w17": "1k",
    "w_ar3": "monolith",
    "w18": "no",
    "w19": "simple",
    "w20": "no",
    "w_ar6": "no",
    "w_be8": "no",
    "w_d0": "commercial",
}

NESTED_ANSWERS = {
    "general": {
        "w2": "landing",
        "w4": {"value": "yes", "text": "https://example.com"},
    },
    "design": {
        "w_d0": "commercial",
    },
}


@contextmanager
def silence_app_console():
    """Подавить вывод модулей, пишущих в sys.__stdout__ (MLP, online)."""
    backup = sys.__stdout__
    sys.__stdout__ = io.StringIO()
    try:
        yield
    finally:
        sys.__stdout__ = backup
