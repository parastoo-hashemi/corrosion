from __future__ import annotations

from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cv.splits import build_splits


class SplitTests(unittest.TestCase):
    def test_group_shuffle_has_no_specimen_overlap(self) -> None:
        df = pd.DataFrame(
            {
                "record_id": [f"R{i}" for i in range(12)],
                "specimen_id": ["A", "A", "B", "B", "C", "C", "D", "D", "E", "E", "F", "F"],
                "treatment_code": ["NO", "NO", "SA", "SA", "PA", "PA", "NO", "NO", "SA", "SA", "PA", "PA"],
                "campaign_id": ["C1"] * 6 + ["C2"] * 6,
            }
        )
        split = build_splits(df, strategy="group_shuffle", random_state=42, test_size=0.33)[0]
        train_groups = set(df.iloc[split.train_idx]["specimen_id"])
        test_groups = set(df.iloc[split.test_idx]["specimen_id"])
        self.assertFalse(train_groups & test_groups)


if __name__ == "__main__":
    unittest.main()
