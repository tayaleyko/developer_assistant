# Ответы анкеты -> палитра/типографика/секции -> граф раскладки с координатами.
# Результат (spec) редактируемый: sections описывают макет семантически,
# layout — дерево узлов для превью и JSON, spec_to_html() отдаёт готовый файл.

import json
import random
import zlib

CANVAS_W = 1200          # ширина холста веб-макета
DESKTOP_W, DESKTOP_H = 1200, 800   # окно десктоп-макета
MARGIN = 80              # боковые поля контента

_SPHERE_PALETTES = {
    "finance":   {"primary": "#1E4FD8", "accent": "#D9A441", "bg": "#F6F8FC"},
    "medical":   {"primary": "#0E9488", "accent": "#3B82F6", "bg": "#F5FBFA"},
    "ecommerce": {"primary": "#2563EB", "accent": "#F59E0B", "bg": "#F8FAFC"},
    "tech":      {"primary": "#4F46E5", "accent": "#06B6D4", "bg": "#F7F8FD"},
    "education": {"primary": "#7C3AED", "accent": "#FBBF24", "bg": "#F9F7FF"},
    "ecology":   {"primary": "#15803D", "accent": "#84CC16", "bg": "#F6FBF7"},
    "realty":    {"primary": "#0F766E", "accent": "#C2894B", "bg": "#FAF9F6"},
    "food":      {"primary": "#DC4B3F", "accent": "#F5A524", "bg": "#FFF9F4"},
    "creative":  {"primary": "#18181B", "accent": "#FF4D6D", "bg": "#FAFAFA"},
    "gov":       {"primary": "#1D4ED8", "accent": "#B91C1C", "bg": "#F5F7FA"},
    "corporate": {"primary": "#1E4FD8", "accent": "#0EA5E9", "bg": "#F6F8FC"},
    "game":      {"primary": "#7C3AED", "accent": "#F43F5E", "bg": "#F7F5FF"},
    "utility":   {"primary": "#475569", "accent": "#0EA5E9", "bg": "#F8FAFC"},
    "other":     {"primary": "#4F5BD5", "accent": "#22B8CF", "bg": "#F7F8FC"},
}

_HEADLINES = {
    "finance":   ("Управляйте финансами уверенно", "Аналитика, платежи и отчёты — в одном окне"),
    "medical":   ("Забота о здоровье — онлайн", "Запись к врачу и результаты анализов без очередей"),
    "ecommerce": ("Всё нужное — с доставкой сегодня", "Тысячи товаров с честными ценами и отзывами"),
    "tech":      ("Платформа для команд разработки", "Планируйте, пишите и выпускайте быстрее"),
    "education": ("Учитесь в своём темпе", "Курсы от практиков с проверкой заданий"),
    "ecology":   ("Технологии для устойчивого будущего", "Считаем след и помогаем его сокращать"),
    "realty":    ("Найдите дом своей мечты", "Проверенные объекты и честные планировки"),
    "food":      ("Свежее меню — каждый день", "Готовим из локальных продуктов и доставляем горячим"),
    "creative":  ("Портфолио, которое запоминается", "Работы, процессы и живые кейсы студии"),
    "gov":       ("Государственные услуги онлайн", "Быстро, прозрачно и без визитов в ведомства"),
    "other":     ("Ваш продукт, каким он должен быть", "Расскажите о деле — мы покажем его лучшую сторону"),
}

_APP_NAMES = {
    "finance": "FinDesk", "medical": "MedCard", "creative": "Studio One",
    "tech": "DevBench", "education": "EduClass", "corporate": "Рабочий кабинет",
    "game": "Game Center", "utility": "Системная утилита", "other": "Приложение",
}

_SERVICES = {
    "finance":   ["Платежи", "Кредитование", "Инвестиции", "Страхование", "Отчётность", "Поддержка"],
    "medical":   ["Приём врача", "Диагностика", "Анализы", "Телемедицина", "Стационар", "Профосмотры"],
    "ecommerce": ["Электроника", "Одежда", "Дом и сад", "Красота", "Спорт", "Детям"],
    "tech":      ["Разработка", "Интеграции", "Аналитика", "Безопасность", "Поддержка", "Обучение"],
    "education": ["Программирование", "Дизайн", "Маркетинг", "Языки", "Менеджмент", "Аналитика"],
    "ecology":   ["Аудит", "Отчётность ESG", "Переработка", "Энергия", "Логистика", "Консалтинг"],
    "realty":    ["Квартиры", "Дома", "Коммерческая", "Аренда", "Ипотека", "Оценка"],
    "food":      ["Завтраки", "Обеды", "Ужины", "Десерты", "Напитки", "Сезонное"],
    "creative":  ["Брендинг", "Веб-дизайн", "Моушн", "Иллюстрация", "Фото", "3D"],
    "gov":       ["Документы", "Налоги", "Транспорт", "Семья", "Здоровье", "Жильё"],
    "other":     ["Услуга 1", "Услуга 2", "Услуга 3", "Услуга 4", "Услуга 5", "Услуга 6"],
}

_PRODUCTS = {
    "food":      [("Паста с трюфелем", "590 ₽"), ("Том-ям с креветками", "640 ₽"),
                  ("Боул с лососем", "560 ₽"), ("Чизкейк", "320 ₽"),
                  ("Рамен", "540 ₽"), ("Тартар из говядины", "690 ₽"),
                  ("Лимонад манго", "240 ₽"), ("Сырники", "350 ₽")],
    "_default":  [("Товар Alpha", "2 990 ₽"), ("Товар Nova", "1 490 ₽"),
                  ("Товар Prime", "5 990 ₽"), ("Товар Lite", "990 ₽"),
                  ("Товар Max", "7 490 ₽"), ("Товар Go", "1 990 ₽"),
                  ("Товар Pro", "4 490 ₽"), ("Товар Mini", "790 ₽")],
}

_ARTICLES = [
    "Что изменится в отрасли в этом году: главные тренды",
    "Интервью с экспертом: как принимаются решения",
    "Разбор: пять ошибок, которые совершают почти все",
    "Репортаж из первых рук: один день внутри команды",
    "Исследование: цифры, о которых стоит знать",
    "Мнение редакции: куда всё движется",
]

_NAV_BY_TYPE = {
    "landing":   ["Главная", "Возможности", "Цены", "Контакты"],
    "corporate": ["О компании", "Услуги", "Проекты", "Новости", "Контакты"],
    "ecommerce": ["Каталог", "Акции", "Доставка", "О нас"],
    "news":      ["Политика", "Экономика", "Технологии", "Культура", "Спорт"],
    "saas":      ["Продукт", "Решения", "Цены", "Документация"],
    "blog":      ["Статьи", "Обо мне", "Проекты", "Контакты"],
    "_default":  ["Главная", "О нас", "Услуги", "Контакты"],
}

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def _mix(c1, c2, t):
    a, b = _hex_to_rgb(c1), _hex_to_rgb(c2)
    return _rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def _lighten(c, t):
    return _mix(c, "#FFFFFF", t)


def _darken(c, t):
    return _mix(c, "#000000", t)


def _luma(c):
    r, g, b = _hex_to_rgb(c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _text_on(c):
    return "#FFFFFF" if _luma(c) < 150 else "#101828"


def flatten_answers(answers):
    flat = {}
    for _block, block_answers in (answers or {}).items():
        if isinstance(block_answers, dict):
            flat.update(block_answers)
    return flat


def _val(flat, key, default=""):
    v = flat.get(key, default)
    if isinstance(v, dict):
        return v.get("value", default)
    if isinstance(v, list):
        return v[0] if v else default
    return v if v is not None else default


def _params_from_answers(flat, project_type):
    if project_type == "website":
        return {
            "project_type": "website",
            "site_type": _val(flat, "w2", "corporate"),
            "sphere": _val(flat, "w_d0", "other"),
            "style": _val(flat, "w_d5", "unknown"),
            "pages": _val(flat, "w_d6", "2-5"),
            "nav": _val(flat, "w_d7", "top"),
            "dark_mode": _val(flat, "w_d8", "no"),
            "animations": _val(flat, "w_d9", "subtle"),
            "accessibility": _val(flat, "w_d10", "nice"),
            "ui_kit": _val(flat, "w_d11", "unknown"),
        }
    return {
        "project_type": "desktop",
        "app_type": _val(flat, "d2", "other"),
        "sphere": _val(flat, "d_d0", "other"),
        "design_system": _val(flat, "d_d3", "unknown"),
        "nav": _val(flat, "d_d5", "sidebar"),
        "dark_mode": _val(flat, "d_d6", "no"),
        "animations": _val(flat, "d_d7", "subtle"),
        "accessibility": _val(flat, "d_d8", "nice"),
        "scaling": _val(flat, "d_d9", "basic"),
        "onboarding": _val(flat, "d_d10", "tooltips"),
    }


def _build_palette(params, palette_override=None, dark=False):
    base = dict(_SPHERE_PALETTES.get(params["sphere"], _SPHERE_PALETTES["other"]))
    style = params.get("style", "unknown")

    if palette_override:
        if len(palette_override) >= 1:
            base["primary"] = palette_override[0]
        if len(palette_override) >= 2:
            base["accent"] = palette_override[1]

    primary, accent, bg = base["primary"], base["accent"], base["bg"]

    if style == "minimalist":
        bg = "#FCFCFD"
        primary = _mix(primary, "#667085", 0.15)
    elif style == "friendly":
        primary = _lighten(primary, 0.12)
        bg = _mix(bg, accent, 0.04)
    elif style == "creative":
        primary, accent = accent, primary   # смелая инверсия акцентов

    if dark:
        dbg = _mix("#0E1015", primary, 0.06)
        return {
            "bg": dbg,
            "surface": _lighten(dbg, 0.06),
            "text": "#E8EAF2",
            "muted": "#9AA0B4",
            "border": _lighten(dbg, 0.14),
            "primary": _lighten(primary, 0.18),
            "primary_text": _text_on(_lighten(primary, 0.18)),
            "accent": _lighten(accent, 0.10),
            "footer": _darken(dbg, 0.25),
        }

    a11y = params.get("accessibility") == "yes"
    return {
        "bg": bg,
        "surface": "#FFFFFF",
        "text": "#0B1220" if a11y else "#101828",
        "muted": "#475467" if a11y else "#667085",
        "border": "#E4E7EF",
        "primary": _darken(primary, 0.08) if a11y else primary,
        "primary_text": _text_on(primary),
        "accent": accent,
        "footer": _mix("#101828", primary, 0.25),
    }


def _build_typography(params):
    style = params.get("style", "unknown")
    site_type = params.get("site_type", "")
    ds = params.get("design_system", "")

    radius = {"minimalist": 4, "corporate": 8, "creative": 2, "friendly": 16}.get(style, 8)
    if params.get("ui_kit") == "yes":
        radius = 8
    if ds == "fluent":
        radius = 6
    elif ds == "material":
        radius = 10
    elif ds == "macos_hig":
        radius = 10

    heading_font = "'Segoe UI', system-ui, sans-serif"
    if site_type == "news":
        heading_font = "Georgia, 'Times New Roman', serif"
    elif style == "creative":
        heading_font = "'Segoe UI Black', 'Arial Black', system-ui, sans-serif"
    if ds == "material":
        heading_font = "Roboto, 'Segoe UI', sans-serif"
    elif ds == "macos_hig":
        heading_font = "-apple-system, 'Helvetica Neue', 'Segoe UI', sans-serif"

    return {
        "heading_font": heading_font,
        "body_font": "'Segoe UI', system-ui, sans-serif" if ds != "material" else "Roboto, sans-serif",
        "base_size": 16 if params.get("accessibility") == "yes" else 15,
        "radius": radius,
        "spacing": {"minimalist": 1.25, "creative": 1.15, "friendly": 1.1}.get(style, 1.0),
    }


def _nav_links(params):
    links = list(_NAV_BY_TYPE.get(params.get("site_type", ""), _NAV_BY_TYPE["_default"]))
    pages = params.get("pages", "2-5")
    if pages == "1":
        links = links[:3]
    elif pages in ("16-50", "50+"):
        links = links[:4] + ["Ещё"]
    return links


def _compose_website(params, rng):
    sphere = params["sphere"]
    site_type = params["site_type"]
    headline, subline = _HEADLINES.get(sphere, _HEADLINES["other"])
    services = _SERVICES.get(sphere, _SERVICES["other"])
    links = _nav_links(params)
    brand = {"finance": "FinPlace", "medical": "MedPoint", "ecommerce": "Маркет",
             "tech": "DevHub", "education": "Учебная среда", "ecology": "GreenLab",
             "realty": "Домовой", "food": "Кухня № 1", "creative": "Студия",
             "gov": "Госпортал", "other": "Бренд"}.get(sphere, "Бренд")

    hero_variant = rng.choice(["split", "centered"]) if site_type in ("landing", "corporate") else \
        ("centered" if site_type == "saas" else "split")

    sections = [{"kind": "navbar", "brand": brand, "links": links,
                 "cta": "Связаться" if site_type in ("corporate", "landing") else "Войти",
                 "nav": params["nav"]}]

    if site_type == "ecommerce":
        products = list(_PRODUCTS.get(sphere, _PRODUCTS["_default"]))
        rng.shuffle(products)
        sections += [
            {"kind": "searchbar"},
            {"kind": "categories", "chips": services[:6]},
            {"kind": "promo", "headline": "Скидки недели до −40%", "cta": "Смотреть все"},
            {"kind": "products", "title": "Популярное сейчас", "items": products[:8]},
            {"kind": "cta_band", "headline": "Бесплатная доставка от 1 500 ₽", "cta": "Подробнее"},
        ]
    elif site_type == "news":
        arts = list(_ARTICLES)
        rng.shuffle(arts)
        sections += [
            {"kind": "masthead", "brand": brand},
            {"kind": "lead_news", "main": arts[0], "side": arts[1:4]},
            {"kind": "articles", "title": "Свежие материалы", "items": arts[1:] + arts[:1]},
            {"kind": "newsletter"},
        ]
    elif site_type == "saas":
        sections += [
            {"kind": "hero", "variant": "centered", "headline": headline, "subline": subline,
             "cta": "Попробовать бесплатно", "secondary": "Демо", "screenshot": True},
            {"kind": "features", "title": "Почему выбирают нас", "cards": services[:3]},
            {"kind": "pricing", "title": "Тарифы",
             "tiers": [("Старт", "0 ₽"), ("Команда", "990 ₽/мес"), ("Бизнес", "2 990 ₽/мес")],
             "highlight": 1},
        ]
    elif site_type == "blog":
        arts = list(_ARTICLES)
        rng.shuffle(arts)
        sections += [
            {"kind": "featured_post", "title": arts[0]},
            {"kind": "posts", "items": arts[1:5], "tags": ["дизайн", "код", "процессы", "заметки"]},
        ]
    elif site_type == "landing":
        sections += [
            {"kind": "hero", "variant": hero_variant, "headline": headline, "subline": subline,
             "cta": "Оставить заявку", "secondary": "Узнать больше",
             "screenshot": False},
            {"kind": "logos", "n": 5},
            {"kind": "features", "title": "Что вы получите", "cards": services[:3]},
            {"kind": "cta_band", "headline": "Готовы начать? Это займёт пару минут",
             "cta": "Оставить заявку"},
        ]
    else:  # corporate и всё остальное
        sections += [
            {"kind": "hero", "variant": hero_variant, "headline": headline, "subline": subline,
             "cta": "Наши услуги", "secondary": "О компании", "screenshot": False},
            {"kind": "features", "title": "Направления работы", "cards": services[:6]},
            {"kind": "about", "title": "О компании",
             "text": "Команда практиков, которая отвечает за результат на каждом этапе."},
            {"kind": "cta_band", "headline": "Обсудим ваш проект?", "cta": "Связаться"},
        ]

    sections.append({"kind": "footer", "brand": brand,
                     "cols": ["Компания", "Продукт", "Помощь", "Контакты"]})
    return sections


def _compose_desktop(params, rng):
    sphere = params["sphere"]
    title = _APP_NAMES.get(sphere, _APP_NAMES["other"])
    nav = params.get("nav", "sidebar")
    if nav == "unknown":
        nav = "sidebar"

    if sphere == "creative":
        content = [{"kind": "canvas_area"}, {"kind": "props_panel"}]
    elif sphere == "utility":
        content = [{"kind": "form", "fields": ["Источник", "Назначение", "Режим", "Расписание"]},
                   {"kind": "log"}]
    else:
        content = [
            {"kind": "statcards",
             "items": [("Активные задачи", "24"), ("За неделю", "132"), ("Ошибки", "3")]},
            {"kind": "table",
             "cols": ["Название", "Статус", "Ответственный", "Обновлено"],
             "rows": 6},
        ]

    sections = [{"kind": "titlebar", "title": title,
                 "chrome": params.get("design_system", "unknown")}]
    if nav == "ribbon":
        sections.append({"kind": "ribbon",
                         "tabs": ["Файл", "Главная", "Вставка", "Вид"],
                         "groups": [("Буфер", 3), ("Формат", 4), ("Данные", 3)]})
    elif nav == "tabs":
        sections.append({"kind": "tabstrip",
                         "tabs": ["Обзор", "Данные", "Отчёты", "Настройки"]})

    sections.append({"kind": "workspace", "nav": nav,
                     "nav_items": ["Обзор", "Проекты", "Задачи", "Отчёты", "Команда", "Настройки"],
                     "content": content})
    sections.append({"kind": "statusbar",
                     "text": "Готово  ·  синхронизировано только что"})
    return sections


def _node(kind, x, y, w, h, **kw):
    n = {"type": kind, "x": round(x), "y": round(y), "w": round(w), "h": round(h)}
    n.update(kw)
    return n


class _Layout:
    """Курсорная раскладка сверху вниз: секции -> абсолютные координаты."""

    def __init__(self, pal, typo, width=CANVAS_W, x0=MARGIN):
        self.pal = pal
        self.typo = typo
        self.width = width
        self.x0 = x0
        self.cw = width - x0 - MARGIN     # ширина контента
        self.y = 0
        self.tree = []

    def section(self, name, height, fill=None):
        if self.x0 == MARGIN:
            x, w = 0, self.width
        else:
            x, w = self.x0 - 40, self.width - self.x0 + 40
        node = _node("frame", x, self.y, w, height, id=name,
                     fill=fill or self.pal["bg"], radius=0, children=[])
        self.tree.append(node)
        return node

    def gap(self, h):
        self.y += round(h * self.typo["spacing"])


def _card(children, x, y, w, h, pal, typo, **kw):
    opts = {"fill": pal["surface"], "stroke": pal["border"], "radius": typo["radius"]}
    opts.update(kw)
    children.append(_node("frame", x, y, w, h, **opts))


def _bars(children, x, y, w, n, pal, gap=16, bar_h=10):
    for i in range(n):
        bw = w if i < n - 1 else w * 0.62
        children.append(_node("bar", x, y + i * gap, bw, bar_h,
                              fill=_mix(pal["muted"], pal["surface"], 0.55)))


def _layout_website(sections, pal, typo, params):
    sidebar = params.get("nav") == "sidebar"
    lay = _Layout(pal, typo, x0=(300 if sidebar else MARGIN))
    R = typo["radius"]

    for sec in sections:
        k = sec["kind"]
        if k == "navbar":
            h = 72
            s = lay.section("navbar", h, fill=pal["surface"])
            ch = s["children"]
            ch.append(_node("text", lay.x0, lay.y + h / 2, 200, 24, label=sec["brand"],
                            size=20, bold=True, color=pal["primary"], anchor="w"))
            if sec.get("nav") == "burger":
                for i in range(3):
                    ch.append(_node("bar", lay.width - MARGIN - 28, lay.y + 28 + i * 8,
                                    28, 3, fill=pal["text"]))
            elif not sidebar:
                bx = lay.width - MARGIN - 140
                ch.append(_node("button", bx, lay.y + 18, 140, 36, label=sec["cta"],
                                fill=pal["primary"], text_color=pal["primary_text"], radius=R))
                lx = bx - 24
                for name in reversed(sec["links"]):
                    lw = max(60, len(name) * 9 + 16)
                    lx -= lw
                    ch.append(_node("text", lx, lay.y + h / 2, lw, 18, label=name,
                                    size=13, color=pal["text"], anchor="w"))
            ch.append(_node("bar", 0, lay.y + h - 1, lay.width, 1, fill=pal["border"]))
            lay.y += h
            continue

        if k == "searchbar":
            h = 64
            s = lay.section("searchbar", h, fill=pal["surface"])
            ch = s["children"]
            ch.append(_node("frame", lay.x0, lay.y + 14, lay.cw - 180, 36,
                            fill=pal["bg"], stroke=pal["border"], radius=R + 6))
            ch.append(_node("text", lay.x0 + 16, lay.y + 32, 300, 16,
                            label="Поиск по каталогу…", size=13, color=pal["muted"], anchor="w"))
            ch.append(_node("button", lay.x0 + lay.cw - 160, lay.y + 14, 160, 36,
                            label="Корзина · 2", fill=pal["accent"],
                            text_color=_text_on(pal["accent"]), radius=R))
            lay.y += h
            continue

        if k == "masthead":
            h = 96
            s = lay.section("masthead", h, fill=pal["surface"])
            ch = s["children"]
            mx = lay.x0 + lay.cw / 2
            ch.append(_node("text", mx, lay.y + 40, 400, 36, label=sec["brand"],
                            size=32, bold=True, color=pal["text"], anchor="center", serif=True))
            ch.append(_node("text", mx, lay.y + 72, 300, 14,
                            label="Независимое издание · сегодня", size=12,
                            color=pal["muted"], anchor="center"))
            ch.append(_node("bar", 0, lay.y + h - 2, lay.width, 2, fill=pal["text"]))
            lay.y += h
            continue

        if k == "hero":
            centered = sec["variant"] == "centered"
            h = 460 if (centered and sec.get("screenshot")) else (380 if centered else 400)
            s = lay.section("hero", h)
            ch = s["children"]
            if centered:
                cx = lay.x0 + lay.cw / 2
                ch.append(_node("text", cx, lay.y + 90, lay.cw * 0.8, 40,
                                label=sec["headline"], size=36, bold=True,
                                color=pal["text"], anchor="center"))
                ch.append(_node("text", cx, lay.y + 140, lay.cw * 0.6, 20,
                                label=sec["subline"], size=16, color=pal["muted"], anchor="center"))
                bw = 190
                ch.append(_node("button", cx - bw - 8, lay.y + 176, bw, 46, label=sec["cta"],
                                fill=pal["primary"], text_color=pal["primary_text"], radius=R))
                ch.append(_node("button", cx + 8, lay.y + 176, bw, 46, label=sec["secondary"],
                                fill=pal["surface"], text_color=pal["primary"],
                                stroke=pal["primary"], radius=R))
                if sec.get("screenshot"):
                    ch.append(_node("image", lay.x0 + lay.cw * 0.1, lay.y + 250,
                                    lay.cw * 0.8, 180, fill=_mix(pal["primary"], pal["bg"], 0.85),
                                    stroke=pal["border"], radius=R, label="скриншот продукта"))
            else:
                ch.append(_node("text", lay.x0, lay.y + 100, lay.cw * 0.5, 40,
                                label=sec["headline"], size=34, bold=True,
                                color=pal["text"], anchor="w", wrap=int(lay.cw * 0.48)))
                ch.append(_node("text", lay.x0, lay.y + 190, lay.cw * 0.45, 20,
                                label=sec["subline"], size=15, color=pal["muted"],
                                anchor="w", wrap=int(lay.cw * 0.45)))
                ch.append(_node("button", lay.x0, lay.y + 250, 190, 46, label=sec["cta"],
                                fill=pal["primary"], text_color=pal["primary_text"], radius=R))
                ch.append(_node("button", lay.x0 + 206, lay.y + 250, 170, 46,
                                label=sec["secondary"], fill=pal["surface"],
                                text_color=pal["primary"], stroke=pal["primary"], radius=R))
                iw = lay.cw * 0.42
                ch.append(_node("image", lay.x0 + lay.cw - iw, lay.y + 60, iw, h - 120,
                                fill=_mix(pal["accent"], pal["bg"], 0.8),
                                stroke=pal["border"], radius=R, label="изображение"))
            lay.y += h
            continue

        if k == "promo":
            h = 200
            s = lay.section("promo", h)
            ch = s["children"]
            ch.append(_node("frame", lay.x0, lay.y + 20, lay.cw, h - 40,
                            fill=pal["primary"], radius=R + 4))
            ch.append(_node("text", lay.x0 + 48, lay.y + h / 2 - 10, lay.cw * 0.5, 30,
                            label=sec["headline"], size=26, bold=True,
                            color=pal["primary_text"], anchor="w"))
            ch.append(_node("button", lay.x0 + lay.cw - 220, lay.y + h / 2 - 23, 170, 46,
                            label=sec["cta"], fill=pal["surface"],
                            text_color=pal["primary"], radius=R))
            lay.y += h
            continue

        if k == "logos":
            h = 110
            s = lay.section("logos", h)
            ch = s["children"]
            n = sec["n"]
            w = 150
            gap = (lay.cw - n * w) / (n - 1)
            for i in range(n):
                ch.append(_node("frame", lay.x0 + i * (w + gap), lay.y + 35, w, 40,
                                fill=_mix(pal["muted"], pal["bg"], 0.82), radius=R))
            lay.y += h
            continue

        if k == "categories":
            h = 66
            s = lay.section("categories", h)
            ch = s["children"]
            x = lay.x0
            for name in sec["chips"]:
                w = len(name) * 9 + 40
                ch.append(_node("chip", x, lay.y + 14, w, 38, label=name,
                                fill=pal["surface"], stroke=pal["border"],
                                text_color=pal["text"], radius=19))
                x += w + 12
            lay.y += h
            continue

        if k == "features":
            cards = sec["cards"]
            rows = (len(cards) + 2) // 3
            h = 90 + rows * 210
            s = lay.section("features", h)
            ch = s["children"]
            ch.append(_node("text", lay.x0, lay.y + 44, lay.cw, 30, label=sec["title"],
                            size=26, bold=True, color=pal["text"], anchor="w"))
            cw = (lay.cw - 48) / 3
            for i, title in enumerate(cards):
                cx = lay.x0 + (i % 3) * (cw + 24)
                cy = lay.y + 90 + (i // 3) * 210
                _card(ch, cx, cy, cw, 186, pal, typo)
                ch.append(_node("frame", cx + 24, cy + 24, 44, 44,
                                fill=_mix(pal["primary"], pal["surface"], 0.85), radius=R + 4))
                ch.append(_node("text", cx + 24, cy + 100, cw - 48, 20, label=title,
                                size=16, bold=True, color=pal["text"], anchor="w"))
                _bars(ch, cx + 24, cy + 128, cw - 48, 2, pal)
            lay.y += h
            continue

        if k == "products":
            items = sec["items"]
            cols, rows = 4, (len(items) + 3) // 4
            card_w = (lay.cw - (cols - 1) * 20) / cols
            card_h = 300
            h = 90 + rows * (card_h + 24)
            s = lay.section("products", h)
            ch = s["children"]
            ch.append(_node("text", lay.x0, lay.y + 44, lay.cw, 30, label=sec["title"],
                            size=26, bold=True, color=pal["text"], anchor="w"))
            for i, (name, price) in enumerate(items):
                cx = lay.x0 + (i % cols) * (card_w + 20)
                cy = lay.y + 90 + (i // cols) * (card_h + 24)
                _card(ch, cx, cy, card_w, card_h, pal, typo)
                ch.append(_node("image", cx + 12, cy + 12, card_w - 24, 140,
                                fill=_mix(pal["accent"], pal["surface"], 0.88),
                                radius=max(2, R - 2)))
                ch.append(_node("text", cx + 16, cy + 176, card_w - 32, 18, label=name,
                                size=13, color=pal["text"], anchor="w"))
                ch.append(_node("text", cx + 16, cy + 206, card_w - 32, 20, label=price,
                                size=17, bold=True, color=pal["text"], anchor="w"))
                ch.append(_node("button", cx + 12, cy + card_h - 54, card_w - 24, 40,
                                label="В корзину", fill=pal["primary"],
                                text_color=pal["primary_text"], radius=R))
            lay.y += h
            continue

        if k == "lead_news":
            h = 420
            s = lay.section("lead_news", h)
            ch = s["children"]
            main_w = lay.cw * 0.6
            ch.append(_node("image", lay.x0, lay.y + 30, main_w, 260,
                            fill=_mix(pal["muted"], pal["bg"], 0.7), radius=2))
            ch.append(_node("text", lay.x0, lay.y + 316, main_w, 26, label=sec["main"],
                            size=22, bold=True, color=pal["text"], anchor="w",
                            wrap=int(main_w), serif=True))
            sx = lay.x0 + main_w + 40
            sw = lay.cw - main_w - 40
            for i, t in enumerate(sec["side"]):
                sy = lay.y + 30 + i * 120
                ch.append(_node("text", sx, sy + 12, sw, 40, label=t, size=15, bold=True,
                                color=pal["text"], anchor="w", wrap=int(sw), serif=True))
                ch.append(_node("text", sx, sy + 66, sw, 14, label="12 минут назад",
                                size=11, color=pal["muted"], anchor="w"))
                if i < len(sec["side"]) - 1:
                    ch.append(_node("bar", sx, sy + 96, sw, 1, fill=pal["border"]))
            lay.y += h
            continue

        if k == "articles":
            items = sec["items"][:6]
            rows = (len(items) + 2) // 3
            card_h = 250
            h = 90 + rows * (card_h + 24)
            s = lay.section("articles", h)
            ch = s["children"]
            ch.append(_node("text", lay.x0, lay.y + 44, lay.cw, 28, label=sec["title"],
                            size=24, bold=True, color=pal["text"], anchor="w", serif=True))
            cw = (lay.cw - 48) / 3
            for i, t in enumerate(items):
                cx = lay.x0 + (i % 3) * (cw + 24)
                cy = lay.y + 90 + (i // 3) * (card_h + 24)
                _card(ch, cx, cy, cw, card_h, pal, typo)
                ch.append(_node("image", cx, cy, cw, 120,
                                fill=_mix(pal["muted"], pal["bg"], 0.72), radius=0))
                ch.append(_node("text", cx + 16, cy + 140, cw - 32, 40, label=t,
                                size=14, bold=True, color=pal["text"], anchor="w",
                                wrap=int(cw - 32), serif=True))
                ch.append(_node("text", cx + 16, cy + card_h - 28, cw - 32, 14,
                                label="Раздел · сегодня", size=11, color=pal["muted"], anchor="w"))
            lay.y += h
            continue

        if k == "pricing":
            h = 470
            s = lay.section("pricing", h)
            ch = s["children"]
            ch.append(_node("text", lay.x0 + lay.cw / 2, lay.y + 50, lay.cw, 30,
                            label=sec["title"], size=26, bold=True,
                            color=pal["text"], anchor="center"))
            cw = (lay.cw - 48) / 3
            for i, (name, price) in enumerate(sec["tiers"]):
                cx = lay.x0 + i * (cw + 24)
                cy = lay.y + 100
                hl = (i == sec.get("highlight"))
                _card(ch, cx, cy, cw, 330, pal, typo,
                      stroke=pal["primary"] if hl else pal["border"],
                      stroke_width=2 if hl else 1)
                if hl:
                    ch.append(_node("chip", cx + cw / 2 - 60, cy - 14, 120, 28,
                                    label="Популярный", fill=pal["primary"],
                                    text_color=pal["primary_text"], radius=14))
                ch.append(_node("text", cx + 24, cy + 44, cw - 48, 20, label=name,
                                size=16, bold=True, color=pal["text"], anchor="w"))
                ch.append(_node("text", cx + 24, cy + 88, cw - 48, 30, label=price,
                                size=26, bold=True, color=pal["primary"], anchor="w"))
                _bars(ch, cx + 24, cy + 140, cw - 48, 4, pal, gap=26)
                ch.append(_node("button", cx + 24, cy + 330 - 64, cw - 48, 42,
                                label="Выбрать", fill=pal["primary"] if hl else pal["surface"],
                                text_color=pal["primary_text"] if hl else pal["primary"],
                                stroke=None if hl else pal["primary"], radius=R))
            lay.y += h
            continue

        if k == "featured_post":
            h = 320
            s = lay.section("featured_post", h)
            ch = s["children"]
            ch.append(_node("image", lay.x0, lay.y + 30, lay.cw * 0.5, 240,
                            fill=_mix(pal["accent"], pal["bg"], 0.75), radius=R))
            tx = lay.x0 + lay.cw * 0.5 + 40
            tw = lay.cw * 0.5 - 40
            ch.append(_node("chip", tx, lay.y + 40, 110, 28, label="Избранное",
                            fill=_mix(pal["primary"], pal["surface"], 0.85),
                            text_color=pal["primary"], radius=14))
            ch.append(_node("text", tx, lay.y + 92, tw, 48, label=sec["title"],
                            size=22, bold=True, color=pal["text"], anchor="w", wrap=int(tw)))
            _bars(ch, tx, lay.y + 170, tw, 3, pal)
            ch.append(_node("text", tx, lay.y + 240, tw, 14, label="Читать 7 минут",
                            size=12, color=pal["muted"], anchor="w"))
            lay.y += h
            continue

        if k == "posts":
            items = sec["items"]
            h = 60 + len(items) * 140 + 20
            s = lay.section("posts", h)
            ch = s["children"]
            main_w = lay.cw - 340
            for i, t in enumerate(items):
                py = lay.y + 30 + i * 140
                _card(ch, lay.x0, py, main_w, 124, pal, typo)
                ch.append(_node("image", lay.x0 + 16, py + 16, 140, 92,
                                fill=_mix(pal["muted"], pal["bg"], 0.75), radius=max(2, R - 2)))
                ch.append(_node("text", lay.x0 + 176, py + 34, main_w - 200, 20, label=t,
                                size=15, bold=True, color=pal["text"], anchor="w",
                                wrap=int(main_w - 200)))
                ch.append(_node("text", lay.x0 + 176, py + 96, 200, 14,
                                label="5 мин · вчера", size=11, color=pal["muted"], anchor="w"))
            sx = lay.x0 + main_w + 30
            _card(ch, sx, lay.y + 30, 310, 200, pal, typo)
            ch.append(_node("text", sx + 20, lay.y + 60, 270, 18, label="Темы",
                            size=15, bold=True, color=pal["text"], anchor="w"))
            tx, ty = sx + 20, lay.y + 88
            for tag in sec["tags"]:
                w = len(tag) * 9 + 28
                if tx + w > sx + 290:
                    tx = sx + 20
                    ty += 42
                ch.append(_node("chip", tx, ty, w, 32, label="#" + tag,
                                fill=pal["bg"], stroke=pal["border"],
                                text_color=pal["muted"], radius=16))
                tx += w + 10
            lay.y += h
            continue

        if k == "about":
            h = 340
            s = lay.section("about", h, fill=pal["surface"])
            ch = s["children"]
            ch.append(_node("image", lay.x0, lay.y + 50, lay.cw * 0.42, 240,
                            fill=_mix(pal["primary"], pal["surface"], 0.88), radius=R))
            tx = lay.x0 + lay.cw * 0.42 + 48
            tw = lay.cw * 0.58 - 48
            ch.append(_node("text", tx, lay.y + 80, tw, 28, label=sec["title"],
                            size=24, bold=True, color=pal["text"], anchor="w"))
            ch.append(_node("text", tx, lay.y + 124, tw, 20, label=sec["text"],
                            size=14, color=pal["muted"], anchor="w", wrap=int(tw)))
            _bars(ch, tx, lay.y + 190, tw, 3, pal)
            lay.y += h
            continue

        if k == "cta_band":
            h = 180
            s = lay.section("cta_band", h)
            ch = s["children"]
            ch.append(_node("frame", lay.x0, lay.y + 20, lay.cw, h - 40,
                            fill=pal["footer"], radius=R + 4))
            ch.append(_node("text", lay.x0 + 48, lay.y + h / 2 - 10, lay.cw * 0.55, 26,
                            label=sec["headline"], size=22, bold=True,
                            color="#FFFFFF", anchor="w"))
            ch.append(_node("button", lay.x0 + lay.cw - 230, lay.y + h / 2 - 23, 180, 46,
                            label=sec["cta"], fill=pal["accent"],
                            text_color=_text_on(pal["accent"]), radius=R))
            lay.y += h
            continue

        if k == "newsletter":
            h = 150
            s = lay.section("newsletter", h, fill=pal["surface"])
            ch = s["children"]
            ch.append(_node("text", lay.x0, lay.y + 56, 380, 22,
                            label="Подпишитесь на рассылку", size=19, bold=True,
                            color=pal["text"], anchor="w"))
            ch.append(_node("frame", lay.x0 + 420, lay.y + 46, lay.cw - 420 - 180, 44,
                            fill=pal["bg"], stroke=pal["border"], radius=R))
            ch.append(_node("text", lay.x0 + 438, lay.y + 68, 200, 16, label="Ваш e-mail",
                            size=13, color=pal["muted"], anchor="w"))
            ch.append(_node("button", lay.x0 + lay.cw - 160, lay.y + 46, 160, 44,
                            label="Подписаться", fill=pal["primary"],
                            text_color=pal["primary_text"], radius=R))
            lay.y += h
            continue

        if k == "footer":
            h = 230
            s = lay.section("footer", h, fill=pal["footer"])
            ch = s["children"]
            ch.append(_node("text", lay.x0, lay.y + 48, 200, 22, label=sec["brand"],
                            size=18, bold=True, color="#FFFFFF", anchor="w"))
            cw = (lay.cw - 260) / len(sec["cols"])
            for i, col in enumerate(sec["cols"]):
                cx = lay.x0 + 260 + i * cw
                ch.append(_node("text", cx, lay.y + 48, cw - 20, 16, label=col,
                                size=13, bold=True, color="#FFFFFF", anchor="w"))
                _bars(ch, cx, lay.y + 78, cw - 60, 3, pal,
                      gap=22)
                for b in ch[-3:]:
                    b["fill"] = "#5A6478"
            ch.append(_node("bar", lay.x0, lay.y + h - 48, lay.cw, 1, fill="#3A4358"))
            ch.append(_node("text", lay.x0, lay.y + h - 28, 400, 14,
                            label="© 2026 · Все права защищены", size=11,
                            color="#8A93A8", anchor="w"))
            lay.y += h
            continue

    # левая панель навигации (если выбран sidebar)
    if sidebar:
        total_h = lay.y
        panel = _node("frame", 0, 0, 260, total_h, id="side_nav",
                      fill=pal["surface"], stroke=pal["border"], radius=0, children=[])
        links = _nav_links(params)
        panel["children"].append(_node("text", 28, 44, 200, 22,
                                       label=sections[0]["brand"], size=18, bold=True,
                                       color=pal["primary"], anchor="w"))
        for i, name in enumerate(links):
            iy = 100 + i * 52
            if i == 0:
                panel["children"].append(_node("frame", 14, iy - 12, 232, 42,
                                               fill=_mix(pal["primary"], pal["surface"], 0.88),
                                               radius=typo["radius"]))
            panel["children"].append(_node("text", 32, iy + 8, 180, 18, label=name,
                                           size=14, color=pal["text"] if i else pal["primary"],
                                           bold=(i == 0), anchor="w"))
        lay.tree.insert(0, panel)

    return lay.tree, lay.y


def _layout_desktop(sections, pal, typo, params):
    R = typo["radius"]
    tree = []
    y = 0
    W, H = DESKTOP_W, DESKTOP_H
    ds = params.get("design_system", "unknown")

    def frame(**kw):
        n = _node("frame", 0, 0, 0, 0, children=[])
        n.update(kw)
        tree.append(n)
        return n

    body_top = 0
    status_h = 30
    content_x = 0

    for sec in sections:
        k = sec["kind"]
        if k == "titlebar":
            h = 40
            s = frame(x=0, y=0, w=W, h=h, id="titlebar",
                      fill=pal["primary"] if ds == "material" else pal["surface"],
                      radius=0)
            tcol = pal["primary_text"] if ds == "material" else pal["text"]
            ch = s["children"]
            if sec["chrome"] == "macos_hig":
                for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
                    ch.append(_node("frame", 16 + i * 22, 14, 12, 12, fill=c, radius=6))
                ch.append(_node("text", W / 2, 20, 300, 16, label=sec["title"],
                                size=13, bold=True, color=tcol, anchor="center"))
            else:
                ch.append(_node("text", 16, 20, 300, 16, label=sec["title"],
                                size=13, bold=True, color=tcol, anchor="w"))
                for i, sym in enumerate(("—", "▢", "✕")):
                    ch.append(_node("text", W - 108 + i * 36, 20, 24, 16, label=sym,
                                    size=12, color=tcol, anchor="center"))
            ch.append(_node("bar", 0, h - 1, W, 1, fill=pal["border"]))
            y = h
            body_top = h
            continue

        if k == "ribbon":
            h = 118
            s = frame(x=0, y=y, w=W, h=h, id="ribbon", fill=pal["surface"], radius=0)
            ch = s["children"]
            tx = 16
            for i, t in enumerate(sec["tabs"]):
                w = len(t) * 9 + 28
                if i == 1:
                    ch.append(_node("frame", tx, y + 6, w, 28,
                                    fill=_mix(pal["primary"], pal["surface"], 0.88),
                                    radius=R))
                ch.append(_node("text", tx + w / 2, y + 20, w, 16, label=t, size=12,
                                bold=(i == 1), color=pal["primary"] if i == 1 else pal["text"],
                                anchor="center"))
                tx += w + 4
            gx = 16
            for gname, n_btn in sec["groups"]:
                gw = n_btn * 56 + 16
                ch.append(_node("frame", gx, y + 42, gw, 64, fill=pal["bg"],
                                stroke=pal["border"], radius=R))
                for b in range(n_btn):
                    ch.append(_node("frame", gx + 8 + b * 56, y + 50, 48, 34,
                                    fill=_mix(pal["primary"], pal["surface"], 0.9),
                                    radius=max(2, R - 2)))
                ch.append(_node("text", gx + gw / 2, y + 96, gw, 12, label=gname,
                                size=10, color=pal["muted"], anchor="center"))
                gx += gw + 12
            ch.append(_node("bar", 0, y + h - 1, W, 1, fill=pal["border"]))
            y += h
            body_top = y
            continue

        if k == "tabstrip":
            h = 46
            s = frame(x=0, y=y, w=W, h=h, id="tabstrip", fill=pal["bg"], radius=0)
            ch = s["children"]
            tx = 12
            for i, t in enumerate(sec["tabs"]):
                w = len(t) * 9 + 44
                ch.append(_node("frame", tx, y + 8, w, 38,
                                fill=pal["surface"] if i == 0 else _mix(pal["surface"], pal["bg"], 0.5),
                                stroke=pal["border"], radius=R))
                ch.append(_node("text", tx + w / 2, y + 27, w, 14, label=t, size=12,
                                bold=(i == 0), color=pal["text"], anchor="center"))
                tx += w + 6
            y += h
            body_top = y
            continue

        if k == "workspace":
            nav = sec["nav"]
            ws_h = H - body_top - status_h
            if nav in ("sidebar", "tree"):
                sb_w = 250 if nav == "sidebar" else 280
                s = frame(x=0, y=body_top, w=sb_w, h=ws_h, id="nav_panel",
                          fill=_mix(pal["surface"], pal["bg"], 0.4) if ds == "macos_hig" else pal["surface"],
                          stroke=pal["border"], radius=0)
                ch = s["children"]
                if nav == "sidebar":
                    for i, item in enumerate(sec["nav_items"]):
                        iy = body_top + 20 + i * 48
                        if i == 0:
                            ch.append(_node("frame", 10, iy - 10, sb_w - 20, 40,
                                            fill=_mix(pal["primary"], pal["surface"], 0.85),
                                            radius=R))
                        ch.append(_node("frame", 22, iy - 2, 20, 20,
                                        fill=_mix(pal["primary"] if i == 0 else pal["muted"],
                                                  pal["surface"], 0.5),
                                        radius=max(2, R - 4)))
                        ch.append(_node("text", 54, iy + 8, 160, 16, label=item, size=13,
                                        bold=(i == 0),
                                        color=pal["primary"] if i == 0 else pal["text"],
                                        anchor="w"))
                else:  # дерево
                    items = [(0, "Проект"), (1, "Документы"), (2, "Отчёт 2026.docx"),
                             (2, "Смета.xlsx"), (1, "Медиа"), (2, "Логотип.svg"),
                             (1, "Архив"), (0, "Библиотека")]
                    for i, (lvl, item) in enumerate(items):
                        iy = body_top + 24 + i * 38
                        ch.append(_node("text", 20 + lvl * 22, iy, 200, 14,
                                        label=("▸ " if lvl < 2 else "· ") + item, size=12,
                                        bold=(lvl == 0), color=pal["text"], anchor="w"))
                content_x = sb_w
            else:
                content_x = 0

            cx0 = content_x + 24
            cw = W - content_x - 48
            cy = body_top + 20

            # панель инструментов
            s = frame(x=content_x, y=body_top, w=W - content_x, h=ws_h, id="content",
                      fill=pal["bg"], radius=0)
            ch = s["children"]
            ch.append(_node("frame", cx0, cy, cw * 0.4, 36, fill=pal["surface"],
                            stroke=pal["border"], radius=R))
            ch.append(_node("text", cx0 + 14, cy + 18, 160, 14, label="Поиск…",
                            size=12, color=pal["muted"], anchor="w"))
            ch.append(_node("button", cx0 + cw - 150, cy, 150, 36, label="+ Создать",
                            fill=pal["primary"], text_color=pal["primary_text"], radius=R))
            cy += 56

            for block in sec["content"]:
                bk = block["kind"]
                if bk == "statcards":
                    n = len(block["items"])
                    scw = (cw - (n - 1) * 16) / n
                    for i, (name, valx) in enumerate(block["items"]):
                        sx = cx0 + i * (scw + 16)
                        _card(ch, sx, cy, scw, 96, pal, typo)
                        ch.append(_node("text", sx + 18, cy + 28, scw - 36, 14,
                                        label=name, size=12, color=pal["muted"], anchor="w"))
                        ch.append(_node("text", sx + 18, cy + 62, scw - 36, 24,
                                        label=valx, size=24, bold=True,
                                        color=pal["text"], anchor="w"))
                    cy += 116
                elif bk == "table":
                    rows = block["rows"]
                    th = 44 + rows * 40
                    _card(ch, cx0, cy, cw, th, pal, typo)
                    ncol = len(block["cols"])
                    colw = cw / ncol
                    for i, col in enumerate(block["cols"]):
                        ch.append(_node("text", cx0 + 18 + i * colw, cy + 22, colw - 30, 14,
                                        label=col, size=12, bold=True,
                                        color=pal["muted"], anchor="w"))
                    ch.append(_node("bar", cx0, cy + 43, cw, 1, fill=pal["border"]))
                    for r in range(rows):
                        ry = cy + 44 + r * 40
                        _bars(ch, cx0 + 18, ry + 15, colw - 40, 1, pal)
                        chip_fill = ["#DCF5E8", "#FDEBD3", "#E4E7EF"][r % 3]
                        chip_text = ["#177A4C", "#B25E09", "#475467"][r % 3]
                        ch.append(_node("chip", cx0 + 18 + colw, ry + 8, 92, 24,
                                        label=["Активно", "Ожидает", "Черновик"][r % 3],
                                        fill=chip_fill, text_color=chip_text, radius=12))
                        _bars(ch, cx0 + 18 + 2 * colw, ry + 15, colw - 60, 1, pal)
                        _bars(ch, cx0 + 18 + 3 * colw, ry + 15, colw - 80, 1, pal)
                        if r < rows - 1:
                            ch.append(_node("bar", cx0, ry + 40, cw, 1,
                                            fill=_mix(pal["border"], pal["surface"], 0.5)))
                    cy += th + 20
                elif bk == "canvas_area":
                    aw = cw - 270
                    ah = ws_h - (cy - body_top) - 24
                    ch.append(_node("frame", cx0, cy, aw, ah,
                                    fill="#23262E", radius=R))
                    ch.append(_node("frame", cx0 + aw * 0.22, cy + ah * 0.18,
                                    aw * 0.5, ah * 0.55, fill="#FFFFFF", radius=2))
                    ch.append(_node("text", cx0 + aw / 2, cy + ah - 22, 200, 12,
                                    label="Холст · 100%", size=10, color="#9AA0B4",
                                    anchor="center"))
                elif bk == "props_panel":
                    px = cx0 + cw - 250
                    ph = ws_h - (cy - body_top) - 24
                    _card(ch, px, cy, 250, ph, pal, typo)
                    ch.append(_node("text", px + 18, cy + 26, 200, 14, label="Свойства",
                                    size=13, bold=True, color=pal["text"], anchor="w"))
                    for i in range(5):
                        ry = cy + 56 + i * 58
                        ch.append(_node("text", px + 18, ry, 100, 12,
                                        label=["Слой", "Заливка", "Обводка", "Тень", "Прозрачность"][i],
                                        size=11, color=pal["muted"], anchor="w"))
                        ch.append(_node("frame", px + 18, ry + 10, 214, 30,
                                        fill=pal["bg"], stroke=pal["border"],
                                        radius=max(2, R - 2)))
                elif bk == "form":
                    fh = 44 + len(block["fields"]) * 66 + 60
                    _card(ch, cx0, cy, cw * 0.55, fh, pal, typo)
                    ch.append(_node("text", cx0 + 22, cy + 30, 300, 16,
                                    label="Параметры задачи", size=14, bold=True,
                                    color=pal["text"], anchor="w"))
                    for i, f in enumerate(block["fields"]):
                        fy = cy + 60 + i * 66
                        ch.append(_node("text", cx0 + 22, fy, 200, 12, label=f,
                                        size=11, color=pal["muted"], anchor="w"))
                        ch.append(_node("frame", cx0 + 22, fy + 10, cw * 0.55 - 44, 34,
                                        fill=pal["bg"], stroke=pal["border"],
                                        radius=max(2, R - 2)))
                    ch.append(_node("button", cx0 + 22, cy + fh - 52, 170, 38,
                                    label="Запустить", fill=pal["primary"],
                                    text_color=pal["primary_text"], radius=R))
                elif bk == "log":
                    lx = cx0 + cw * 0.55 + 20
                    lw = cw * 0.45 - 20
                    lh = ws_h - (cy - body_top) - 24
                    ch.append(_node("frame", lx, cy, lw, lh, fill="#16181D", radius=R))
                    ch.append(_node("text", lx + 16, cy + 24, 200, 12, label="Журнал",
                                    size=11, bold=True, color="#7EE787", anchor="w"))
                    for i in range(8):
                        ch.append(_node("bar", lx + 16, cy + 48 + i * 22,
                                        lw * (0.5 + 0.4 * ((i * 37) % 10) / 10), 8,
                                        fill="#2E3440" if i % 3 else "#3B4252"))
            continue

        if k == "statusbar":
            s = frame(x=0, y=H - status_h, w=W, h=status_h, id="statusbar",
                      fill=pal["surface"], radius=0)
            s["children"].append(_node("bar", 0, H - status_h, W, 1, fill=pal["border"]))
            s["children"].append(_node("text", 16, H - status_h / 2, 500, 14,
                                       label=sec["text"], size=11,
                                       color=pal["muted"], anchor="w"))
            continue

    return tree, H


def generate_template(answers, project_type, palette_override=None, seed=0):
    """answers: state.answers (по блокам) либо уже плоский словарь."""
    flat = flatten_answers(answers) if answers and any(
        isinstance(v, dict) and not v.get("value") for v in answers.values()
    ) else dict(answers or {})
    params = _params_from_answers(flat, project_type)

    rng = random.Random(
        (seed * 7919 + zlib.crc32(json.dumps(params, sort_keys=True).encode("utf-8")))
        & 0xFFFFFFFF
    )

    dark_default = params.get("dark_mode") == "yes" and project_type == "desktop"
    pal = _build_palette(params, palette_override, dark=dark_default)
    typo = _build_typography(params)

    if project_type == "website":
        sections = _compose_website(params, rng)
        layout, height = _layout_website(sections, pal, typo, params)
        canvas = {"width": CANVAS_W, "height": height}
    else:
        sections = _compose_desktop(params, rng)
        layout, height = _layout_desktop(sections, pal, typo, params)
        canvas = {"width": DESKTOP_W, "height": DESKTOP_H}

    spec = {
        "meta": dict(params, seed=seed, generator="template_generator/1.0"),
        "palette": pal,
        "palette_dark": _build_palette(params, palette_override, dark=True)
        if params.get("dark_mode") in ("yes", "optional") else None,
        "typography": typo,
        "sections": sections,
        "canvas": canvas,
        "layout": layout,
    }
    return spec


def spec_to_json(spec):
    return json.dumps(spec, ensure_ascii=False, indent=2)


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _html_website(spec):
    pal, typo, meta = spec["palette"], spec["typography"], spec["meta"]
    dark = spec.get("palette_dark")
    anim = meta.get("animations", "subtle")
    a11y = meta.get("accessibility") == "yes"
    out = []
    add = out.append

    trans = "transition: all .18s ease;" if anim != "no" else ""
    dark_css = ""
    if dark:
        dark_css = f"""
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:{dark['bg']}; --surface:{dark['surface']}; --text:{dark['text']};
    --muted:{dark['muted']}; --border:{dark['border']}; --primary:{dark['primary']};
    --primary-text:{dark['primary_text']}; --accent:{dark['accent']}; --footer:{dark['footer']}; }}
}}"""
    focus_css = "a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:2px;}" if a11y else ""

    add(f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(meta.get('site_type', 'site'))} — сгенерированный шаблон</title>
<style>
:root {{ --bg:{pal['bg']}; --surface:{pal['surface']}; --text:{pal['text']};
  --muted:{pal['muted']}; --border:{pal['border']}; --primary:{pal['primary']};
  --primary-text:{pal['primary_text']}; --accent:{pal['accent']}; --footer:{pal['footer']};
  --radius:{typo['radius']}px; }}{dark_css}
*{{box-sizing:border-box;margin:0;}}
body{{background:var(--bg);color:var(--text);font:{typo['base_size']}px/1.6 {typo['body_font']};}}
h1,h2,h3{{font-family:{typo['heading_font']};line-height:1.2;}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px;}}
.btn{{display:inline-block;padding:12px 26px;border-radius:var(--radius);border:0;cursor:pointer;
  font-weight:600;font-size:15px;background:var(--primary);color:var(--primary-text);
  text-decoration:none;{trans}}}
.btn:hover{{filter:brightness(1.08);}}
.btn.ghost{{background:transparent;color:var(--primary);border:1.5px solid var(--primary);}}
.btn.accent{{background:var(--accent);color:{_text_on(pal['accent'])};}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:24px;{trans}}}
.card:hover{{box-shadow:0 6px 24px rgba(16,24,40,.07);}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;}}
.muted{{color:var(--muted);}}
section{{padding:{int(56 * typo['spacing'])}px 0;}}
{focus_css}
@media (max-width:900px){{.grid3,.grid4{{grid-template-columns:1fr 1fr;}}}}
@media (max-width:600px){{.grid3,.grid4{{grid-template-columns:1fr;}}}}
</style></head><body>""")

    for sec in spec["sections"]:
        k = sec["kind"]
        if k == "navbar":
            links = "".join(f'<a href="#" style="color:var(--text);text-decoration:none;margin-left:22px;font-size:14px;">{_esc(l)}</a>'
                            for l in sec["links"])
            add(f"""<header style="background:var(--surface);border-bottom:1px solid var(--border);">
<div class="wrap" style="display:flex;align-items:center;justify-content:space-between;height:68px;">
<strong style="color:var(--primary);font-size:20px;">{_esc(sec['brand'])}</strong>
<nav style="display:flex;align-items:center;">{links}
<a class="btn" style="margin-left:26px;padding:9px 20px;" href="#">{_esc(sec['cta'])}</a></nav>
</div></header>""")
        elif k == "hero":
            btns = (f'<a class="btn" href="#">{_esc(sec["cta"])}</a> '
                    f'<a class="btn ghost" href="#">{_esc(sec["secondary"])}</a>')
            if sec["variant"] == "centered":
                shot = ('<div style="margin:48px auto 0;max-width:860px;height:300px;border-radius:var(--radius);'
                        'border:1px solid var(--border);background:linear-gradient(135deg,'
                        f'{_mix(pal["primary"], pal["bg"], 0.85)},{_mix(pal["accent"], pal["bg"], 0.85)});"></div>'
                        ) if sec.get("screenshot") else ""
                add(f"""<section><div class="wrap" style="text-align:center;">
<h1 style="font-size:44px;max-width:20ch;margin:0 auto 18px;">{_esc(sec['headline'])}</h1>
<p class="muted" style="max-width:52ch;margin:0 auto 30px;font-size:18px;">{_esc(sec['subline'])}</p>
{btns}{shot}</div></section>""")
            else:
                add(f"""<section><div class="wrap" style="display:grid;grid-template-columns:1.1fr 1fr;gap:48px;align-items:center;">
<div><h1 style="font-size:40px;margin-bottom:18px;">{_esc(sec['headline'])}</h1>
<p class="muted" style="font-size:17px;margin-bottom:28px;">{_esc(sec['subline'])}</p>{btns}</div>
<div style="height:320px;border-radius:var(--radius);background:linear-gradient(135deg,
{_mix(pal['accent'], pal['bg'], 0.75)},{_mix(pal['primary'], pal['bg'], 0.8)});"></div>
</div></section>""")
        elif k == "searchbar":
            add(f"""<div style="background:var(--surface);border-bottom:1px solid var(--border);padding:14px 0;">
<div class="wrap" style="display:flex;gap:16px;">
<input placeholder="Поиск по каталогу…" style="flex:1;padding:11px 18px;border-radius:calc(var(--radius) + 6px);
border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:14px;">
<a class="btn accent" href="#">Корзина · 2</a></div></div>""")
        elif k == "categories":
            chips = "".join(f'<a href="#" style="padding:9px 18px;border:1px solid var(--border);background:var(--surface);border-radius:99px;color:var(--text);text-decoration:none;font-size:14px;">{_esc(c)}</a>' for c in sec["chips"])
            add(f'<div class="wrap" style="display:flex;gap:10px;flex-wrap:wrap;padding:18px 24px;">{chips}</div>')
        elif k == "promo":
            add(f"""<div class="wrap"><div style="background:var(--primary);color:var(--primary-text);
border-radius:calc(var(--radius) + 4px);padding:44px 48px;display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap;">
<h2 style="font-size:28px;">{_esc(sec['headline'])}</h2>
<a class="btn" style="background:var(--surface);color:var(--primary);" href="#">{_esc(sec['cta'])}</a>
</div></div>""")
        elif k == "products":
            cards = ""
            for name, price in sec["items"]:
                cards += f"""<div class="card" style="padding:12px;">
<div style="height:150px;border-radius:calc(var(--radius) - 2px);background:{_mix(pal['accent'], pal['surface'], 0.88)};margin-bottom:12px;"></div>
<div style="font-size:14px;">{_esc(name)}</div>
<div style="font-weight:700;font-size:18px;margin:6px 0 12px;">{_esc(price)}</div>
<a class="btn" style="display:block;text-align:center;padding:10px;" href="#">В корзину</a></div>"""
            add(f'<section><div class="wrap"><h2 style="font-size:28px;margin-bottom:26px;">{_esc(sec["title"])}</h2><div class="grid4">{cards}</div></div></section>')
        elif k == "logos":
            cells = "".join(f'<div style="height:40px;border-radius:var(--radius);background:{_mix(pal["muted"], pal["bg"], 0.82)};"></div>' for _ in range(sec["n"]))
            add(f'<div class="wrap" style="display:grid;grid-template-columns:repeat({sec["n"]},1fr);gap:32px;padding:10px 24px 34px;">{cells}</div>')
        elif k == "features":
            cards = ""
            for title in sec["cards"]:
                cards += f"""<div class="card"><div style="width:44px;height:44px;border-radius:calc(var(--radius) + 4px);
background:{_mix(pal['primary'], pal['surface'], 0.85)};margin-bottom:18px;"></div>
<h3 style="font-size:17px;margin-bottom:10px;">{_esc(title)}</h3>
<p class="muted" style="font-size:14px;">Коротко о том, какую задачу закрывает это направление и почему оно важно.</p></div>"""
            add(f'<section><div class="wrap"><h2 style="font-size:28px;margin-bottom:26px;">{_esc(sec["title"])}</h2><div class="grid3">{cards}</div></div></section>')
        elif k == "masthead":
            add(f"""<header style="background:var(--surface);border-bottom:2px solid var(--text);text-align:center;padding:26px 0 18px;">
<h1 style="font-size:38px;">{_esc(sec['brand'])}</h1>
<div class="muted" style="font-size:13px;margin-top:6px;">Независимое издание · сегодня</div></header>""")
        elif k == "lead_news":
            side = "".join(f'<div style="padding:14px 0;border-bottom:1px solid var(--border);"><h3 style="font-size:16px;">{_esc(t)}</h3><div class="muted" style="font-size:12px;margin-top:6px;">12 минут назад</div></div>' for t in sec["side"])
            add(f"""<section><div class="wrap" style="display:grid;grid-template-columns:1.6fr 1fr;gap:40px;">
<article><div style="height:300px;background:{_mix(pal['muted'], pal['bg'], 0.7)};margin-bottom:18px;"></div>
<h2 style="font-size:26px;">{_esc(sec['main'])}</h2></article><aside>{side}</aside></div></section>""")
        elif k == "articles":
            cards = ""
            for t in sec["items"][:6]:
                cards += f"""<article class="card" style="padding:0;overflow:hidden;">
<div style="height:130px;background:{_mix(pal['muted'], pal['bg'], 0.72)};"></div>
<div style="padding:16px;"><h3 style="font-size:15px;margin-bottom:10px;">{_esc(t)}</h3>
<div class="muted" style="font-size:12px;">Раздел · сегодня</div></div></article>"""
            add(f'<section><div class="wrap"><h2 style="font-size:26px;margin-bottom:24px;">{_esc(sec["title"])}</h2><div class="grid3">{cards}</div></div></section>')
        elif k == "pricing":
            cards = ""
            for i, (name, price) in enumerate(sec["tiers"]):
                hl = i == sec.get("highlight")
                badge = '<div style="position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:var(--primary);color:var(--primary-text);padding:4px 16px;border-radius:99px;font-size:12px;font-weight:600;">Популярный</div>' if hl else ""
                border = "2px solid var(--primary)" if hl else "1px solid var(--border)"
                btn = 'class="btn"' if hl else 'class="btn ghost"'
                cards += f"""<div class="card" style="position:relative;border:{border};text-align:left;">{badge}
<h3 style="font-size:17px;">{_esc(name)}</h3>
<div style="font-size:30px;font-weight:800;color:var(--primary);margin:14px 0 18px;">{_esc(price)}</div>
<p class="muted" style="font-size:14px;margin-bottom:22px;">Все базовые возможности<br>Поддержка по почте<br>Обновления без доплат</p>
<a {btn} style="display:block;text-align:center;" href="#">Выбрать</a></div>"""
            add(f'<section><div class="wrap"><h2 style="text-align:center;font-size:28px;margin-bottom:34px;">{_esc(sec["title"])}</h2><div class="grid3">{cards}</div></div></section>')
        elif k == "featured_post":
            add(f"""<section><div class="wrap" style="display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center;">
<div style="height:260px;border-radius:var(--radius);background:{_mix(pal['accent'], pal['bg'], 0.75)};"></div>
<div><span style="background:{_mix(pal['primary'], pal['surface'], 0.85)};color:var(--primary);padding:5px 14px;border-radius:99px;font-size:12px;font-weight:600;">Избранное</span>
<h2 style="font-size:26px;margin:16px 0 12px;">{_esc(sec['title'])}</h2>
<p class="muted">Короткое вступление к материалу: о чём он и почему его стоит прочитать.</p>
<div class="muted" style="font-size:13px;margin-top:14px;">Читать 7 минут</div></div></div></section>""")
        elif k == "posts":
            rows = "".join(f"""<div class="card" style="display:flex;gap:18px;align-items:center;">
<div style="width:140px;height:92px;flex:none;border-radius:calc(var(--radius) - 2px);background:{_mix(pal['muted'], pal['bg'], 0.75)};"></div>
<div><h3 style="font-size:16px;margin-bottom:8px;">{_esc(t)}</h3>
<div class="muted" style="font-size:12px;">5 мин · вчера</div></div></div>""" for t in sec["items"])
            tags = "".join(f'<a href="#" style="border:1px solid var(--border);border-radius:99px;padding:6px 14px;font-size:13px;color:var(--muted);text-decoration:none;">#{_esc(t)}</a>' for t in sec["tags"])
            add(f"""<section><div class="wrap" style="display:grid;grid-template-columns:1.8fr 1fr;gap:32px;align-items:start;">
<div style="display:grid;gap:18px;">{rows}</div>
<aside class="card"><h3 style="font-size:16px;margin-bottom:14px;">Темы</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;">{tags}</div></aside></div></section>""")
        elif k == "about":
            add(f"""<section style="background:var(--surface);"><div class="wrap" style="display:grid;grid-template-columns:1fr 1.3fr;gap:48px;align-items:center;">
<div style="height:260px;border-radius:var(--radius);background:{_mix(pal['primary'], pal['surface'], 0.88)};"></div>
<div><h2 style="font-size:28px;margin-bottom:14px;">{_esc(sec['title'])}</h2>
<p class="muted">{_esc(sec['text'])}</p>
<p class="muted" style="margin-top:12px;">Работаем с 2016 года, за плечами — десятки завершённых проектов и команда, которая любит своё дело.</p></div>
</div></section>""")
        elif k == "cta_band":
            add(f"""<div class="wrap" style="padding-bottom:56px;"><div style="background:var(--footer);color:#fff;
border-radius:calc(var(--radius) + 4px);padding:44px 48px;display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap;">
<h2 style="font-size:24px;">{_esc(sec['headline'])}</h2>
<a class="btn accent" href="#">{_esc(sec['cta'])}</a></div></div>""")
        elif k == "newsletter":
            add(f"""<section style="background:var(--surface);"><div class="wrap" style="display:flex;gap:18px;align-items:center;flex-wrap:wrap;">
<h2 style="font-size:20px;flex:1;min-width:240px;">Подпишитесь на рассылку</h2>
<input placeholder="Ваш e-mail" style="flex:2;min-width:220px;padding:12px 16px;border-radius:var(--radius);border:1px solid var(--border);background:var(--bg);color:var(--text);">
<button class="btn">Подписаться</button></div></section>""")
        elif k == "footer":
            cols = "".join(f'<div><div style="font-weight:600;margin-bottom:14px;">{_esc(c)}</div><div style="color:#8A93A8;font-size:14px;line-height:2;">Ссылка<br>Ссылка<br>Ссылка</div></div>' for c in sec["cols"])
            add(f"""<footer style="background:var(--footer);color:#fff;padding:52px 0 30px;">
<div class="wrap" style="display:grid;grid-template-columns:1.2fr repeat({len(sec['cols'])},1fr);gap:28px;">
<strong style="font-size:19px;">{_esc(sec['brand'])}</strong>{cols}</div>
<div class="wrap" style="border-top:1px solid #3A4358;margin-top:36px;padding-top:20px;color:#8A93A8;font-size:13px;">© 2026 · Все права защищены</div>
</footer>""")

    add("</body></html>")
    return "".join(out)


def _html_desktop(spec):
    # окно приложения на нейтральном фоне
    typo = spec["typography"]
    body = (f"<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
            f"<title>Десктоп-шаблон</title></head>"
            f"<body style=\"margin:0;background:#3A3F4A;display:flex;align-items:center;"
            f"justify-content:center;min-height:100vh;font-family:{typo['body_font']};\">"
            f"<div style='box-shadow:0 30px 80px rgba(0,0,0,.45);border-radius:10px;overflow:hidden;'>"
            f"{_svg_from_layout(spec)}</div></body></html>")
    return body


def _svg_from_layout(spec):
    """Точный SVG-рендер графа раскладки (общий для веб- и десктоп-спеков)."""
    pal = spec["palette"]
    W, H = spec["canvas"]["width"], spec["canvas"]["height"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" style="display:block;background:{pal["bg"]};">']

    def draw(n):
        t = n["type"]
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        if t in ("frame", "image", "bar", "button", "chip"):
            fill = n.get("fill", "#FFFFFF")
            rx = n.get("radius", 0)
            stroke = n.get("stroke")
            sw = n.get("stroke_width", 1)
            s_attr = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s_attr}/>')
            if t == "image":
                parts.append(f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y + h}" stroke="#FFFFFF" stroke-opacity="0.35"/>')
                parts.append(f'<line x1="{x + w}" y1="{y}" x2="{x}" y2="{y + h}" stroke="#FFFFFF" stroke-opacity="0.35"/>')
            if t in ("button", "chip") and n.get("label"):
                tc = n.get("text_color", "#FFFFFF")
                fs = 13 if t == "button" else 12
                parts.append(f'<text x="{x + w / 2}" y="{y + h / 2 + fs / 3}" text-anchor="middle" '
                             f'font-family="Segoe UI, sans-serif" font-size="{fs}" '
                             f'font-weight="600" fill="{tc}">{_esc(n["label"])}</text>')
        elif t == "text":
            fs = n.get("size", 14)
            # при anchor=center в x уже лежит центр, так что координата одна на все случаи
            anchor = {"w": "start", "center": "middle", "e": "end"}.get(n.get("anchor", "w"), "start")
            weight = "700" if n.get("bold") else "400"
            fam = "Georgia, serif" if n.get("serif") else "Segoe UI, sans-serif"
            label = _esc(n.get("label", ""))
            wrap = n.get("wrap")
            if wrap and len(label) * fs * 0.55 > wrap:
                # грубый перенос на две строки
                words = label.split()
                mid = len(words) // 2
                l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
                parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" '
                             f'font-size="{fs}" font-weight="{weight}" fill="{n.get("color", "#000")}">'
                             f'<tspan x="{x}" dy="0">{l1}</tspan>'
                             f'<tspan x="{x}" dy="{fs * 1.25}">{l2}</tspan></text>')
            else:
                parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" '
                             f'font-size="{fs}" font-weight="{weight}" '
                             f'fill="{n.get("color", "#000")}">{label}</text>')
        for c in n.get("children", []):
            draw(c)

    for n in spec["layout"]:
        draw(n)
    parts.append("</svg>")
    return "".join(parts)


def spec_to_html(spec):
    if spec["meta"]["project_type"] == "website":
        return _html_website(spec)
    return _html_desktop(spec)
