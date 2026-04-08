from __future__ import annotations

import sys

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.data_cleaning import build_master_table, build_terminal_structural_subset
from corrosion_proxy_rul.data_loading import load_excel_metadata, scan_image_directory
from corrosion_proxy_rul.splits import build_split_manifests, split_summary
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging, save_dataframe_csv, write_json


def main():
    logger = configure_logging("run_audit_validation")
    configs = load_configs()
    dataset_cfg = configs["dataset"]

    metadata_df = load_excel_metadata(dataset_cfg["paths"]["excel"])
    image_df = scan_image_directory(dataset_cfg["paths"]["images_dir"])
    master_df, mapping_df, issues_df = build_master_table(metadata_df, image_df)
    terminal_df = build_terminal_structural_subset(master_df)

    split_cfg = configs["modeling"]["group_shuffle"]
    manifests = build_split_manifests(
        master_df,
        group_col="specimen_id",
        treatment_col="split_group_treatment",
        campaign_col="campaign_id",
        n_splits=split_cfg["n_splits"],
        test_size=split_cfg["test_size"],
        random_state=configs["modeling"]["random_state"],
    )

    save_dataframe_csv(metadata_df, OUTPUT_DIR / "audit" / "metadata_loaded.csv")
    save_dataframe_csv(image_df, OUTPUT_DIR / "audit" / "image_scan.csv")
    save_dataframe_csv(mapping_df, OUTPUT_DIR / "audit" / "specimen_mapping_validated.csv")
    save_dataframe_csv(issues_df, OUTPUT_DIR / "audit" / "issues_log.csv")
    save_dataframe_csv(master_df, OUTPUT_DIR / "data" / "master_table.csv")
    save_dataframe_csv(terminal_df, OUTPUT_DIR / "data" / "terminal_structural_table.csv")

    for strategy, manifest_df in manifests.items():
        save_dataframe_csv(manifest_df, OUTPUT_DIR / "splits" / f"master_{strategy}.csv")
        save_dataframe_csv(split_summary(manifest_df), OUTPUT_DIR / "splits" / f"master_{strategy}_summary.csv")

    facts = {
        "aligned_rows": int(len(master_df)),
        "unique_specimens": int(master_df["specimen_id"].nunique()),
        "image_files": int(len(image_df)),
        "orphan_images": issues_df.loc[issues_df["issue_type"] == "orphan_image", "sample_name"].dropna().tolist(),
        "structural_rows": int(master_df["has_structural_label"].sum()),
        "group_key": "specimen_id",
    }
    write_json(OUTPUT_DIR / "audit" / "verified_facts.json", facts)
    logger.info("Audit complete. Verified facts: %s", facts)


if __name__ == "__main__":
    main()
