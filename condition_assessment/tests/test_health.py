from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rul.health import compute_health_index, risk_class_from_probability


class HealthTests(unittest.TestCase):
    def test_health_index_bounds(self) -> None:
        value = compute_health_index(
            surface_total_rust_pct=30.0,
            peak_rust_pct=45.0,
            wire_area_loss_pct=20.0,
            ultimate_load_kn=2.0,
            reference_load_kn=2.5,
        )
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_risk_class_mapping(self) -> None:
        self.assertEqual(risk_class_from_probability(0.2), "Low")
        self.assertEqual(risk_class_from_probability(0.4), "Moderate")
        self.assertEqual(risk_class_from_probability(0.7), "High")
        self.assertEqual(risk_class_from_probability(0.95), "Critical")


if __name__ == "__main__":
    unittest.main()
