#!/usr/bin/env python3
"""Create leakage-free specimen-level train/validation/test manifests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_CSV = PROJECT_ROOT / "Data" / "Images_Dataset_A-Z-1_augmented.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "Data" / "splits"
DEFAULT_REPORT = PROJECT_ROOT / "Documentation" / "codex" / "split_report.md"

TRAIN_SPECIMENS = [
    "D01",
    "D02",
    "D03",
    "E01",
    "E05",
    "E06",
    "F01",
    "G01",
    "G03",
    "G04",
    "G05",
    "G06",
    "S1MI07",
    "S2SA02",
    "E02",
    "E03",
    "E04",
    "F02",
    "F03",
    "F04",
    "F05",
    "F06",
    "G02",
    "S1MI01",
    "S1MI02",
    "S1MI03",
    "S1MI06",
    "S2SA01",
    "S2SA04",
    "S2SA05",
    "S3PA01",
    "S3PA03",
    "D05",
    "D06",
    "S2SA06",
    "D04",
    "S1MI04",
    "S1MI05",
]

VAL_SPECIMENS = [
    "S3PA02",
    "S4SAVF01",
    "S4SAVF02",
    "S2SA07",
    "S2SA03",
]

TEST_SPECIMENS = [
    "S3PA04",
    "S5VF01",
    "S5VF03",
    "S5VF02",
    "S4SAVF03",
]

EXPECTED_STRATA = {
    1: {
        "D01",
        "D02",
        "D03",
        "E01",
        "E05",
        "E06",
        "F01",
        "G01",
        "G03",
        "G04",
        "G05",
        "G06",
        "S1MI07",
        "S2SA02",
        "S3PA02",
        "S3PA04",
    },
    2: {
        "E02",
        "E03",
        "E04",
        "F02",
        "F03",
        "F04",
        "F05",
        "F06",
        "G02",
        "S1MI01",
        "S1MI02",
        "S1MI03",
        "S1MI06",
        "S2SA01",
        "S2SA04",
        "S2SA05",
        "S3PA01",
        "S3PA03",
        "S4SAVF01",
        "S4SAVF02",
        "S5VF01",
        "S5VF03",
    },
    3: {"D05", "D06", "S2SA06", "S2SA07", "S5VF02"},
    4: {"D04", "S1MI04", "S1MI05", "S2SA03", "S4SAVF03"},
}

REQUIRED_COLUMNS = {
    "original_image_name",
    "augmented_image_name",
    "image_path",
    "original_image_path",
    "label",
    "augmentation_id",
    "augmentation_type",
    "augmentation_parameters",
    "is_augmented",
    "specimen_id",
    "A_Total_Rust_Category_(1–4)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create hardcoded, severity-stratified, specimen-level split manifests "
            "for the offline-augmented corrosion image dataset."
        )
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=DEFAULT_INPUT_CSV,
        help="Input augmented metadata CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for train/validation/test manifest CSVs.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help="Path for the Markdown split report.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of existing manifests and report.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def parse_augmented_flags(series: pd.Series) -> pd.Series:
    normalized = series.astype(str).str.strip().str.casefold()
    unknown = sorted(set(normalized) - {"true", "false"})
    if unknown:
        raise RuntimeError(
            "Column 'is_augmented' contains values other than True/False: "
            f"{unknown}"
        )
    return normalized.eq("true")


def parse_labels(series: pd.Series, column_name: str) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.isna().any():
        bad_rows = (numeric[numeric.isna()].index + 2).tolist()[:10]
        raise RuntimeError(
            f"Column {column_name!r} contains non-numeric labels at CSV rows "
            f"{bad_rows}."
        )
    if not numeric.mod(1).eq(0).all():
        raise RuntimeError(f"Column {column_name!r} contains non-integer labels.")
    integer = numeric.astype(int)
    invalid = sorted(set(integer) - {1, 2, 3, 4})
    if invalid:
        raise RuntimeError(
            f"Column {column_name!r} contains labels outside {{1,2,3,4}}: "
            f"{invalid}"
        )
    return integer


def output_paths(output_dir: Path, report_path: Path) -> dict[str, Path]:
    return {
        "train": output_dir / "train_manifest.csv",
        "val": output_dir / "val_manifest.csv",
        "test": output_dir / "test_manifest.csv",
        "report": report_path,
    }


def preflight_outputs(paths: dict[str, Path], overwrite: bool) -> None:
    existing = [path for path in paths.values() if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"- {display_path(path)}" for path in existing)
        raise FileExistsError(
            "Output file(s) already exist. Re-run with --overwrite to replace:\n"
            + formatted
        )


def validate_input(
    data: pd.DataFrame,
    is_augmented: pd.Series,
    labels: pd.Series,
    target_labels: pd.Series,
) -> pd.Series:
    missing_columns = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing_columns:
        raise RuntimeError(f"Input CSV is missing required columns: {missing_columns}")
    if "split" in data.columns:
        raise RuntimeError("Input CSV already contains a 'split' column.")
    if data.empty:
        raise RuntimeError("Input CSV contains no rows.")
    if data["specimen_id"].str.strip().eq("").any():
        raise RuntimeError("Input CSV contains blank specimen_id values.")
    if not labels.equals(target_labels):
        mismatch = labels[labels.ne(target_labels)].index.tolist()[:10]
        csv_rows = [index + 2 for index in mismatch]
        raise RuntimeError(
            "Columns 'label' and 'A_Total_Rust_Category_(1–4)' disagree at "
            f"CSV rows {csv_rows}."
        )

    train_set = set(TRAIN_SPECIMENS)
    val_set = set(VAL_SPECIMENS)
    test_set = set(TEST_SPECIMENS)
    assigned_sets = (train_set, val_set, test_set)
    if (
        train_set & val_set
        or train_set & test_set
        or val_set & test_set
    ):
        raise RuntimeError("The hardcoded specimen assignment lists are not disjoint.")

    assigned_union = set().union(*assigned_sets)
    input_specimens = set(data["specimen_id"])
    if assigned_union != input_specimens:
        missing_from_assignment = sorted(input_specimens - assigned_union)
        absent_from_input = sorted(assigned_union - input_specimens)
        raise RuntimeError(
            "Hardcoded specimen assignment does not match the input CSV. "
            f"Unassigned input specimens: {missing_from_assignment}; "
            f"assigned specimens absent from input: {absent_from_input}."
        )
    if len(assigned_union) != 48:
        raise RuntimeError(
            f"Expected 48 hardcoded specimens, found {len(assigned_union)}."
        )

    source_specimen_counts = data.groupby("original_image_name")[
        "specimen_id"
    ].nunique()
    if not source_specimen_counts.eq(1).all():
        bad_names = source_specimen_counts[source_specimen_counts.ne(1)].index.tolist()
        raise RuntimeError(
            "Some original_image_name groups span multiple specimens: "
            f"{bad_names[:10]}"
        )

    original_counts = (~is_augmented).groupby(data["original_image_name"]).sum()
    if not original_counts.eq(1).all():
        bad_names = original_counts[original_counts.ne(1)].index.tolist()
        raise RuntimeError(
            "Each original_image_name must have exactly one original row; "
            f"violations: {bad_names[:10]}"
        )

    original_rows = data.loc[~is_augmented]
    original_labels = labels.loc[~is_augmented]
    maximum_labels = original_labels.groupby(original_rows["specimen_id"]).max()
    for stratum, expected_specimens in EXPECTED_STRATA.items():
        observed = set(maximum_labels[maximum_labels.eq(stratum)].index)
        if observed != expected_specimens:
            raise RuntimeError(
                f"Maximum-label stratum {stratum} differs from the hardcoded "
                f"assignment. Observed: {sorted(observed)}; "
                f"expected: {sorted(expected_specimens)}."
            )
    return maximum_labels


def add_split_column(rows: pd.DataFrame, split_name: str) -> pd.DataFrame:
    manifest = rows.copy()
    manifest.insert(0, "split", split_name)
    return manifest


def build_manifests(
    data: pd.DataFrame, is_augmented: pd.Series
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Keep training augmentations while retaining only held-out originals.

    Augmented copies of validation/test specimens must be excluded entirely;
    putting them in training would reveal the held-out specimen."""
    train_mask = data["specimen_id"].isin(TRAIN_SPECIMENS)
    val_specimen_mask = data["specimen_id"].isin(VAL_SPECIMENS)
    test_specimen_mask = data["specimen_id"].isin(TEST_SPECIMENS)

    manifests = {
        "train": add_split_column(data.loc[train_mask], "train"),
        "val": add_split_column(data.loc[val_specimen_mask & ~is_augmented], "val"),
        "test": add_split_column(
            data.loc[test_specimen_mask & ~is_augmented], "test"
        ),
    }
    excluded = data.loc[(val_specimen_mask | test_specimen_mask) & is_augmented].copy()
    return manifests, excluded


def count_rows(manifest: pd.DataFrame) -> tuple[int, int, int]:
    augmented = parse_augmented_flags(manifest["is_augmented"])
    augmented_count = int(augmented.sum())
    original_count = int((~augmented).sum())
    return original_count, augmented_count, len(manifest)


def validate_manifests(
    data: pd.DataFrame,
    is_augmented: pd.Series,
    labels: pd.Series,
    manifests: dict[str, pd.DataFrame],
    excluded: pd.DataFrame,
) -> list[str]:
    """Check specimen disjointness and original/augmentation membership before writing."""
    messages: list[str] = []

    specimen_sets = {
        name: set(manifest["specimen_id"]) for name, manifest in manifests.items()
    }
    if (
        specimen_sets["train"] & specimen_sets["val"]
        or specimen_sets["train"] & specimen_sets["test"]
        or specimen_sets["val"] & specimen_sets["test"]
    ):
        raise RuntimeError("A specimen_id appears in more than one split.")
    messages.append("No specimen appears in more than one split")

    if parse_augmented_flags(manifests["val"]["is_augmented"]).any() or (
        parse_augmented_flags(manifests["test"]["is_augmented"]).any()
    ):
        raise RuntimeError("An augmented row appears in validation or test.")
    messages.append("No augmented row in val or test")

    original_indices = set(data.index[~is_augmented])
    assigned_original_indices: list[int] = []
    for manifest in manifests.values():
        manifest_augmented = parse_augmented_flags(manifest["is_augmented"])
        assigned_original_indices.extend(
            manifest.index[~manifest_augmented].tolist()
        )
    if (
        set(assigned_original_indices) != original_indices
        or len(assigned_original_indices) != len(original_indices)
    ):
        raise RuntimeError(
            "Original rows are missing from the manifests or assigned more than once."
        )
    messages.append(
        f"All {len(original_indices)} original rows assigned to exactly one split"
    )

    partition_indices = [
        set(manifests["train"].index),
        set(manifests["val"].index),
        set(manifests["test"].index),
        set(excluded.index),
    ]
    combined = set().union(*partition_indices)
    combined_size = sum(len(indices) for indices in partition_indices)
    if combined != set(data.index) or combined_size != len(data):
        raise RuntimeError(
            "Train, validation, test, and excluded rows do not partition the input."
        )
    messages.append(
        "Row totals sum to "
        f"{len(data)} ({len(manifests['train'])} + {len(manifests['val'])} + "
        f"{len(manifests['test'])} + {len(excluded)})"
    )

    for split_name, display_name in (("val", "Val"), ("test", "Test")):
        split_labels = set(labels.loc[manifests[split_name].index])
        if split_labels != {1, 2, 3, 4}:
            raise RuntimeError(
                f"{display_name} manifest has labels {sorted(split_labels)}, "
                "expected {1,2,3,4}."
            )
        messages.append(
            f"{display_name} manifest contains labels {{1, 2, 3, 4}}"
        )

    expected_sets = {
        "train": set(TRAIN_SPECIMENS),
        "val": set(VAL_SPECIMENS),
        "test": set(TEST_SPECIMENS),
    }
    if any(
        specimen_sets[name] != expected_sets[name]
        for name in ("train", "val", "test")
    ):
        raise RuntimeError("Manifest specimen assignments differ from hardcoded lists.")
    messages.append("Specimen assignments match hardcoded lists")
    return messages


def specimens_by_stratum(
    specimen_ids: list[str], maximum_labels: pd.Series
) -> dict[int, list[str]]:
    specimen_set = set(specimen_ids)
    return {
        stratum: sorted(
            specimen
            for specimen in maximum_labels[maximum_labels.eq(stratum)].index
            if specimen in specimen_set
        )
        for stratum in (1, 2, 3, 4)
    }


def class_counts(manifest: pd.DataFrame) -> dict[int, int]:
    labels = parse_labels(manifest["label"], "label")
    counts = labels.value_counts().to_dict()
    return {label: int(counts.get(label, 0)) for label in (1, 2, 3, 4)}


def make_report(
    input_csv: Path,
    manifests: dict[str, pd.DataFrame],
    excluded: pd.DataFrame,
    maximum_labels: pd.Series,
    total_originals: int,
    total_augmented: int,
    total_rows: int,
) -> str:
    assignments = {
        "Train": specimens_by_stratum(TRAIN_SPECIMENS, maximum_labels),
        "Val": specimens_by_stratum(VAL_SPECIMENS, maximum_labels),
        "Test": specimens_by_stratum(TEST_SPECIMENS, maximum_labels),
    }
    assignment_lines = [
        "| Split | Stratum 1 (max label 1) | Stratum 2 (max label 2) | "
        "Stratum 3 (max label 3) | Stratum 4 (max label 4) |",
        "|---|---|---|---|---|",
    ]
    for split_name in ("Train", "Val", "Test"):
        cells = [
            ", ".join(f"`{item}`" for item in assignments[split_name][stratum])
            for stratum in (1, 2, 3, 4)
        ]
        assignment_lines.append(
            f"| {split_name} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |"
        )

    row_counts = {
        name: count_rows(manifests[name]) for name in ("train", "val", "test")
    }
    excluded_augmented = len(excluded)
    row_count_lines = [
        "| Split | Specimens | Original rows | Augmented rows | Total rows |",
        "|---|---:|---:|---:|---:|",
        f"| Train | {len(TRAIN_SPECIMENS)} | {row_counts['train'][0]} | "
        f"{row_counts['train'][1]} | {row_counts['train'][2]} |",
        f"| Val | {len(VAL_SPECIMENS)} | {row_counts['val'][0]} | "
        f"{row_counts['val'][1]} | {row_counts['val'][2]} |",
        f"| Test | {len(TEST_SPECIMENS)} | {row_counts['test'][0]} | "
        f"{row_counts['test'][1]} | {row_counts['test'][2]} |",
        f"| Excluded (aug) | — | 0 | {excluded_augmented} | "
        f"{excluded_augmented} |",
        f"| **Total** | **48** | **{total_originals}** | "
        f"**{total_augmented}** | **{total_rows}** |",
    ]

    validation_counts = {
        "Val": class_counts(manifests["val"]),
        "Test": class_counts(manifests["test"]),
    }
    class_lines = [
        "| Split | Label 1 | Label 2 | Label 3 | Label 4 | Total originals |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for split_name in ("Val", "Test"):
        counts = validation_counts[split_name]
        class_lines.append(
            f"| {split_name} | {counts[1]} | {counts[2]} | {counts[3]} | "
            f"{counts[4]} | {sum(counts.values())} |"
        )

    return f"""# Corrosion Classification Split Report

## Method

The manifests use a fixed specimen-level assignment stratified by each specimen's maximum four-class corrosion severity label across original images. All rows from a training specimen remain together in training, while validation and test contain only original images; augmented rows belonging to held-out validation and test specimens are excluded.

Input metadata: `{display_path(input_csv)}`.

## Specimen assignment

{chr(10).join(assignment_lines)}

## Row counts

{chr(10).join(row_count_lines)}

The {excluded_augmented} excluded rows are augmented copies from validation or test specimens and do not appear in any manifest.

## Per-class distribution in validation and test

{chr(10).join(class_lines)}

## Leakage check

No `specimen_id` appears in more than one of the train, validation, or test splits.

## Reproduction

From the repository root:

```bash
python augmentation/make_splits.py --overwrite
```
"""


def write_outputs_transactionally(
    paths: dict[str, Path],
    manifests: dict[str, pd.DataFrame],
    report_text: str,
) -> None:
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    temporary_paths = {
        name: path.with_name(f".{path.name}.tmp") for name, path in paths.items()
    }
    backup_paths = {
        name: path.with_name(f".{path.name}.bak") for name, path in paths.items()
    }
    committed: list[str] = []
    backed_up: list[str] = []

    try:
        for path in temporary_paths.values():
            if path.exists():
                path.unlink()
        for path in backup_paths.values():
            if path.exists():
                path.unlink()

        manifests["train"].to_csv(
            temporary_paths["train"], index=False, encoding="utf-8"
        )
        manifests["val"].to_csv(
            temporary_paths["val"], index=False, encoding="utf-8"
        )
        manifests["test"].to_csv(
            temporary_paths["test"], index=False, encoding="utf-8"
        )
        temporary_paths["report"].write_text(report_text, encoding="utf-8")

        for name, target in paths.items():
            if target.exists():
                target.replace(backup_paths[name])
                backed_up.append(name)
            temporary_paths[name].replace(target)
            committed.append(name)

        for name in backed_up:
            backup_paths[name].unlink(missing_ok=True)
    except Exception:
        for name in committed:
            paths[name].unlink(missing_ok=True)
        for name in backed_up:
            if backup_paths[name].exists():
                backup_paths[name].replace(paths[name])
        for path in temporary_paths.values():
            path.unlink(missing_ok=True)
        for path in backup_paths.values():
            path.unlink(missing_ok=True)
        raise


def main() -> int:
    args = parse_args()
    input_csv = args.input_csv.resolve()
    output_dir = args.output_dir.resolve()
    report_path = args.report.resolve()
    paths = output_paths(output_dir, report_path)
    preflight_outputs(paths, args.overwrite)

    if not input_csv.is_file():
        raise FileNotFoundError(f"Input CSV not found: {display_path(input_csv)}")

    data = pd.read_csv(
        input_csv,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )
    missing_columns = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing_columns:
        raise RuntimeError(f"Input CSV is missing required columns: {missing_columns}")
    print(
        f"Loading {display_path(input_csv)} ... {len(data)} rows, "
        f"{data['specimen_id'].nunique()} specimens."
    )

    is_augmented = parse_augmented_flags(data["is_augmented"])
    labels = parse_labels(data["label"], "label")
    target_labels = parse_labels(
        data["A_Total_Rust_Category_(1–4)"],
        "A_Total_Rust_Category_(1–4)",
    )

    print("Computing per-specimen maximum labels ...")
    maximum_labels = validate_input(data, is_augmented, labels, target_labels)

    print("Applying hardcoded stratified specimen assignment ...")
    print(f"  Train: {len(TRAIN_SPECIMENS)} specimens")
    print(f"  Val:   {len(VAL_SPECIMENS)} specimens")
    print(f"  Test:  {len(TEST_SPECIMENS)} specimens")

    print("\nBuilding split manifests ...")
    manifests, excluded = build_manifests(data, is_augmented)
    train_counts = count_rows(manifests["train"])
    val_counts = count_rows(manifests["val"])
    test_counts = count_rows(manifests["test"])
    print(
        f"  Train: {train_counts[0]} original + {train_counts[1]} augmented "
        f"= {train_counts[2]} rows"
    )
    print(
        f"  Val:   {val_counts[0]} original + {val_counts[1]} augmented "
        f"= {val_counts[2]} rows"
    )
    print(
        f"  Test:  {test_counts[0]} original + {test_counts[1]} augmented "
        f"= {test_counts[2]} rows"
    )
    print(f"  Excluded augmented rows: {len(excluded)}")

    print("\nRunning validation checks ...")
    validation_messages = validate_manifests(
        data, is_augmented, labels, manifests, excluded
    )
    for message in validation_messages:
        print(f"[OK] {message}")

    total_originals = int((~is_augmented).sum())
    total_augmented = int(is_augmented.sum())
    report_text = make_report(
        input_csv,
        manifests,
        excluded,
        maximum_labels,
        total_originals,
        total_augmented,
        len(data),
    )

    print(f"\nWriting {display_path(paths['train'])} ... {len(manifests['train'])} rows")
    print(f"Writing {display_path(paths['val'])} ... {len(manifests['val'])} rows")
    print(f"Writing {display_path(paths['test'])} ... {len(manifests['test'])} rows")
    print(f"Writing {display_path(paths['report'])} ...")
    write_outputs_transactionally(paths, manifests, report_text)

    print("\nDone. Splits written successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("ERROR: interrupted by user.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)
