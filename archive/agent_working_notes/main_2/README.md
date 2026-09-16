# Phase 2 (`main_2`) - Multimodal Deep Pipeline

This phase uses deep image embeddings + tabular context features for corrosion prediction.

## Environment

Use your requested conda environment:

```bash
conda activate reinforce_2
```

## Train Phase 2

From repository root:

```bash
python -m main_2.train_phase2 \
  --excel-path Data/Images_Dataset_A-Z.xlsx \
  --image-dir Data/Images_dataset \
  --artifacts-dir main_2/artifacts \
  --reports-dir main_2/reports
```

Outputs:
- Model/artifacts: `main_2/artifacts/`
- Predictions and metrics: `main_2/reports/`
- Figures (including per-material): `main_2/reports/figures/`
- Scientific report: `main_2/reports/phase2_scientific_report.md`

## Build Detailed PDF Scientific Report

```bash
python -m main_2.build_pdf_report
```

Output:
- `main_2/reports/phase2_scientific_report_full.pdf`

## Deploy API

```bash
python -m uvicorn main_2.api:app --host 0.0.0.0 --port 8100
```

Health:

```bash
curl http://127.0.0.1:8100/health
```

Prediction:

```bash
curl -X POST http://127.0.0.1:8100/predict/current \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "Data/Images_dataset/D01-20240724-28W.png",
    "n_steel_mesh": 4,
    "treatment": "NO",
    "nacl_pct": 0.05,
    "ageing_days": 260,
    "cover_mm": 7.16,
    "week": 28,
    "series": "D"
  }'
```
