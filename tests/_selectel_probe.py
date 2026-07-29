"""Прогон профиля Selectel для §4.2."""
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

SELECTEL_ANSWERS = {
    "w1": "commercial",
    "w2": "corporate",
    "w3": "russia",
    "w4": {"value": "yes", "text": "https://www.selectel.ru"},
    "w5": "6+",
    "w6": "6+months",
    "w7": "1m+",
    "w8": "20k+",
    "w12": "critical",
    "w13": "responsive",
    "w_fe3": "ssr",
    "w_fe4": "react",
    "w14": "extended",
    "w15": "russia",
    "w_be3": "node",
    "w16": "yes",
    "w17": "50-500k",
    "w_ar3": "microservices",
    "w18": "yes",
    "w19": "cloud_russia",
    "w20": "critical",
    "w_ar6": "yes",
    "w_be8": "fulltext",
    "w_d0": "tech",
    "w_d4": {"value": "yes", "text": "https://www.selectel.ru"},
}

if __name__ == "__main__":
    answers = {"blocks": SELECTEL_ANSWERS}
    t0 = time.perf_counter()
    with silence_app_console():
        offline = get_offline_result(answers, "website")
    print("=== OFFLINE ===")
    print("label:", offline["label"])
    print("time_s:", round(time.perf_counter() - t0, 3))
    print("top3:", offline["top3"])
    print("stack:", json.dumps(offline["stack"], ensure_ascii=False, indent=2))
    print("design:", json.dumps(offline["design"], ensure_ascii=False, indent=2))

    t0 = time.perf_counter()
    with silence_app_console():
        online = get_online_result(answers, "website")
    print("\n=== ONLINE ===")
    print("time_s:", round(time.perf_counter() - t0, 3))
    print("error:", online.get("error"))
    print("palette:", online.get("palette"))
    if online.get("site_analysis"):
        print(json.dumps(online["site_analysis"], ensure_ascii=False, indent=2))
