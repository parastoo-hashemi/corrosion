"""Checks for relocation of artifact bundles; no model loading or fitting."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from corrosion.research_paths import resolve_artifact_path


class ArtifactPathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bundle = self.root / "artifacts"
        self.bundle.mkdir()

    def test_existing_recorded_file_keeps_precedence(self):
        original = self.root / "model.joblib"
        original.write_bytes(b"recorded")
        (self.bundle / original.name).write_bytes(b"local")
        self.assertEqual(resolve_artifact_path(original, self.bundle), original.resolve())

    def test_stale_absolute_path_uses_specified_bundle(self):
        local = self.bundle / "model.joblib"
        local.write_bytes(b"saved model")
        stale = self.root / "previous_checkout" / local.name
        self.assertEqual(resolve_artifact_path(str(stale), self.bundle), local.resolve())
        self.assertEqual(local.read_bytes(), b"saved model")
        self.assertFalse(stale.exists())

    def test_filename_is_relative_to_supplied_bundle(self):
        local = self.bundle / "model.joblib"
        local.touch()
        self.assertEqual(resolve_artifact_path(local.name, self.bundle), local.resolve())

    def test_missing_model_does_not_search_another_bundle(self):
        elsewhere = self.root / "other_experiment"
        elsewhere.mkdir()
        (elsewhere / "model.joblib").touch()
        with self.assertRaises(FileNotFoundError):
            resolve_artifact_path(self.root / "missing" / "model.joblib", self.bundle)

    def test_directory_is_not_accepted_as_artifact(self):
        (self.bundle / "model.joblib").mkdir()
        with self.assertRaises(FileNotFoundError):
            resolve_artifact_path(self.root / "missing" / "model.joblib", self.bundle)


if __name__ == "__main__":
    unittest.main()
