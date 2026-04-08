from __future__ import annotations

import sys
import json

sys.path.insert(0, "src")

import pandas as pd

import run_audit_validation
import run_eda
import run_extract_image_features
import train_degradation_models
import train_hidden_damage_models
import train_rul_proxy_models
import train_surface_models
from corrosion_proxy_rul.reporting import write_readme, write_scientific_report
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, ROOT_DIR, configure_logging


def main():
    logger = configure_logging("run_full_baseline")

    run_audit_validation.main()
    run_eda.main()
    run_extract_image_features.main()
    train_surface_models.main()
    train_hidden_damage_models.main()
    train_degradation_models.main()
    train_rul_proxy_models.main()

    facts = json.loads((OUTPUT_DIR / "audit" / "verified_facts.json").read_text())
    surface_best = pd.read_csv(OUTPUT_DIR / "models" / "surface" / "best_models.csv")
    hidden_best = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "best_models.csv")
    degradation_best = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_best_fits.csv")
    proxy_summary = pd.read_csv(OUTPUT_DIR / "models" / "proxy_rul" / "proxy_rul_summary.csv")

    commands = [
        "conda run -n env python run_audit_validation.py",
        "conda run -n env python run_eda.py",
        "conda run -n env python run_extract_image_features.py",
        "conda run -n env python train_surface_models.py",
        "conda run -n env python train_hidden_damage_models.py",
        "conda run -n env python train_degradation_models.py",
        "conda run -n env python train_rul_proxy_models.py",
        "conda run -n env python run_full_baseline.py",
    ]
    write_readme(ROOT_DIR, commands)
    write_scientific_report(
        ROOT_DIR, facts, surface_best, hidden_best, degradation_best, proxy_summary
    )
    logger.info("Full baseline run completed successfully")


if __name__ == "__main__":
    main()
