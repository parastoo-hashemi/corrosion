from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import pandas as pd

from .config import load_configs


@dataclass(frozen=True)
class SpecimenRecord:
    specimen_id: str
    campaign_id: str
    series_id: str
    split_group_treatment: str
    treatment_protocol: str
    treatment_coarse: str
    treatment_label_coarse: str
    n_steel_mesh: int
    nacl_pct: float
    terminal_week: int
    terminal_days: int


def mapping_to_dataframe() -> pd.DataFrame:
    mapping = load_configs()["specimen_mapping"]["specimens"]
    rows = []
    for specimen_id, payload in mapping.items():
        row = {"specimen_id": specimen_id}
        row.update(payload)
        rows.append(row)
    df = pd.DataFrame(rows).sort_values("specimen_id").reset_index(drop=True)
    return df


def validate_mapping(specimen_ids: Iterable[str]) -> pd.DataFrame:
    mapping_df = mapping_to_dataframe()
    expected = set(specimen_ids)
    found = set(mapping_df["specimen_id"])
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    if missing or extra:
        raise ValueError(
            f"Specimen mapping mismatch. Missing={missing}, extra={extra}"
        )
    return mapping_df


def apply_mapping(df: pd.DataFrame) -> pd.DataFrame:
    mapping_df = validate_mapping(df["specimen_id"].unique())
    merged = df.merge(mapping_df, on="specimen_id", how="left", validate="many_to_one")
    if merged["campaign_id"].isna().any():
        missing = sorted(merged.loc[merged["campaign_id"].isna(), "specimen_id"].unique())
        raise ValueError(f"Unmapped specimen IDs: {missing}")
    return merged
