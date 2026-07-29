"""Массовая проверка URL для site_analyzer — только статус и score."""
import io
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from services.site_analyzer import analyze_site, extract_palette, is_online_available

# РФ / СНГ — нишевые
RU = [
    "https://productradar.ru",
    "https://vas3k.club",
    "https://www.itmo.ru",
    "https://www.spbstu.ru",
    "https://www.hse.ru",
    "https://www.courson.ru",
    "https://www.skillbox.ru",
    "https://www.netology.ru",
    "https://www.tilda.cc",
    "https://www.nethouse.ru",
    "https://www.reg.ru",
    "https://www.timeweb.com",
    "https://www.selectel.ru",
    "https://www.cnews.ru",
    "https://www.ixbt.com",
    "https://www.opennet.ru",
    "https://www.linux.org.ru",
    "https://www.pikabu.ru",
    "https://www.drive2.ru",
    "https://www.championat.com",
    "https://www.sports.ru",
    "https://www.afisha.ru",
    "https://www.kinopoisk.ru",
    "https://www.litres.ru",
    "https://www.labirint.ru",
    "https://www.citilink.ru",
    "https://www.mvideo.ru",
    "https://www.dns-shop.ru",
    "https://www.sberbank.ru",
    "https://www.tinkoff.ru",
    "https://www.raiffeisen.ru",
    "https://www.vc.ru",
    "https://www.rbc.ru",
    "https://www.kommersant.ru",
    "https://www.gazeta.ru",
    "https://www.changelog.ru",
    "https://www.dev.by",
    "https://www.habr.com",
]

# Dev / UI — менее медийные
DEV = [
    "https://bejamas.com",
    "https://www.magicpatterns.com",
    "https://bento.me",
    "https://www.carbonmade.com",
    "https://www.patterns.dev",
    "https://www.joshwcomeau.com",
    "https://www.typedream.com",
    "https://www.polar.sh",
    "https://www.cal.com",
    "https://www.cult-ui.com",
    "https://www.magicui.design",
    "https://www.kibo-ui.com",
    "https://www.shadcnblocks.com",
    "https://www.stitcher.io",
    "https://www.learn-clojurescript.com",
    "https://www.refactoringui.com",
    "https://www.smashingmagazine.com",
    "https://www.css-tricks.com",
    "https://www.web.dev",
    "https://www.magicui.design",
    "https://ui.shadcn.com",
    "https://www.radix-ui.com",
    "https://www.framer.com",
    "https://www.webstudio.is",
    "https://www.superlist.com",
    "https://www.paper.design",
    "https://www.raycast.com",
    "https://www.tweakcn.com",
    "https://www.originui.com",
    "https://www.hyperui.com",
    "https://www.lottiefiles.com",
    "https://www.svgrepo.com",
    "https://www.read.cv",
    "https://photopea.com",
    "https://www.uxhub.ru",
    "https://radar.tech",
    "https://www.carbon.ai",
]

CANDIDATES = list(dict.fromkeys(RU + DEV))  # unique, preserve order


def score_result(r, url):
    tech = r["technologies"]
    design = r["design"]
    pal = extract_palette(url)
    s = sum([
        tech.get("Фреймворк") != "Не определён",
        design.get("UI-библиотека") != "Не определена",
        "Не определена" not in design.get("Тип навигации", ""),
        design.get("Шрифты") != "Не определены",
        len(pal) >= 3,
    ])
    return s, pal, tech, design


if __name__ == "__main__":
    print("online:", is_online_available())
    print(f"checking {len(CANDIDATES)} URLs...\n")

    ok = []
    fail = []

    for url in CANDIDATES:
        r = analyze_site(url)
        if "error" in r:
            err = r["error"]
            if "403" in err:
                reason = "403"
            elif "429" in err:
                reason = "429"
            elif "402" in err:
                reason = "402"
            elif "Connection" in err or "timeout" in err.lower():
                reason = "network"
            else:
                reason = "other"
            fail.append((url, reason, err[:80]))
            continue
        s, pal, tech, design = score_result(r, url)
        ok.append({
            "url": url,
            "score": s,
            "fw": tech.get("Фреймворк"),
            "backend": tech.get("Backend"),
            "hosting": tech.get("Хостинг"),
            "ui": design.get("UI-библиотека"),
            "nav": design.get("Тип навигации", "")[:50],
            "analytics": tech.get("Аналитика"),
            "palette_n": len(pal),
        })

    print("=" * 70)
    print(f"OK: {len(ok)}  |  FAIL: {len(fail)}")
    print("=" * 70)

    print("\n--- УСПЕШНЫЕ (по score) ---")
    for x in sorted(ok, key=lambda i: (-i["score"], i["url"])):
        print(f"{x['score']}/5 | {x['url']}")
        print(f"       fw={x['fw']} | be={x['backend']} | host={x['hosting']} | ui={x['ui']}")
        print(f"       nav={x['nav']} | pal={x['palette_n']} | analytics={x['analytics']}")

    print("\n--- ОТКАЗЫ ---")
    for url, reason, err in fail:
        print(f"{reason:8} | {url}")
        print(f"         {err}")
