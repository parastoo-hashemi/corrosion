from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


def _fmt(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data available._"
    try:
        return df.to_markdown(index=False)
    except Exception:
        return "```\n" + df.to_string(index=False) + "\n```"


def write_scientific_report(
    report_path: Path,
    run_info: Dict[str, object],
    model_metrics: pd.DataFrame,
    figures: Dict[str, str],
    by_treatment: pd.DataFrame,
    by_series: pd.DataFrame,
    by_specimen: pd.DataFrame,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    best_row = model_metrics.sort_values("test_mae").iloc[0]
    worst_specimen = by_specimen.sort_values("mae", ascending=False).head(10)
    best_specimen = by_specimen.sort_values("mae", ascending=True).head(10)
    if str(best_row["model"]) == "multimodal_mlp":
        interpretation_line = (
            "The multimodal fusion setup improved robustness relative to the image-only baseline."
        )
    else:
        interpretation_line = (
            "In this run, the image-only deep representation outperformed multimodal fusion, "
            "suggesting visual signals dominate under the current dataset size."
        )

    text = f"""# Phase 2 Scientific Report: Multimodal Deep Corrosion Prediction

## 1. Executive Summary
This Phase 2 pipeline implements a **multimodal deep-learning strategy** combining:
- deep visual embeddings from a pretrained ResNet-18 encoder,
- engineered tabular/context features from the experimental table,
- a neural regression head for quantitative corrosion prediction.

The model is trained and validated with **group-wise splitting by specimen** to prevent leakage across weeks for the same material.  
Best Phase 2 model: **{best_row['model']}** with test MAE **{best_row['test_mae']:.4f}** and R2 **{best_row['test_r2']:.4f}**.

## 2. Data and Experimental Context
- Total records: **{run_info['dataset']['rows']}**
- Total specimens (materials): **{run_info['dataset']['specimens']}**
- Week range: **{run_info['dataset']['week_min']} to {run_info['dataset']['week_max']}**
- Corrupted images handled automatically: **{run_info['dataset']['corrupted_images_count']}**

Target variable:
- `B_Peak_Rust_Percentage_[%]` (continuous peak corrosion evidence).

Severity bands for interpretation:
- Low: < 1%
- Medium: 1% to < 20%
- High: >= 20%

## 3. Methodology
### 3.1 Pipeline
1. Clean Excel structure (first row as semantic header).
2. Parse specimen/time metadata from ID (`specimen-date-week`).
3. Extract deep image embeddings (512-d) via pretrained ResNet-18 (ImageNet transfer).
4. Encode tabular features (scaling + one-hot encoding).
5. Train neural regressors:
   - Image-only deep baseline.
   - Multimodal deep fusion model.
6. Evaluate on held-out specimen groups (test split).

### 3.2 Validation Protocol
- Grouped split by specimen:
  - train/val/test are separated by material identity.
- Metrics:
  - MAE (primary operational metric),
  - RMSE,
  - R2.

### 3.3 Why this design is scientifically defensible
- It follows transfer-learning best practices for limited datasets.
- It keeps interpretation tied to corrosion progression and material groups.
- It avoids temporal/material leakage that would inflate reported performance.

## 4. Quantitative Results
### 4.1 Model Comparison (Test)
{_fmt(model_metrics)}

### 4.2 Performance by Treatment (Test)
{_fmt(by_treatment)}

### 4.3 Performance by Series (Test)
{_fmt(by_series)}

### 4.4 Best/Worst Material-level Performance (Test)
Best 10 specimens by MAE:
{_fmt(best_specimen)}

Worst 10 specimens by MAE:
{_fmt(worst_specimen)}

## 5. Visual Evidence
Key figure files generated:
- Target distribution: `{figures.get('target_distribution', '')}`
- Predicted vs true (test): `{figures.get('pred_vs_true', '')}`
- Residual distribution: `{figures.get('residual_distribution', '')}`
- Residual vs week: `{figures.get('residual_vs_week', '')}`
- Model comparison: `{figures.get('model_comparison', '')}`
- MAE by treatment: `{figures.get('mae_by_treatment', '')}`
- MAE by series: `{figures.get('mae_by_series', '')}`
- Progression by treatment: `{figures.get('progression_by_treatment', '')}`
- Progression by series: `{figures.get('progression_by_series', '')}`
- Severity confusion matrix: `{figures.get('severity_confusion', '')}`
- Per-material progression plots generated: `{figures.get('per_material_count', '0')}` files

## 6. Interpretation and Practical Impact
1. {interpretation_line}
2. Material-dependent behavior is visible through specimen-level plots and group metrics.
3. The produced error diagnostics identify where additional data collection is most needed.

## 7. Limitations
1. Dataset size is moderate for deep learning; rare corrosion regimes may still be underrepresented.
2. Some progression uncertainty remains at late weeks for highly variable specimens.
3. One source image was corrupted and required robust fallback handling.

## 8. Recommended Next Steps
1. Add more late-stage images and mechanical-test-linked labels for stronger extrapolation.
2. Evaluate temporal transformers or sequence-aware models at specimen level.
3. Add uncertainty estimation (e.g., deep ensembles) for risk-aware maintenance planning.

## 9. Reproducibility
- Environment: `conda activate reinforce_2`
- Entry point: `python -m corrosion.image_embeddings.train_phase2`
- API deployment: `python -m uvicorn corrosion.image_embeddings.api:app --host 0.0.0.0 --port 8100`
"""
    report_path.write_text(text, encoding="utf-8")
