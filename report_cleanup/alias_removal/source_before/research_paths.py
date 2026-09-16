"""Locate bundled artifacts without rewriting historical manifests."""

from pathlib import Path


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
