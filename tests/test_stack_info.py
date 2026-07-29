import sys
import unittest

from tests.helpers import APP_DIR, SAMPLE_WEBSITE_ANSWERS

sys.path.insert(0, str(APP_DIR))
from services.stack_info import get_stack, get_design, WEBSITE_STACKS, DESKTOP_STACKS

class TestStackInfo(unittest.TestCase):

    def test_get_stack_website_known_label(self):
        stack = get_stack("gatsby_netlify", "website")
        self.assertIn("Frontend", stack)
        self.assertIn("Хостинг", stack)
        self.assertIn("Gatsby", stack["Frontend"])

    def test_get_stack_desktop_known_label(self):
        stack = get_stack("electron_js", "desktop")
        self.assertIn("Frontend", stack)
        self.assertIn("Electron", stack["Frontend"])

    def test_get_stack_unknown_returns_empty(self):
        self.assertEqual(get_stack("nonexistent_label", "website"), {})

    def test_all_website_labels_have_frontend(self):
        for label in WEBSITE_STACKS:
            self.assertIn("Frontend", get_stack(label, "website"))

    def test_all_desktop_labels_have_frontend(self):
        for label in DESKTOP_STACKS:
            self.assertIn("Frontend", get_stack(label, "desktop"))

    def test_get_design_website_commercial(self):
        design = get_design("commercial", "website", SAMPLE_WEBSITE_ANSWERS)
        self.assertIsInstance(design, dict)
        self.assertTrue(design)

    def test_get_design_desktop_other(self):
        design = get_design("other", "desktop", {})
        self.assertIsInstance(design, dict)
        self.assertTrue(design)


if __name__ == "__main__":
    unittest.main()
