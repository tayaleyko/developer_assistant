import sys
import unittest

from tests.helpers import APP_DIR, QUESTIONS_PATH

sys.path.insert(0, str(APP_DIR))
from loader import load_json, load_initial_question, load_blocks

class TestLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_json(QUESTIONS_PATH)

    def test_load_json_returns_initial_question(self):
        self.assertIn("initialQuestion", self.data)

    def test_load_initial_question(self):
        q = load_initial_question(self.data)
        self.assertEqual(q.id, "platform")
        self.assertEqual(q.type, "single")
        self.assertGreaterEqual(len(q.options), 2)

    def test_load_blocks_website_sorted(self):
        blocks = load_blocks(self.data, "website")
        self.assertGreater(len(blocks), 0)
        orders = [b.order for b in blocks]
        self.assertEqual(orders, sorted(orders))

    def test_load_blocks_desktop(self):
        blocks = load_blocks(self.data, "desktop")
        self.assertGreater(len(blocks), 0)
        self.assertTrue(all(b.questions for b in blocks))

    def test_question_options_have_labels(self):
        blocks = load_blocks(self.data, "website")
        first_q = blocks[0].questions[0]
        self.assertTrue(first_q.options)
        self.assertTrue(first_q.options[0].label)


if __name__ == "__main__":
    unittest.main()
