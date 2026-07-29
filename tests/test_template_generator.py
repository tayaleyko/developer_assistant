# Тесты модуля генерации интерфейсных шаблонов.

import json
import unittest

import tests.helpers  # noqa: F401  (настраивает sys.path)

from services.template_generator import (
    generate_template, spec_to_html, spec_to_json, flatten_answers,
    CANVAS_W, DESKTOP_W, DESKTOP_H,
)

SITE_TYPES = ["landing", "corporate", "ecommerce", "news", "saas", "blog"]
STYLES = ["minimalist", "corporate", "creative", "friendly", "unknown"]
NAVS_W = ["top", "sidebar", "burger", "unknown"]
NAVS_D = ["tabs", "sidebar", "tree", "ribbon", "unknown"]
SPHERES = ["finance", "medical", "food", "creative", "gov", "other"]


def _website_answers(site_type="landing", style="corporate", nav="top",
                     sphere="finance", dark="no", a11y="nice"):
    return {
        "general": {"w1": "commercial", "w2": site_type},
        "design": {
            "w_d0": sphere, "w_d1": "no", "w_d2": "no", "w_d3": "no",
            "w_d4": {"value": "no", "text": ""},
            "w_d5": style, "w_d6": "2-5", "w_d7": nav,
            "w_d8": dark, "w_d9": "subtle", "w_d10": a11y, "w_d11": "unknown",
        },
    }


def _desktop_answers(nav="sidebar", sphere="finance", ds="fluent"):
    return {
        "general": {"d1": "commercial", "d2": "business"},
        "design": {
            "d_d0": sphere, "d_d1": "no", "d_d2": "select", "d_d3": ds,
            "d_d4": "no", "d_d5": nav, "d_d6": "no", "d_d7": "subtle",
            "d_d8": "nice", "d_d9": "basic", "d_d10": "tooltips",
        },
    }


def _walk(nodes):
    for n in nodes:
        yield n
        for c in n.get("children", []):
            yield from _walk([c])


class TestTemplateGenerator(unittest.TestCase):

    # ---------------------------------------------------------- базовое
    def test_flatten_answers(self):
        flat = flatten_answers(_website_answers())
        self.assertEqual(flat["w2"], "landing")
        self.assertEqual(flat["w_d5"], "corporate")

    def test_website_spec_structure(self):
        spec = generate_template(_website_answers(), "website")
        for key in ("meta", "palette", "typography", "sections", "canvas", "layout"):
            self.assertIn(key, spec)
        self.assertEqual(spec["meta"]["project_type"], "website")
        self.assertGreater(len(spec["layout"]), 0)
        self.assertGreater(spec["canvas"]["height"], 500)

    # ---------------------------------------------------------- матрица
    def test_all_site_types_and_styles(self):
        for st in SITE_TYPES:
            for style in STYLES:
                spec = generate_template(
                    _website_answers(site_type=st, style=style), "website")
                self.assertGreater(len(spec["sections"]), 2, f"{st}/{style}")
                # у любого сайта есть навигация и футер
                kinds = [s["kind"] for s in spec["sections"]]
                self.assertIn("navbar", kinds, f"{st}/{style}")
                self.assertIn("footer", kinds, f"{st}/{style}")

    def test_all_navs_website(self):
        for nav in NAVS_W:
            spec = generate_template(_website_answers(nav=nav), "website")
            self.assertGreater(len(spec["layout"]), 0, nav)
            if nav == "sidebar":
                ids = [n.get("id") for n in spec["layout"]]
                self.assertIn("side_nav", ids)

    def test_all_navs_desktop(self):
        for nav in NAVS_D:
            spec = generate_template(_desktop_answers(nav=nav), "desktop")
            self.assertEqual(spec["canvas"]["width"], DESKTOP_W)
            self.assertEqual(spec["canvas"]["height"], DESKTOP_H)
            ids = [n.get("id") for n in spec["layout"]]
            self.assertIn("titlebar", ids, nav)
            self.assertIn("statusbar", ids, nav)
            if nav == "ribbon":
                self.assertIn("ribbon", ids)
            elif nav == "tabs":
                self.assertIn("tabstrip", ids)

    def test_all_spheres_have_distinct_palettes(self):
        primaries = set()
        for sp in SPHERES:
            spec = generate_template(_website_answers(sphere=sp), "website")
            primaries.add(spec["palette"]["primary"])
        self.assertGreater(len(primaries), len(SPHERES) - 2)

    # ---------------------------------------------------------- геометрия
    def test_nodes_within_canvas(self):
        for st in SITE_TYPES:
            spec = generate_template(_website_answers(site_type=st), "website")
            W = spec["canvas"]["width"]
            H = spec["canvas"]["height"]
            for n in _walk(spec["layout"]):
                if n["type"] == "text":
                    continue  # текст может выравниваться по центру/якорю
                self.assertGreaterEqual(n["x"], -1, f"{st}: {n}")
                self.assertLessEqual(n["x"] + n["w"], W + 1, f"{st}: {n}")
                self.assertLessEqual(n["y"] + n["h"], H + 1, f"{st}: {n}")

    def test_desktop_nodes_within_window(self):
        for nav in NAVS_D:
            spec = generate_template(_desktop_answers(nav=nav), "desktop")
            for n in _walk(spec["layout"]):
                if n["type"] == "text":
                    continue
                self.assertLessEqual(n["y"] + n["h"], DESKTOP_H + 1, f"{nav}: {n}")

    # ---------------------------------------------------------- условия
    def test_constraint_dark_mode(self):
        spec = generate_template(_website_answers(dark="yes"), "website")
        self.assertIsNotNone(spec["palette_dark"])
        spec2 = generate_template(_website_answers(dark="no"), "website")
        self.assertIsNone(spec2["palette_dark"])

    def test_constraint_accessibility_contrast(self):
        spec = generate_template(_website_answers(a11y="yes"), "website")
        # УСИЛЕННЫЙ контраст: текст темнее обычного
        self.assertEqual(spec["palette"]["text"], "#0B1220")
        html = spec_to_html(spec)
        self.assertIn("focus-visible", html)

    def test_seed_variation_and_determinism(self):
        a = _website_answers(site_type="ecommerce")
        s0 = generate_template(a, "website", seed=0)
        s0b = generate_template(a, "website", seed=0)
        self.assertEqual(spec_to_json(s0), spec_to_json(s0b))  # воспроизводимость

    def test_palette_override(self):
        spec = generate_template(
            _website_answers(), "website",
            palette_override=["#112233", "#AABBCC"])
        self.assertEqual(spec["palette"]["accent"], "#AABBCC")

    # ---------------------------------------------------------- экспорт
    def test_json_roundtrip(self):
        spec = generate_template(_website_answers(), "website")
        data = json.loads(spec_to_json(spec))
        self.assertEqual(data["meta"]["site_type"], "landing")

    def test_html_export_website(self):
        for st in SITE_TYPES:
            spec = generate_template(_website_answers(site_type=st), "website")
            html = spec_to_html(spec)
            self.assertIn("<!doctype html>", html.lower(), st)
            self.assertIn("lang=\"ru\"", html, st)
            # в HTML попал заголовок/бренд из секций
            self.assertIn(spec["sections"][0]["brand"], html, st)

    def test_html_export_desktop(self):
        spec = generate_template(_desktop_answers(), "desktop")
        html = spec_to_html(spec)
        self.assertIn("<svg", html)
        self.assertIn("FinDesk", html)


if __name__ == "__main__":
    unittest.main()
