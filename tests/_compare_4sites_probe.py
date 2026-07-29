"""Сравнение 4 эталонных сайтов: selectel, netology, tilda, tinkoff."""
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
from services.site_analyzer import analyze_site, extract_palette

PROFILES = {
    "selectel": {
        "url": "https://www.selectel.ru",
        "name": "Selectel (облачный провайдер B2B)",
        "answers": {
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
        },
    },
    "netology": {
        "url": "https://www.netology.ru",
        "name": "Нетология (EdTech / SaaS)",
        "answers": {
            "w1": "commercial",
            "w2": "saas",
            "w3": "russia",
            "w4": {"value": "yes", "text": "https://www.netology.ru"},
            "w5": "6+",
            "w6": "6+months",
            "w7": "1m+",
            "w8": "20k+",
            "w12": "critical",
            "w13": "responsive",
            "w_fe3": "spa",
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
            "w_d0": "education",
            "w_d4": {"value": "yes", "text": "https://www.netology.ru"},
        },
    },
    "tilda": {
        "url": "https://www.tilda.cc",
        "name": "Tilda (конструктор сайтов / SaaS)",
        "answers": {
            "w1": "commercial",
            "w2": "saas",
            "w3": "both",
            "w4": {"value": "yes", "text": "https://www.tilda.cc"},
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
            "w18": "yes",
            "w19": "cloud_international",
            "w20": "critical",
            "w_ar6": "yes",
            "w_be8": "fulltext",
            "w_d0": "tech",
            "w_d4": {"value": "yes", "text": "https://www.tilda.cc"},
        },
    },
    "tinkoff": {
        "url": "https://www.tinkoff.ru",
        "name": "Т-Банк (финтех / корпоративный)",
        "answers": {
            "w1": "commercial",
            "w2": "corporate",
            "w3": "russia",
            "w4": {"value": "yes", "text": "https://www.tinkoff.ru"},
            "w5": "6+",
            "w6": "6+months",
            "w7": "1m+",
            "w8": "20k+",
            "w12": "critical",
            "w13": "responsive",
            "w_fe3": "spa",
            "w_fe4": "react",
            "w14": "extended",
            "w15": "russia",
            "w_be3": "java",
            "w16": "yes",
            "w17": "500k+",
            "w_ar3": "microservices",
            "w18": "yes",
            "w19": "cloud_russia",
            "w20": "critical",
            "w_ar6": "yes",
            "w_be8": "fulltext",
            "w_d0": "finance",
            "w_d4": {"value": "yes", "text": "https://www.tinkoff.ru"},
        },
    },
}


def analyzer_score(tech, design, palette):
    return sum([
        tech.get("Фреймворк") != "Не определён",
        tech.get("Backend") != "Не определён",
        design.get("UI-библиотека") != "Не определена",
        "Не определена" not in design.get("Тип навигации", ""),
        design.get("Шрифты") != "Не определены",
        len(palette) >= 3,
        tech.get("Аналитика") != "Не обнаружена",
    ])


if __name__ == "__main__":
    results = []
    for key, prof in PROFILES.items():
        url = prof["url"]
        print("=" * 70)
        print(prof["name"], url)
        print("=" * 70)

        ar = analyze_site(url)
        if "error" in ar:
            print("ANALYZER FAIL:", ar["error"])
            results.append({"key": key, "fail": True, "error": ar["error"]})
            print()
            continue

        tech = ar["technologies"]
        design = ar["design"]
        pal = extract_palette(url)
        a_score = analyzer_score(tech, design, pal)

        answers = {"blocks": prof["answers"]}
        t0 = time.perf_counter()
        with silence_app_console():
            offline = get_offline_result(answers, "website")
        off_t = time.perf_counter() - t0

        t0 = time.perf_counter()
        with silence_app_console():
            online = get_online_result(answers, "website")
        on_t = time.perf_counter() - t0

        row = {
            "key": key,
            "name": prof["name"],
            "url": url,
            "analyzer_score": a_score,
            "tech": tech,
            "design": design,
            "palette": pal,
            "offline_label": offline["label"],
            "offline_p": offline["top3"][0][1],
            "offline_time": round(off_t, 3),
            "offline_top3": offline["top3"],
            "online_label": online["label"],
            "online_error": online.get("error"),
            "online_time": round(on_t, 3),
            "online_palette": online.get("palette", []),
            "offline_design_keys": list(offline.get("design", {}).keys()),
            "offline_stack": offline.get("stack", {}),
        }
        results.append(row)

        print(f"analyzer_score: {a_score}/7")
        print(f"offline: {offline['label']} p={offline['top3'][0][1]:.3f} t={off_t:.3f}s")
        print(f"online:  error={online.get('error')} t={on_t:.3f}s palette={len(online.get('palette') or [])}")
        print(json.dumps({"tech": tech, "design": design, "palette": pal}, ensure_ascii=False, indent=2))
        print()

    out_path = ROOT / "docs" / "chapter4" / "_compare_4sites.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("Saved:", out_path)
