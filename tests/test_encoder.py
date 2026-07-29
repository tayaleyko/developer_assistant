import tempfile
import unittest
from pathlib import Path

import pandas as pd

from tests.helpers import APP_DIR, ROOT

import sys

sys.path.insert(0, str(APP_DIR))
from services.encoder import SurveyEncoder


class TestSurveyEncoder(unittest.TestCase):
    """SurveyEncoder — кодирование ответов опроса."""

    @classmethod
    def setUpClass(cls):
        df = pd.read_csv(ROOT / "data" / "website.csv")
        cls.encoder = SurveyEncoder()
        cls.encoder.fit(df)
        cls.sample_row = df.iloc[0]

    def test_fit_sets_feature_columns(self):
        self.assertGreater(len(self.encoder.feature_cols), 0)
        self.assertNotIn("label", self.encoder.feature_cols)

    def test_transform_shape_matches_onehot(self):
        df = pd.read_csv(ROOT / "data" / "website.csv").head(3)
        matrix = self.encoder.transform(df)
        self.assertEqual(matrix.shape[0], 3)
        self.assertEqual(matrix.shape[1], len(self.encoder.onehot_columns))

    def test_encode_missing_keys_as_unknown(self):
        unknown_row = {col: "unknown" for col in self.encoder.feature_cols}
        expected = self.encoder.encode_answers(unknown_row)
        actual = self.encoder.encode_answers({})
        self.assertTrue((expected == actual).all())

    def test_encode_dict_value(self):
        answers = dict(self.sample_row.drop("label"))
        answers["w4"] = {"value": "yes", "text": "https://site.ru"}
        vector = self.encoder.encode_answers(answers)
        self.assertEqual(vector.shape[1], len(self.encoder.onehot_columns))
        self.assertGreater(float(vector.sum()), 0.0)

    def test_encode_list_single_value(self):
        vector = self.encoder.encode_answers({"w2": ["landing"]})
        self.assertGreater(float(vector.sum()), 0.0)

    def test_encode_list_multiple_becomes_all(self):
        single = self.encoder.encode_answers({"w13": ["responsive"]})
        multi = self.encoder.encode_answers({"w13": ["responsive", "adaptive"]})
        self.assertFalse((single == multi).all())

    def test_decode_label_roundtrip(self):
        idx = self.encoder.label_map["gatsby_netlify"]
        self.assertEqual(self.encoder.decode_label(idx), "gatsby_netlify")

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "encoder.pkl"
            self.encoder.save(path)
            loaded = SurveyEncoder.load(path)
            self.assertEqual(loaded.feature_cols, self.encoder.feature_cols)
            self.assertEqual(loaded.onehot_columns, self.encoder.onehot_columns)


if __name__ == "__main__":
    unittest.main()
