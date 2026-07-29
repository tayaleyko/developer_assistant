import sys
import unittest

from tests.helpers import APP_DIR, MODEL_DIR, SAMPLE_WEBSITE_ANSWERS, silence_app_console

sys.path.insert(0, str(APP_DIR))
from services.mlp_model import predict_stack, predict_stack_ensemble


def _models_ready(platform: str) -> bool:
    return all(
        (MODEL_DIR / f"{platform}_{suffix}").exists()
        for suffix in ("mlp.pkl", "encoder.pkl", "metrics.json")
    )


@unittest.skipUnless(_models_ready("website"), "Модель website не обучена")
class TestMlpModelWebsite(unittest.TestCase):

    def test_predict_stack_returns_label_and_top3(self):
        with silence_app_console():
            label, top3 = predict_stack(SAMPLE_WEBSITE_ANSWERS, "website")
        self.assertIsInstance(label, str)
        self.assertTrue(label)
        self.assertEqual(len(top3), 3)
        self.assertTrue(all(isinstance(p, float) for _, p in top3))

    def test_predict_stack_landing_profile(self):
        with silence_app_console():
            label, _ = predict_stack(SAMPLE_WEBSITE_ANSWERS, "website")
        self.assertEqual(label, "gatsby_netlify")

    def test_top3_probabilities_descending(self):
        with silence_app_console():
            _, top3 = predict_stack(SAMPLE_WEBSITE_ANSWERS, "website")
        probs = [p for _, p in top3]
        self.assertEqual(probs, sorted(probs, reverse=True))

    def test_ensemble_returns_same_structure(self):
        with silence_app_console():
            label, top3 = predict_stack_ensemble(SAMPLE_WEBSITE_ANSWERS, "website")
        self.assertIsInstance(label, str)
        self.assertEqual(len(top3), 3)


@unittest.skipUnless(_models_ready("desktop"), "Модель desktop не обучена")
class TestMlpModelDesktop(unittest.TestCase):
    """mlp_model — предсказание стека (desktop)."""

    def test_predict_stack_runs(self):
        answers = {
            "d2": "utility",
            "d3": "windows",
            "d4": "no",
            "d5": "no",
            "d6": "1month",
            "d7": "50k",
            "d8": "1k",
            "d9": "no",
            "d10": "simple",
            "d11": "no",
            "d12": "local",
            "d13": "no",
            "d14": "no",
            "d_d0": "other",
        }
        with silence_app_console():
            label, top3 = predict_stack(answers, "desktop")
        self.assertIsInstance(label, str)
        self.assertEqual(len(top3), 3)


if __name__ == "__main__":
    unittest.main()
