# Corrosion Prediction Pipeline

This folder contains:
- Data loading/cleaning for `Data/Images_Dataset_A-Z.xlsx`
- Image feature extraction from `Data/Images_dataset`
- Three validated ML tasks:
  - `current_corrosion`: predicts current peak rust percentage from metadata + image.
  - `progression`: predicts peak rust percentage at any week from metadata + week.
  - `time_to_threshold`: predicts remaining weeks to severe corrosion threshold.
- FastAPI deployment service for inference.

## 1) Install dependencies

From the repository root:

```bash
python3 -m pip install --user -r main/requirements.txt
```

## 2) Train models

From the repository root:

```bash
python3 -m main.train_models \
  --excel-path Data/Images_Dataset_A-Z.xlsx \
  --image-dir Data/Images_dataset \
  --artifacts-dir main/artifacts \
  --reports-dir main/reports
```

Outputs:
- Models: `main/artifacts/*_model.joblib`
- Manifest: `main/artifacts/manifest.json`
- Metrics: `main/reports/*_metrics.csv`
- Feature importance: `main/reports/*_feature_importance.csv`

## 3) Run the API (deployment)

```bash
python3 -m uvicorn main.api:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## 4) Example API calls

### Current corrosion from image

```bash
curl -X POST http://127.0.0.1:8000/predict/current \
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

### Progression curve

```bash
curl -X POST http://127.0.0.1:8000/predict/progression \
  -H "Content-Type: application/json" \
  -d '{
    "n_steel_mesh": 4,
    "treatment": "NO",
    "nacl_pct": 0.05,
    "ageing_days": 260,
    "cover_mm": 7.16,
    "series": "D",
    "start_week": 0,
    "end_week": 36,
    "step": 1,
    "threshold_pct": 20
  }'
```

### Remaining time to threshold

```bash
curl -X POST http://127.0.0.1:8000/predict/time-to-threshold \
  -H "Content-Type: application/json" \
  -d '{
    "n_steel_mesh": 4,
    "treatment": "NO",
    "nacl_pct": 0.05,
    "ageing_days": 260,
    "cover_mm": 7.16,
    "series": "D",
    "week": 22,
    "current_peak_rust_pct": 13.8,
    "threshold_pct": 20
  }'
```

