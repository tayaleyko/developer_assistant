import sys
import unittest

from tests.helpers import APP_DIR, MODEL_DIR, NESTED_ANSWERS, SAMPLE_WEBSITE_ANSWERS, silence_app_console

sys.path.insert(0, str(APP_DIR))
from services.ai_stub import (
    _flatten_answers,
    _extract_url_from_answer,
    get_offline_result,
)


def _models_ready(platform: str) -> bool:
    return all(
        (MODEL_DIR / f"{platform}_{suffix}").exists()
        for suffix in ("mlp.pkl", "encoder.pkl", "metrics.json")
    )


class TestAiStub(unittest.TestCase):
    """ai_stub — фасад рекомендаций (offline)."""

    def test_flatten_nested_answers(self):
        flat = _flatten_answers(NESTED_ANSWERS)
        self.assertEqual(flat["w2"], "landing")
        self.assertEqual(flat["w_d0"], "commercial")
        self.assertIn("text", flat["w4"])

    def test_flatten_skips_non_dict_blocks(self):
        flat = _flatten_answers({"bad": "value", "ok": {"w2": "saas"}})
        self.assertEqual(flat["w2"], "saas")
        self.assertNotIn("bad", flat)

    def test_extract_url_from_dict(self):
        ans = {"w4": {"value": "yes", "text": "https://example.com"}}
        self.assertEqual(_extract_url_from_answer(ans, "w4"), "https://example.com")

    def test_extract_url_from_string(self):
        ans = {"w4": "https://demo.org"}
        self.assertEqual(_extract_url_from_answer(ans, "w4"), "https://demo.org")

    def test_extract_url_missing(self):
        self.assertIsNone(_extract_url_from_answer({}, "w4"))


@unittest.skipUnless(_models_ready("website"), "Модель website не обучена")
class TestAiStubOfflineIntegration(unittest.TestCase):
    """ai_stub — интеграция с MLP (требует обученных моделей)."""

    def test_get_offline_result_structure(self):
        answers = {"general": dict(SAMPLE_WEBSITE_ANSWERS)}
        with silence_app_console():
            result = get_offline_result(answers, "website")
        self.assertIn("label", result)
        self.assertIn("stack", result)
        self.assertIn("design", result)
        self.assertIn("top3", result)
        self.assertIsInstance(result["top3"], list)
        self.assertLessEqual(len(result["top3"]), 3)

    def test_get_offline_result_stack_not_empty_for_known_label(self):
        answers = {"general": dict(SAMPLE_WEBSITE_ANSWERS)}
        with silence_app_console():
            result = get_offline_result(answers, "website")
        if result["label"] in ("gatsby_netlify", "nextjs_vercel"):
            self.assertTrue(result["stack"])


if __name__ == "__main__":
    unittest.main()
