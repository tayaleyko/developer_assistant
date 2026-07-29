"""Прогон профиля productradar.ru для §4.2 (online-анализ сайта)."""
import io
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from tests.helpers import silence_app_console
from services.ai_stub import get_offline_result, get_online_result

URL = "https://productradar.ru"

# Каталог стартапов: лендинг/витрина, РФ, PHP-контур, Tailwind, аналог в w4
PRODUCTRADAR_ANSWERS = {
    "w1": "commercial",
    "w2": "landing",
    "w3": "russia",
    "w4": {"value": "yes", "text": URL},
    "w5": "2-5",
    "w6": "1-3months",
    "w7": "100-500k",
    "w8": "5k",
    "w12": "important",
    "w13": "responsive",
    "w_fe3": "ssr",
    "w_fe4": "unknown",
    "w14": "no",
    "w15": "no",
    "w_be3": "php",
    "w16": "no",
    "w17": "1-50k",
    "w_ar3": "monolith",
    "w18": "no",
    "w19": "cloud_russia",
    "w20": "prefer",
    "w_ar6": "no",
    "w_be8": "no",
    "w_d0": "tech",
    "w_d4": {"value": "yes", "text": URL},
    "w_d2": {"value": "select"},
    "w_d5": {"value": "yes", "text": URL},
    "w_d6": "corporate",
    "w_d8": "horizontal",
    "w_d9": "optional",
    "w_d10": "subtle",
    "w_d11": "nice",
    "w_d12": "yes",
}

if __name__ == "__main__":
    answers = {"blocks": PRODUCTRADAR_ANSWERS}

    t0 = time.perf_counter()
    with silence_app_console():
        offline = get_offline_result(answers, "website")
    offline_dt = time.perf_counter() - t0

    print("=== OFFLINE ===")
    print("label:", offline["label"])
    print("time_s:", round(offline_dt, 3))
    print("top3:", offline["top3"])

    t0 = time.perf_counter()
    with silence_app_console():
        online = get_online_result(answers, "website")
    online_dt = time.perf_counter() - t0

    print("\n=== ONLINE ===")
    print("label:", online["label"])
    print("time_s:", round(online_dt, 3))
    print("error:", online.get("error"))
    print("palette:", online.get("palette"))
    if online.get("site_analysis"):
        print("\n--- site_analysis ---")
        print(json.dumps(online["site_analysis"], ensure_ascii=False, indent=2))
