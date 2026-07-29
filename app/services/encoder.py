import pandas as pd
import joblib


class SurveyEncoder:
    """One-hot кодирование ответов анкеты и меток стека."""

    def __init__(self):
        self.feature_cols = []
        self.onehot_columns = []
        self.label_map = {}
        self.label_map_inv = {}

    def fit(self, df):
        self.feature_cols = [c for c in df.columns if c != "label"]
        self.onehot_columns = list(
            pd.get_dummies(df[self.feature_cols], dtype=float).columns
        )

        labels = sorted(df["label"].unique())
        self.label_map = {lab: i for i, lab in enumerate(labels)}
        self.label_map_inv = {i: lab for lab, i in self.label_map.items()}
        return self

    def transform(self, df):
        X = pd.get_dummies(df[self.feature_cols], dtype=float)
        return X.reindex(columns=self.onehot_columns, fill_value=0.0).values

    def transform_target(self, df):
        return df["label"].map(self.label_map).values

    def encode_answers(self, answers_flat):
        row = {}
        for col in self.feature_cols:
            val = answers_flat.get(col, "unknown")
            if isinstance(val, dict):
                val = val.get("value", "unknown")
            if isinstance(val, list):
                val = val[0] if len(val) == 1 else "all"
            row[col] = str(val)

        X = pd.get_dummies(pd.DataFrame([row]), dtype=float)
        return X.reindex(columns=self.onehot_columns, fill_value=0.0).values

    def decode_label(self, idx):
        return self.label_map_inv.get(idx, "unknown")

    @property
    def n_classes(self):
        return len(self.label_map)

    def save(self, path):
        joblib.dump(self, path)

    @staticmethod
    def load(path):
        return joblib.load(path)
