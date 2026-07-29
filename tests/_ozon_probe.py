"""Прогон профиля Ozon для §4.2 — только вывод, не тест."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from tests.helpers import silence_app_console
from services.ai_stub import get_offline_result

# Профиль по строке датасета, близкой к ozon.ru (e-commerce, RU+мир, high load)
OZON_ANSWERS = {
    "w2": "ecommerce",
    "w3": "both",
    "w5": "6+",
    "w6": "6+months",
    "w7": "1m+",
    "w8": "20k+",
    "w12": "critical",
    "w13": "responsive",
    "w_fe3": "ssr",
    "w_fe4": "react",
    "w14": "extended",
    "w15": "both",
    "w_be3": "node",
    "w16": "yes",
    "w17": "50-500k",
    "w_ar3": "microservices",
    "w18": "no",
    "w19": "cloud_international",
    "w20": "critical",
    "w_ar6": "yes",
    "w_be8": "fulltext",
    "w_d0": "ecommerce",
    "w4": {"value": "yes", "text": "https://www.ozon.ru"},
}

if __name__ == "__main__":
    t0 = time.perf_counter()
    with silence_app_console():
        r = get_offline_result({"general": OZON_ANSWERS}, "website")
    dt = time.perf_counter() - t0
    print("label:", r["label"])
    print("time_s:", round(dt, 3))
    print("top3:", r["top3"])
    print("stack:", json.dumps(r["stack"], ensure_ascii=False, indent=2))
    print("design_keys:", list(r.get("design", {}).keys()))
