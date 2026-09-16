"""Locate bundled artifacts without rewriting historical manifests."""

from pathlib import Path


LEGACY_FOLDERS = {
    "main_first": "exploratory_prototype",
    "main": "classical_corrosion",
    "main_2": "image_embeddings",
    "main_3": "condition_assessment",
    "main_4": "structural_capacity",
    "augmentation": "classification_data_preparation",
    "main_4_old": "archive/structural_baseline_snapshot",
}


def resolve_project_path(recorded_path: str | Path, project_root: Path | None = None) -> Path:
    """Translate a recorded repository path to the current layout.

    Legacy experiment roots, report paths and the former emiling collection are mapped.
    Report audit paths resolve directly to the archive, without a shortcut directory.
    Historical names embedded in other directories stay unchanged. Paths must
    remain inside this checkout;
    paths from another computer are not guessed or silently relocated.
    Existence is checked by the reader, so this also supports new output paths.
    """
    root = (project_root or Path(__file__).parent).resolve()
    path = Path(recorded_path)
    if path.is_absolute():
        path = path.relative_to(root)
    if path.parts and path.parts[0] == "report_cleanup":
        path = Path("archive/repository_maintenance", *path.parts[1:])
    elif path.parts and path.parts[0] in {"report_v2", "final_reports"}:
        parts = list(path.parts[1:])
        if parts and parts[0] in {"thesis", "article"}:
            kind, *remaining = parts
            if remaining[:1] == ["v3"]:
                remaining = remaining[1:]
            if remaining == [kind + ".pdf"]:
                parts = [kind + ".pdf"]
            elif kind == "thesis" and remaining == ["FIGURE_AUDIT.md"]:
                parts = ["records", "thesis", "v3", "FIGURE_AUDIT.md"]
            else:
                parts = ["sources", kind, *remaining]
        elif parts and parts[0] in {"evidence", "qa", "critique", "FINAL_VERIFICATION.md",
                                   "RESEARCH_NOTES.md", "VERIFICATION_LOG.md"}:
            parts = ["records", *parts]
        if parts[:1] == ["records"]:
            path = Path("archive/agent_working_notes/report_v2", *parts[1:])
        else:
            path = Path("final_reports", *parts)
    elif path.parts and path.parts[0] == "emiling":
        parts = list(path.parts[1:])
        if parts:
            parts[0] = {"main_3": "condition_assessment", "main_4": "structural_capacity"}.get(parts[0], parts[0])
        path = Path("selected_results", *parts)
    elif path.parts:
        path = Path(LEGACY_FOLDERS.get(path.parts[0], path.parts[0]), *path.parts[1:])
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Recorded path escapes the project: {recorded_path}")
    return resolved


def resolve_artifact_path(recorded_path: str | Path, artifacts_dir: Path) -> Path:
    """Keep a valid recorded path; otherwise use its filename in this bundle.

    Historical manifests contain absolute paths from earlier checkouts. Only the
    explicitly supplied artifacts directory is searched for a relocated file.
    Missing files remain errors; no manifest or serialized model is modified.
    """
    recorded = Path(recorded_path)
    if recorded.is_file():
        return recorded.resolve()

    bundled = Path(artifacts_dir) / recorded.name
    if bundled.is_file():
        return bundled.resolve()

    raise FileNotFoundError(
        f"Artifact unavailable at recorded path {recorded} or bundled path {bundled}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Locate a historical repository path in the current folders.")
    parser.add_argument("path", help="Recorded repository-relative path")
    args = parser.parse_args()
    try:
        result = resolve_project_path(args.path)
    except ValueError as exc:
        parser.error(str(exc))
    if not result.exists():
        parser.error(f"No file or directory at mapped path: {result}")
    print(result)
