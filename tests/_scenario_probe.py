import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from tests.helpers import SAMPLE_WEBSITE_ANSWERS, silence_app_console
from services.ai_stub import get_offline_result

SCENARIOS = {
    "S1": ("website", dict(SAMPLE_WEBSITE_ANSWERS)),
    "S2": ("website", {
        "w2": "ecommerce", "w3": "russia", "w5": "100+", "w6": "6months+",
        "w7": "300k+", "w8": "50k+", "w12": "yes", "w13": "responsive",
        "w_fe3": "ssr", "w_fe4": "react", "w14": "yes", "w15": "yes",
        "w_be3": "rest", "w16": "yes", "w17": "50k+", "w_ar3": "microservices",
        "w18": "yes", "w19": "complex", "w20": "yes", "w_ar6": "yes", "w_be8": "yes",
        "w_d0": "commercial",
    }),
    "S3": ("website", {
        "w2": "saas", "w3": "both", "w5": "100+", "w6": "6months+",
        "w7": "300k+", "w8": "50k+", "w12": "yes", "w13": "adaptive",
        "w_fe3": "spa", "w_fe4": "react", "w14": "yes", "w15": "yes",
        "w_be3": "rest", "w16": "yes", "w17": "100k+", "w_ar3": "microservices",
        "w18": "yes", "w19": "complex", "w20": "yes", "w_ar6": "yes", "w_be8": "yes",
        "w_d0": "tech",
    }),
    "S4": ("desktop", {
        "d2": "corporate", "d3": "windows", "d4": "yes", "d5": "no",
        "d6": "3-6months", "d7": "300k+", "d8": "100+", "d9": "yes",
        "d10": "complex", "d11": "yes", "d12": "server", "d13": "yes",
        "d14": "yes", "d_d0": "finance",
    }),
}

if __name__ == "__main__":
    for sid, (ptype, answers) in SCENARIOS.items():
        t0 = time.perf_counter()
        with silence_app_console():
            r = get_offline_result({"block": answers}, ptype)
        dt = time.perf_counter() - t0
        print(
            sid, ptype, r["label"], f"{dt:.3f}s",
            "stack_keys", len(r.get("stack", {})),
            "design_keys", len(r.get("design", {})),
            "top1", r["top3"][0] if r.get("top3") else None,
        )
