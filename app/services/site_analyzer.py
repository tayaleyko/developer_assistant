import re
import sys
import numpy as np

try:
    import requests
    from bs4 import BeautifulSoup
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    _HAS_ONLINE = True
except ImportError:
    _HAS_ONLINE = False

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def is_online_available():
    if not _HAS_ONLINE:
        return False
    try:
        requests.get("https://ya.ru", timeout=3)
        return True
    except Exception:
        return False


def _detect_technologies(soup, html, headers):
    result = {}

    if "__NEXT_DATA__" in html or "/_next/" in html:
        result["Фреймворк"] = "Next.js (React)"
    elif "__NUXT__" in html or "/_nuxt/" in html:
        result["Фреймворк"] = "Nuxt.js (Vue)"
    elif re.search(r'ng-version', html):
        result["Фреймворк"] = "Angular"
    elif "react" in html.lower() and ("reactDOM" in html or "react-dom" in html):
        result["Фреймворк"] = "React"
    elif re.search(r'Vue\.js|vue\.min\.js|vue\.global', html):
        result["Фреймворк"] = "Vue.js"
    else:
        result["Фреймворк"] = "Не определён"

    powered = headers.get("X-Powered-By", "")
    server = headers.get("Server", "")
    if "PHP" in powered:
        result["Backend"] = "PHP"
    elif "Express" in powered:
        result["Backend"] = "Node.js (Express)"
    elif "ASP.NET" in powered or "ASP.NET" in server:
        result["Backend"] = ".NET (ASP.NET)"
    elif "gunicorn" in server.lower() or "uvicorn" in server.lower():
        result["Backend"] = "Python"
    elif "next" in server.lower() or "vercel" in server.lower():
        result["Backend"] = "Node.js (Next.js API)"
    else:
        result["Backend"] = "Не определён"

    result["БД"] = "Не определяется из HTML (зависит от бэкенда)"

    h_str = str(headers).lower()
    if "cloudflare" in h_str:
        result["CDN"] = "Cloudflare"
    elif "fastly" in h_str:
        result["CDN"] = "Fastly"
    elif "akamai" in h_str:
        result["CDN"] = "Akamai"
    elif "cdn" in h_str:
        result["CDN"] = "Присутствует (провайдер не определён)"
    else:
        result["CDN"] = "Не обнаружен"

    if "vercel" in h_str:
        result["Хостинг"] = "Vercel"
    elif "netlify" in h_str:
        result["Хостинг"] = "Netlify"
    elif "amazonaws" in h_str:
        result["Хостинг"] = "AWS"
    elif "google" in h_str:
        result["Хостинг"] = "Google Cloud"
    else:
        result["Хостинг"] = "Не определён"

    analytics = []
    if "google-analytics" in html or "gtag(" in html or "ga.js" in html:
        analytics.append("Google Analytics")
    if "metrika" in html or "mc.yandex" in html:
        analytics.append("Яндекс.Метрика")
    if "hotjar" in html:
        analytics.append("Hotjar")
    if "amplitude" in html.lower():
        analytics.append("Amplitude")
    result["Аналитика"] = ", ".join(analytics) if analytics else "Не обнаружена"

    payments = []
    if "yookassa" in html.lower() or "kassa.yandex" in html.lower():
        payments.append("ЮКасса")
    if "stripe" in html.lower() and "js.stripe.com" in html.lower():
        payments.append("Stripe")
    if "paypal" in html.lower():
        payments.append("PayPal")
    if "tinkoff" in html.lower() and "securepay" in html.lower():
        payments.append("Тинькофф Оплата")
    result["Платёжная система"] = ", ".join(payments) if payments else "Не обнаружена"

    return result


def _analyze_design(soup, html):
    result = {}

    fonts = set()
    for link in soup.find_all("link", href=True):
        if "fonts.googleapis.com" in link["href"]:
            for m in re.findall(r"family=([^&:]+)", link["href"]):
                fonts.add(m.replace("+", " "))
    for style in soup.find_all("style"):
        for m in re.findall(r"font-family:\s*[\"']?([^;\"'}\n]+)", style.string or ""):
            font_name = m.strip().strip("'\"").split(",")[0].strip()
            if font_name and len(font_name) < 40:
                fonts.add(font_name)
    result["Шрифты"] = ", ".join(sorted(fonts)) if fonts else "Не определены"

    all_classes = []
    for tag in soup.find_all(class_=True):
        cls = tag.get("class", [])
        if isinstance(cls, list):
            all_classes.extend(cls)
        else:
            all_classes.append(str(cls))
    classes_str = " ".join(all_classes)

    if "ant-" in classes_str:
        result["UI-библиотека"] = "Ant Design"
    elif "Mui" in classes_str or "css-" in classes_str and "MuiButton" in html:
        result["UI-библиотека"] = "Material UI (MUI)"
    elif "chakra-" in classes_str:
        result["UI-библиотека"] = "Chakra UI"
    elif "btn-primary" in classes_str or "container" in classes_str and "bootstrap" in html.lower():
        result["UI-библиотека"] = "Bootstrap"
    elif "tailwind" in html.lower() or re.search(r'class="[^"]*\b(flex|grid|px-|py-|bg-|text-)\b', html):
        result["UI-библиотека"] = "Tailwind CSS"
    else:
        result["UI-библиотека"] = "Не определена"

    nav = soup.find("nav") or soup.find("header")
    if nav:
        count = len(nav.find_all("a"))
        if count > 10:
            result["Тип навигации"] = f"Расширенная навигация / мегаменю ({count} ссылок)"
        elif count > 0:
            result["Тип навигации"] = f"Стандартное горизонтальное меню ({count} пунктов)"
        else:
            result["Тип навигации"] = "Минималистичная навигация"
    else:
        result["Тип навигации"] = "Не определена (элемент <nav> не найден)"

    script_str = " ".join(s.get("src", "") for s in soup.find_all("script", src=True)).lower()
    anim_libs = []
    if "gsap" in script_str:
        anim_libs.append("GSAP")
    if "aos" in script_str or "aos.js" in html.lower():
        anim_libs.append("AOS")
    if "framer-motion" in script_str:
        anim_libs.append("Framer Motion")
    if "lottie" in script_str:
        anim_libs.append("Lottie")
    result["Анимации"] = ", ".join(anim_libs) if anim_libs else "Не обнаружены"

    result["Структура"] = "Требуется анализ sitemap.xml"

    return result


def analyze_site(url):
    if not _HAS_ONLINE:
        return {"error": "Библиотеки requests / beautifulsoup4 не установлены"}

    if not url.startswith("http"):
        url = "https://" + url

    try:
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=10, allow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        return {"error": f"Не удалось загрузить {url}: {e}"}

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    return {
        "technologies": _detect_technologies(soup, html, resp.headers),
        "design": _analyze_design(soup, html),
    }


def _extract_colors_from_html(html):
    colors = [m.lower() for m in re.findall(r"#([0-9a-fA-F]{6})\b", html)]
    for m in re.findall(r"#([0-9a-fA-F]{3})\b", html):
        colors.append((m[0] * 2 + m[1] * 2 + m[2] * 2).lower())
    for r, g, b in re.findall(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", html):
        colors.append(f"{int(r):02x}{int(g):02x}{int(b):02x}")
    return colors


def _hex_to_rgb(hex_color):
    return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]


def _rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def _brightness(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def extract_palette(url, n_clusters=5):
    if not _HAS_ONLINE:
        return []

    if not url.startswith("http"):
        url = "https://" + url

    out = sys.__stdout__
    try:
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"[palette] {url} вернул HTTP {resp.status_code}, палитра пропущена", file=out)
            return []
        html = resp.text
    except Exception as e:
        print(f"[palette] Ошибка загрузки {url}: {e}", file=out)
        return []

    colors = _extract_colors_from_html(html)
    if len(colors) < n_clusters:
        return [f"#{c}" for c in colors]

    # чёрный и белый встречаются почти везде и только зашумляют кластеры
    colors = [c for c in colors if c not in ("000000", "ffffff")]
    if len(colors) < n_clusters:
        return [f"#{c}" for c in colors]

    rgb_array = np.array([_hex_to_rgb(c) for c in colors], dtype=float)

    kmeans = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        random_state=42,
    )
    kmeans.fit(rgb_array)

    sil = silhouette_score(rgb_array, kmeans.labels_)
    print(f"\n{'='*60}", file=out)
    print(f"  KMeans — палитра цветов ({url})", file=out)
    print(f"{'='*60}", file=out)
    print("  Пространство:     RGB (Euclidean)", file=out)
    print("  Инициализация:    KMeans++", file=out)
    print("  n_init:           10", file=out)
    print(f"  Кластеров (K):    {n_clusters}", file=out)
    print(f"  Цветов на входе:  {len(colors)}", file=out)
    print(f"  Итераций:         {kmeans.n_iter_}", file=out)
    print(f"  Inertia (WCSS):   {kmeans.inertia_:.2f}", file=out)
    print(f"  Silhouette Score: {sil:.4f}", file=out)

    palette = []
    for r, g, b in sorted(kmeans.cluster_centers_, key=lambda c: _brightness(*c), reverse=True):
        hex_color = _rgb_to_hex(r, g, b)
        palette.append(hex_color)
        print(f"    {hex_color}  RGB({int(r)}, {int(g)}, {int(b)})  яркость={_brightness(r, g, b):.0f}", file=out)

    print(f"{'='*60}\n", file=out)

    return palette
