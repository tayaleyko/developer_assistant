import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import APP_DIR

sys.path.insert(0, str(APP_DIR))
import storage


class TestStorage(unittest.TestCase):
    """storage — сохранение и загрузка прогресса."""

    def test_save_and_load_progress(self):
        payload = {
            "project_type": "website",
            "answers": {"general": {"w2": "landing"}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            progress_file = Path(tmp) / "progress.json"
            with patch.object(storage, "PROGRESS_FILE", progress_file):
                storage.save_progress(payload)
                self.assertTrue(progress_file.exists())
                loaded = storage.load_progress()
                self.assertEqual(loaded, payload)

    def test_load_progress_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress_file = Path(tmp) / "missing.json"
            with patch.object(storage, "PROGRESS_FILE", progress_file):
                self.assertIsNone(storage.load_progress())

    def test_saved_json_is_utf8(self):
        payload = {"project_type": "website", "answers": {"b": {"q": "да"}}}
        with tempfile.TemporaryDirectory() as tmp:
            progress_file = Path(tmp) / "progress.json"
            with patch.object(storage, "PROGRESS_FILE", progress_file):
                storage.save_progress(payload)
                text = progress_file.read_text(encoding="utf-8")
                self.assertIn("да", text)
                self.assertEqual(json.loads(text), payload)


if __name__ == "__main__":
    unittest.main()
