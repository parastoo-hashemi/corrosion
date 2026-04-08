from __future__ import annotations

from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.io import parse_record_ids, wire_loss_to_percent


class DataParsingTests(unittest.TestCase):
    def test_parse_record_ids(self) -> None:
        parsed = parse_record_ids(pd.Series(["S1MI02-20221206-28W", "D01-20240110-0W"]))
        self.assertEqual(parsed.loc[0, "specimen_id"], "S1MI02")
        self.assertEqual(int(parsed.loc[0, "week"]), 28)
        self.assertEqual(parsed.loc[1, "series_label"], "D")
        self.assertTrue(bool(parsed["record_id_valid"].all()))

    def test_wire_loss_fraction_scaling(self) -> None:
        scaled = wire_loss_to_percent(pd.Series([0.25, 0.5698]), scale_threshold=1.5)
        self.assertAlmostEqual(float(scaled.iloc[0]), 25.0)
        self.assertAlmostEqual(float(scaled.iloc[1]), 56.98)


if __name__ == "__main__":
    unittest.main()
