import sys
import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from tests.helpers import APP_DIR

sys.path.insert(0, str(APP_DIR))
from services import site_analyzer
from services.site_analyzer import (
    _detect_technologies,
    _extract_colors_from_html,
    _analyze_design,
    analyze_site,
)


class TestSiteAnalyzer(unittest.TestCase):

    def test_detect_nextjs(self):
        html = '<html><script id="__NEXT_DATA__">{}</script></html>'
        soup = BeautifulSoup(html, "html.parser")
        tech = _detect_technologies(soup, html, {})
        self.assertIn("Next.js", tech["Фреймворк"])

    def test_detect_php_backend(self):
        html = "<html></html>"
        soup = BeautifulSoup(html, "html.parser")
        headers = {"X-Powered-By": "PHP/8.2"}
        tech = _detect_technologies(soup, html, headers)
        self.assertEqual(tech["Backend"], "PHP")

    def test_detect_yandex_metrika(self):
        html = '<html><script src="https://mc.yandex.ru/metrika/tag.js"></script></html>'
        soup = BeautifulSoup(html, "html.parser")
        tech = _detect_technologies(soup, html, {})
        self.assertIn("Яндекс.Метрика", tech["Аналитика"])

    def test_extract_colors_hex_and_rgb(self):
        html = '<div style="color:#ff0000; background: rgb(0, 128, 255)"></div>'
        colors = _extract_colors_from_html(html)
        self.assertIn("ff0000", colors)
        self.assertIn("0080ff", colors)

    def test_analyze_design_bootstrap_hint(self):
        html = '<html><body><div class="btn-primary container">x</div></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        design = _analyze_design(soup, html.lower())
        self.assertIn("UI-библиотека", design)

    @patch("services.site_analyzer.requests.get")
    def test_analyze_site_success(self, mock_get):
        html = (
            '<html><head></head><body>'
            '<script id="__NEXT_DATA__">{}</script>'
            '</body></html>'
        )
        response = MagicMock()
        response.text = html
        response.headers = {"Server": "Vercel"}
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        result = analyze_site("https://example.com")
        self.assertNotIn("error", result)
        self.assertIn("technologies", result)
        self.assertIn("design", result)
        self.assertIn("Next.js", result["technologies"]["Фреймворк"])

    @patch("services.site_analyzer.requests.get")
    def test_analyze_site_network_error(self, mock_get):
        mock_get.side_effect = ConnectionError("offline")
        result = analyze_site("https://example.com")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
