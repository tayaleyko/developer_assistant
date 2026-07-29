"""Проверка URL для online-анализа site_analyzer."""
import io
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from services.site_analyzer import analyze_site, extract_palette, is_online_available

CANDIDATES = [
    "https://productradar.ru",
    "https://vas3k.club",
    "https://bejamas.com",
    "https://www.magicpatterns.com",
    "https://bento.me",
    "https://www.uxhub.ru",
    "https://www.carbonmade.com",
    "https://www.read.cv",
    "https://www.patterns.dev",
    "https://www.joshwcomeau.com",
    "https://www.typedream.com",
    "https://www.lottiefiles.com",
    "https://www.hyperui.com",
    "https://www.polar.sh",
    "https://www.cal.com",
    "https://www.cult-ui.com",
    "https://www.svgrepo.com",
    "https://www.kodik.info",
    "https://www.itmo.ru",
    "https://www.spbstu.ru",
    "https://radar.tech",
    "https://www.stitcher.io",
    "https://photopea.com",
    "https://www.carbon.ai",
    "https://www.shadcnblocks.com",
    "https://www.originui.com",
    "https://www.kibo-ui.com",
    "https://www.magicui.design",
]

if __name__ == "__main__":
    print("online:", is_online_available(), "\n")
    for url in CANDIDATES:
        r = analyze_site(url)
        if "error" in r:
            print("FAIL", url, "->", r["error"][:100])
            print()
            continue
        tech = r["technologies"]
        design = r["design"]
        fw = tech.get("Фреймворк", "?")
        ui = design.get("UI-библиотека", "?")
        nav = design.get("Тип навигации", "?")
        fonts = design.get("Шрифты", "?")
        pal = extract_palette(url)
        score = sum([
            fw != "Не определён",
            ui != "Не определена",
            "Не определена" not in nav,
            fonts != "Не определены",
            len(pal) >= 3,
        ])
        print(f"SCORE {score}/5 | {url}")
        print(f"  fw={fw} | backend={tech.get('Backend')} | hosting={tech.get('Хостинг')}")
        print(f"  ui={ui}")
        print(f"  nav={nav[:70]}")
        print(f"  fonts={fonts[:60]}")
        print(f"  analytics={tech.get('Аналитика')}")
        print(f"  palette({len(pal)})={pal}")
        print()
