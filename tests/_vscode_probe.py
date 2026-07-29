"""Прогон профиля Visual Studio Code для §4.2."""
import io
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from tests.helpers import silence_app_console
from services.ai_stub import get_offline_result

# По строке датасета editor + electron (row 18) + сфера tech для дизайна
VSCODE_ANSWERS = {
    "d2": "editor",
    "d3": ["windows", "macos", "linux"],
    "d4": "both",
    "d5": {"value": "yes", "text": "Visual Studio Code / code.visualstudio.com"},
    "d6": "2-5",
    "d7": "3-6months",
    "d8": "100-500k",
    "d13": "full",
    "d14": "moderate",
    "d15": "filesystem",
    "d_fe4": "electron",
    "d16": "no",
    "d17": "basic",
    "d18": "no",
    "d19": "yes",
    "d_ar3": "yes",
    "d_ar5": "no",
    "d_fe8": "yes",
    "d_fe9": "yes",
    "d_ar7": "no",
    "d_h8": "no",
    "d_h10": "no",
    "d_d0": "tech",
    "d_d2": {"value": "yes", "text": "#007ACC, #1E1E1E, #252526"},
    "d_d3": "custom",
    "d_d5": "sidebar",
    "d_d6": "yes",
    "d_d7": "subtle",
    "d_d8": "yes",
    "d_d9": "yes",
}

if __name__ == "__main__":
    t0 = time.perf_counter()
    with silence_app_console():
        r = get_offline_result({"blocks": VSCODE_ANSWERS}, "desktop")
    dt = time.perf_counter() - t0
    print("label:", r["label"])
    print("time_s:", round(dt, 3))
    print("top3:", r["top3"])
    print("\n--- stack ---")
    print(json.dumps(r["stack"], ensure_ascii=False, indent=2))
    print("\n--- design ---")
    print(json.dumps(r["design"], ensure_ascii=False, indent=2))
