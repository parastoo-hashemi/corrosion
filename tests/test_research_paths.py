"""Checks for relocation of artifact bundles; no model loading or fitting."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from corrosion.research_paths import LEGACY_FOLDERS, resolve_artifact_path, resolve_project_path


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


class ProjectPathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def test_all_old_roots_resolve_without_symlinks(self):
        for old, new in LEGACY_FOLDERS.items():
            target = self.root / new / "result.csv"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("preserved")
            self.assertEqual(resolve_project_path(old + "/result.csv", self.root), target)
            self.assertFalse((self.root / old).exists())

    def test_canonical_names_stay_unchanged(self):
        path = "structural_capacity/outputs/result.csv"
        self.assertEqual(resolve_project_path(path, self.root), self.root / path)

    def test_embedded_archive_names_stay_unchanged(self):
        for path in ["archive/agent_working_notes/main_4/README.md", "archive/emiling/main_3/plot.png"]:
            self.assertEqual(resolve_project_path(path, self.root), self.root / path)

    def test_selected_collection_old_paths_resolve_to_preserved_files(self):
        for old, new in [
            ("emiling/main_3/plot.png", "selected_results/condition_assessment/plot.png"),
            ("emiling/main_4/metadata_only+Ridge/plot.png", "selected_results/structural_capacity/metadata_only+Ridge/plot.png"),
            ("emiling/other.txt", "selected_results/other.txt"),
        ]:
            target = self.root / new
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"preserved")
            self.assertEqual(resolve_project_path(old, self.root), target)
            self.assertEqual(resolve_project_path(self.root / old, self.root), target)
            self.assertEqual(resolve_project_path(new, self.root), target)
            self.assertFalse((self.root / old).exists())
        self.assertEqual(resolve_project_path("emiling", self.root), self.root / "selected_results")

    def test_selected_collection_parent_traversal_is_rejected(self):
        for path in ["emiling/../../outside.csv", "emiling/main_3/../../../outside.csv"]:
            with self.assertRaises(ValueError):
                resolve_project_path(path, self.root)

    def test_same_checkout_absolute_path_is_mapped(self):
        self.assertEqual(resolve_project_path(self.root / "main/model.joblib", self.root),
                         self.root / "classical_corrosion/model.joblib")

    def test_unrelated_absolute_path_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_project_path(self.root.parent / "another_checkout/main/model.joblib", self.root)

    def test_parent_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_project_path("../../outside.csv", self.root)

    def test_partial_name_is_not_replaced(self):
        for path in ["main_4_extra/result.csv", "emiling_extra/main_3/plot.png"]:
            self.assertEqual(resolve_project_path(path, self.root), self.root / path)
        self.assertEqual(resolve_project_path("emiling/main_3_extra/plot.png", self.root),
                         self.root / "selected_results/main_3_extra/plot.png")

    def test_report_delivery_and_source_paths(self):
        cases = {
            "report_v2": "final_reports",
            "report_v2/thesis/v3/thesis.pdf": "final_reports/thesis.pdf",
            "report_v2/article/v3/article.pdf": "final_reports/article.pdf",
            "report_v2/thesis/v3/thesis.tex": "final_reports/sources/thesis/thesis.tex",
            "report_v2/article/v3/article.tex": "final_reports/sources/article/article.tex",
            "report_v2/thesis/v3/chapters/01_introduction.tex": "final_reports/sources/thesis/chapters/01_introduction.tex",
            "report_v2/thesis/README.md": "final_reports/sources/thesis/README.md",
            "report_v2/figures/example.pdf": "final_reports/figures/example.pdf",
        }
        for old, new in cases.items():
            self.assertEqual(resolve_project_path(old, self.root), self.root / new)
            self.assertEqual(resolve_project_path(self.root / old, self.root), self.root / new)
            self.assertEqual(resolve_project_path(new, self.root), self.root / new)

    def test_report_records_use_the_preserved_archive(self):
        archive = self.root / "archive/agent_working_notes/report_v2"
        archive.mkdir(parents=True)
        (self.root / "final_reports").mkdir()
        cases = {
            "report_v2/evidence/v3/check.json": "evidence/v3/check.json",
            "report_v2/qa/v3/plot.png": "qa/v3/plot.png",
            "report_v2/critique/review.md": "critique/review.md",
            "report_v2/FINAL_VERIFICATION.md": "FINAL_VERIFICATION.md",
            "report_v2/RESEARCH_NOTES.md": "RESEARCH_NOTES.md",
            "report_v2/VERIFICATION_LOG.md": "VERIFICATION_LOG.md",
            "report_v2/thesis/v3/FIGURE_AUDIT.md": "thesis/v3/FIGURE_AUDIT.md",
        }
        for old, relative in cases.items():
            target = archive / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("preserved")
            self.assertEqual(resolve_project_path(old, self.root), target)
            self.assertEqual(resolve_project_path(self.root / old, self.root), target)
            self.assertEqual(resolve_project_path("final_reports/records/" + relative, self.root), target)
            self.assertEqual(resolve_project_path(self.root / "final_reports/records" / relative, self.root), target)
            self.assertEqual(resolve_project_path(target, self.root), target)
        self.assertEqual(resolve_project_path("final_reports/records", self.root), archive)
        self.assertFalse((self.root / "final_reports/records").exists())

    def test_report_mapping_boundaries(self):
        for path in ["report_v2_extra/thesis/v3/thesis.pdf", "archive/report_v2/thesis/v3/thesis.pdf"]:
            self.assertEqual(resolve_project_path(path, self.root), self.root / path)
        for path in ["report_v2/../../outside.txt", "report_v2/thesis/v3/../../../../outside.txt"]:
            with self.assertRaises(ValueError):
                resolve_project_path(path, self.root)

    def test_maintenance_records_resolve_without_a_root_shortcut(self):
        for suffix in ["", "renaming/files_before.json", "records_shortcut/verification.json",
                       "renaming/source_before/report_cleanup/verify_delivery.py"]:
            old = Path("report_cleanup") / suffix
            target = self.root / "archive/repository_maintenance" / suffix
            self.assertEqual(resolve_project_path(old, self.root), target)
            self.assertEqual(resolve_project_path(self.root / old, self.root), target)
            self.assertEqual(resolve_project_path(target, self.root), target)
        self.assertFalse((self.root / "report_cleanup").exists())
        for name in ["report_cleanup_extra/file.json", "archive/report_cleanup/file.json"]:
            self.assertEqual(resolve_project_path(name, self.root), self.root / name)
        with self.assertRaises(ValueError):
            resolve_project_path("report_cleanup/../../../outside.json", self.root)


if __name__ == "__main__":
    unittest.main()
