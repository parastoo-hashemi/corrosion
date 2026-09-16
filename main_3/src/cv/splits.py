"""Grouped evaluation definitions for the historical main_3 experiment.

The independent unit is a specimen, not one photograph from its time series.
Campaign holdout addresses transfer across confounded experimental settings."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


@dataclass(frozen=True)
class SplitDefinition:
    strategy: str
    fold_id: str
    holdout_group: str
    train_idx: np.ndarray
    test_idx: np.ndarray


def group_shuffle_split(
    df: pd.DataFrame,
    group_col: str,
    test_size: float,
    random_state: int,
) -> SplitDefinition:
    """Separate complete groups so repeated images cannot leak between partitions."""
    splitter = GroupShuffleSplit(
        n_splits=1, test_size=test_size, random_state=random_state
    )
    idx = np.arange(len(df))
    train_idx, test_idx = next(splitter.split(idx, groups=df[group_col].astype(str)))
    return SplitDefinition(
        strategy="group_shuffle",
        fold_id="fold_00",
        holdout_group="mixed_specimens",
        train_idx=train_idx,
        test_idx=test_idx,
    )


def leave_one_group_out(df: pd.DataFrame, group_col: str, strategy: str) -> list[SplitDefinition]:
    splits: list[SplitDefinition] = []
    for order, holdout_value in enumerate(
        sorted(df[group_col].dropna().astype(str).unique().tolist())
    ):
        test_mask = df[group_col].astype(str) == holdout_value
        if test_mask.sum() == 0 or (~test_mask).sum() == 0:
            continue
        splits.append(
            SplitDefinition(
                strategy=strategy,
                fold_id=f"fold_{order:02d}",
                holdout_group=holdout_value,
                train_idx=np.flatnonzero(~test_mask.values),
                test_idx=np.flatnonzero(test_mask.values),
            )
        )
    return splits


def build_splits(
    df: pd.DataFrame,
    strategy: str,
    random_state: int,
    test_size: float,
) -> list[SplitDefinition]:
    """Map the requested evaluation regime to its original grouping variable."""
    if strategy == "group_shuffle":
        return [
            group_shuffle_split(
                df=df,
                group_col="specimen_id",
                test_size=test_size,
                random_state=random_state,
            )
        ]
    if strategy == "leave_one_treatment_out":
        return leave_one_group_out(df=df, group_col="treatment_code", strategy=strategy)
    if strategy == "leave_one_campaign_out":
        return leave_one_group_out(df=df, group_col="campaign_id", strategy=strategy)
    raise ValueError(f"Unsupported split strategy: {strategy}")
