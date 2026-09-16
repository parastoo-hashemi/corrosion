# Phase 2 Scientific Report: Multimodal Deep Corrosion Prediction

## 1. Executive Summary
This Phase 2 pipeline implements a **multimodal deep-learning strategy** combining:
- deep visual embeddings from a pretrained ResNet-18 encoder,
- engineered tabular/context features from the experimental table,
- a neural regression head for quantitative corrosion prediction.

The model is trained and validated with **group-wise splitting by specimen** to prevent leakage across weeks for the same material.  
Best Phase 2 model: **image_only_mlp** with test MAE **5.6255** and R2 **0.5237**.

## 2. Data and Experimental Context
- Total records: **792**
- Total specimens (materials): **48**
- Week range: **0 to 36**
- Corrupted images handled automatically: **1**

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
```
         model  test_mae  test_rmse  test_r2
image_only_mlp  5.625508   9.263883 0.523721
multimodal_mlp  5.747576   9.865218 0.459882
```

### 4.2 Performance by Treatment (Test)
```
Treatment  n      mae      rmse  mean_true  mean_pred
    SA_VF 15 3.621691  5.069773   3.279733   5.007616
    SA_PA 15 4.001444  6.764382   7.504133   4.574518
       MI 45 4.339227  7.185805   8.149800  10.004148
       SA 33 6.023989 11.421895   6.812030   7.179682
       PA 18 6.442182  8.105050  12.515944   7.208230
       NO 33 8.184623 12.012847  16.220030   9.089595
```

### 4.3 Performance by Series (Test)
```
series   n       mae      rmse  mean_true  mean_pred
     S 105  4.075141  8.037653   6.960771   6.877920
     F  18  5.584780  7.322439   4.359667   9.891121
     G  18  6.442182  8.105050  12.515944   7.208230
     D  18 13.893368 16.183532  26.622333  12.810167
```

### 4.4 Best/Worst Material-level Performance (Test)
Best 10 specimens by MAE:
```
specimen  n       mae      rmse  mean_true  mean_pred
  S1MI01 15  1.334129  1.786233   3.737267   4.624908
  S1MI03 15  2.642315  3.410044   7.090067   8.803897
S4SAVF02 15  3.621691  5.069773   3.279733   5.007616
  S3PA03 15  4.001444  6.764382   7.504133   4.574518
  S1MI02 15  4.391448  8.719556   4.861133   8.746398
     F01 18  5.584780  7.322439   4.359667   9.891121
  S1MI04 15  5.983917  8.200509  12.498200  12.462149
     G02 18  6.442182  8.105050  12.515944   7.208230
  S2SA07 15  6.551041 14.922118   9.754867   3.925955
     D05 18 13.893368 16.183532  26.622333  12.810167
```

Worst 10 specimens by MAE:
```
specimen  n       mae      rmse  mean_true  mean_pred
     D05 18 13.893368 16.183532  26.622333  12.810167
  S2SA07 15  6.551041 14.922118   9.754867   3.925955
     G02 18  6.442182  8.105050  12.515944   7.208230
  S1MI04 15  5.983917  8.200509  12.498200  12.462149
     F01 18  5.584780  7.322439   4.359667   9.891121
  S1MI02 15  4.391448  8.719556   4.861133   8.746398
  S3PA03 15  4.001444  6.764382   7.504133   4.574518
S4SAVF02 15  3.621691  5.069773   3.279733   5.007616
  S1MI03 15  2.642315  3.410044   7.090067   8.803897
  S1MI01 15  1.334129  1.786233   3.737267   4.624908
```

## 5. Visual Evidence
Key figure files generated:
- Target distribution: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/01_target_distribution.png`
- Predicted vs true (test): `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/02_pred_vs_true_test.png`
- Residual distribution: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/03_residual_distribution.png`
- Residual vs week: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/04_residual_vs_week.png`
- Model comparison: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/05_model_comparison.png`
- MAE by treatment: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/06_mae_by_treatment.png`
- MAE by series: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/07_mae_by_series.png`
- Progression by treatment: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/08_progression_by_treatment.png`
- Progression by series: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/09_progression_by_series.png`
- Severity confusion matrix: `/Users/youseffayyaz/Documents/Proj_corrosion/main_2/reports/figures/10_severity_confusion_matrix.png`
- Per-material progression plots generated: `48` files

## 6. Interpretation and Practical Impact
1. In this run, the image-only deep representation outperformed multimodal fusion, suggesting visual signals dominate under the current dataset size.
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
- Entry point: `python -m main_2.train_phase2`
- API deployment: `python -m uvicorn main_2.api:app --host 0.0.0.0 --port 8100`
