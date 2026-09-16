from __future__ import annotations

from typing import Dict

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, LeaveOneGroupOut


def _append_manifest_rows(
    rows, df: pd.DataFrame, strategy: str, split_id: str, membership: str, group_col: str
):
    subset = df[["sample_name", "specimen_id"]].copy()
    subset["group_value"] = df[group_col].values
    subset["strategy"] = strategy
    subset["split_id"] = split_id
    subset["membership"] = membership
    rows.extend(subset.to_dict("records"))


def build_split_manifests(
    df: pd.DataFrame,
    group_col: str,
    treatment_col: str,
    campaign_col: str,
    n_splits: int,
    test_size: float,
    random_state: int,
) -> Dict[str, pd.DataFrame]:
    manifests = {}

    group_rows = []
    splitter = GroupShuffleSplit(
        n_splits=n_splits, test_size=test_size, random_state=random_state
    )
    for split_idx, (train_idx, test_idx) in enumerate(
        splitter.split(df, groups=df[group_col])
    ):
        _append_manifest_rows(
            group_rows, df.iloc[train_idx], "group_shuffle", f"gss_{split_idx}", "train", group_col
        )
        _append_manifest_rows(
            group_rows, df.iloc[test_idx], "group_shuffle", f"gss_{split_idx}", "test", group_col
        )
    manifests["group_shuffle"] = pd.DataFrame(group_rows)

    for strategy, col in [
        ("leave_one_treatment_out", treatment_col),
        ("leave_one_campaign_out", campaign_col),
    ]:
        rows = []
        splitter = LeaveOneGroupOut()
        for split_idx, (train_idx, test_idx) in enumerate(splitter.split(df, groups=df[col])):
            _append_manifest_rows(rows, df.iloc[train_idx], strategy, f"{strategy}_{split_idx}", "train", col)
            _append_manifest_rows(rows, df.iloc[test_idx], strategy, f"{strategy}_{split_idx}", "test", col)
        manifests[strategy] = pd.DataFrame(rows)

    return manifests


def split_summary(manifest_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (strategy, split_id), split_df in manifest_df.groupby(["strategy", "split_id"]):
        train = split_df.loc[split_df["membership"] == "train"]
        test = split_df.loc[split_df["membership"] == "test"]
        leakage = bool(set(train["specimen_id"]) & set(test["specimen_id"]))
        rows.append(
            {
                "strategy": strategy,
                "split_id": split_id,
                "train_rows": len(train),
                "test_rows": len(test),
                "train_specimens": train["specimen_id"].nunique(),
                "test_specimens": test["specimen_id"].nunique(),
                "leakage_detected": leakage,
            }
        )
    return pd.DataFrame(rows).sort_values(["strategy", "split_id"]).reset_index(drop=True)


def manifest_to_split_ids(manifest_df: pd.DataFrame):
    for split_id, split_df in manifest_df.groupby("split_id"):
        train_ids = split_df.loc[split_df["membership"] == "train", "sample_name"].tolist()
        test_ids = split_df.loc[split_df["membership"] == "test", "sample_name"].tolist()
        yield split_id, train_ids, test_ids
