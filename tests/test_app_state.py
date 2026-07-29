import sys
import unittest

from tests.helpers import APP_DIR

sys.path.insert(0, str(APP_DIR))
from models import Block, Question, Option
from state import AppState


def _make_block(block_id: str, n_questions: int) -> Block:
    questions = [
        Question(id=f"{block_id}_q{i}", text=f"Q{i}", type="single", options=[Option("a", "A")])
        for i in range(n_questions)
    ]
    return Block(id=block_id, title=block_id, order=1, questions=questions)


class TestAppState(unittest.TestCase):
    """AppState — состояние сессии и полнота блоков."""

    def setUp(self):
        self.state = AppState()
        self.state.set_blocks([
            _make_block("general", 2),
            _make_block("tech", 3),
        ])

    def test_block_incomplete_when_empty(self):
        self.assertFalse(self.state.is_block_complete("general"))

    def test_block_complete_when_all_answered(self):
        self.state.answers["general"] = {"general_q0": "a", "general_q1": "a"}
        self.assertTrue(self.state.is_block_complete("general"))

    def test_block_incomplete_with_partial_answers(self):
        self.state.answers["general"] = {"general_q0": "a"}
        self.assertFalse(self.state.is_block_complete("general"))

    def test_unknown_block_not_complete(self):
        self.assertFalse(self.state.is_block_complete("missing"))

    def test_has_any_complete_block(self):
        self.assertFalse(self.state.has_any_complete_block())
        self.state.answers["general"] = {"general_q0": "a", "general_q1": "a"}
        self.assertTrue(self.state.has_any_complete_block())

    def test_to_dict_and_load_dict(self):
        self.state.project_type = "website"
        self.state.answers["general"] = {"general_q0": "a"}
        data = self.state.to_dict()
        other = AppState()
        other.load_dict(data)
        self.assertEqual(other.project_type, "website")
        self.assertEqual(other.answers, self.state.answers)

    def test_clear_resets_session(self):
        self.state.project_type = "desktop"
        self.state.answers["general"] = {"general_q0": "a"}
        self.state.clear()
        self.assertIsNone(self.state.project_type)
        self.assertEqual(self.state.answers, {})
        self.assertEqual(self.state.blocks, [])


if __name__ == "__main__":
    unittest.main()
