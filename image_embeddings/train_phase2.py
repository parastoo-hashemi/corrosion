from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, TensorDataset

from corrosion.image_embeddings.config import (
    ARTIFACTS_DIR,
    BASE_FEATURES,
    EXCEL_PATH,
    FIGURES_DIR,
    IMAGE_DIR,
    PER_MATERIAL_DIR,
    REPORTS_DIR,
    SEED,
    TARGET_COL,
    TEST_SIZE,
    VAL_SIZE_WITHIN_TRAIN,
)
from corrosion.image_embeddings.data import (
    attach_split_labels,
    build_group_splits,
    extract_resnet18_embeddings,
    fit_tabular_preprocessor,
    load_dataframe,
    summary_dict,
    transform_tabular,
)
from corrosion.image_embeddings.models import RegressionMLP
from corrosion.image_embeddings.report_writer import write_scientific_report
from corrosion.image_embeddings.visualize import create_visualizations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 2 multimodal deep-learning training pipeline."
    )
    parser.add_argument("--excel-path", type=Path, default=EXCEL_PATH)
    parser.add_argument("--image-dir", type=Path, default=IMAGE_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=ARTIFACTS_DIR)
    parser.add_argument("--reports-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=18)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=SEED)
    return parser.parse_args()


def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def pick_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def _build_loader(
    x: np.ndarray, y_scaled: np.ndarray, batch_size: int, shuffle: bool
) -> DataLoader:
    ds = TensorDataset(
        torch.tensor(x, dtype=torch.float32),
        torch.tensor(y_scaled, dtype=torch.float32),
    )
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=False)


def train_mlp(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    args: argparse.Namespace,
    model_name: str,
    device: torch.device,
) -> Tuple[RegressionMLP, pd.DataFrame, StandardScaler]:
    y_scaler = StandardScaler()
    y_train_scaled = y_scaler.fit_transform(y_train.reshape(-1, 1)).reshape(-1)
    y_val_scaled = y_scaler.transform(y_val.reshape(-1, 1)).reshape(-1)

    tr_loader = _build_loader(x_train, y_train_scaled, args.batch_size, shuffle=True)
    va_loader = _build_loader(x_val, y_val_scaled, args.batch_size, shuffle=False)

    model = RegressionMLP(input_dim=x_train.shape[1], dropout=args.dropout).to(device)
    optimizer = AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    criterion = nn.SmoothL1Loss()

    best_state = None
    best_val_mae = float("inf")
    patience_count = 0
    rows = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_losses = []
        for xb, yb in tr_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.detach().cpu().item()))

        model.eval()
        val_losses = []
        preds_scaled, true_scaled = [], []
        with torch.no_grad():
            for xb, yb in va_loader:
                xb = xb.to(device)
                yb = yb.to(device)
                pred = model(xb)
                loss = criterion(pred, yb)
                val_losses.append(float(loss.detach().cpu().item()))
                preds_scaled.append(pred.detach().cpu().numpy())
                true_scaled.append(yb.detach().cpu().numpy())

        preds_scaled_arr = np.concatenate(preds_scaled)
        true_scaled_arr = np.concatenate(true_scaled)
        preds = y_scaler.inverse_transform(preds_scaled_arr.reshape(-1, 1)).reshape(-1)
        true = y_scaler.inverse_transform(true_scaled_arr.reshape(-1, 1)).reshape(-1)
        val_mae = mean_absolute_error(true, preds)

        rows.append(
            {
                "model": model_name,
                "epoch": epoch,
                "train_loss": float(np.mean(train_losses)),
                "val_loss": float(np.mean(val_losses)),
                "val_mae": float(val_mae),
            }
        )

        if val_mae < best_val_mae:
            best_val_mae = float(val_mae)
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            patience_count = 0
        else:
            patience_count += 1
            if patience_count >= args.patience:
                break

    if best_state is None:
        raise RuntimeError("Training did not produce a valid checkpoint.")
    model.load_state_dict(best_state)
    history_df = pd.DataFrame(rows)
    return model, history_df, y_scaler


def predict_mlp(
    model: RegressionMLP,
    x: np.ndarray,
    y_scaler: StandardScaler,
    device: torch.device,
    batch_size: int = 256,
) -> np.ndarray:
    model.eval()
    all_preds = []
    loader = DataLoader(
        torch.tensor(x, dtype=torch.float32), batch_size=batch_size, shuffle=False
    )
    with torch.no_grad():
        for xb in loader:
            xb = xb.to(device)
            pred = model(xb).detach().cpu().numpy()
            all_preds.append(pred)
    pred_scaled = np.concatenate(all_preds)
    pred = y_scaler.inverse_transform(pred_scaled.reshape(-1, 1)).reshape(-1)
    return pred.astype(float)


def plot_learning_curves(history_df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for model_name, grp in history_df.groupby("model"):
        axes[0].plot(grp["epoch"], grp["train_loss"], label=f"{model_name} train")
        axes[0].plot(grp["epoch"], grp["val_loss"], label=f"{model_name} val")
        axes[1].plot(grp["epoch"], grp["val_mae"], label=model_name)
    axes[0].set_title("Training and Validation Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("SmoothL1 loss")
    axes[0].legend()
    axes[1].set_title("Validation MAE by Epoch")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("MAE [%]")
    axes[1].legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    set_seed(args.random_state)
    device = pick_device()
    print(f"[INFO] Device: {device}")

    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    PER_MATERIAL_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] Loading dataframe...")
    df = load_dataframe(args.excel_path, args.image_dir)
    split = build_group_splits(
        df=df,
        random_state=args.random_state,
        test_size=TEST_SIZE,
        val_size_within_train=VAL_SIZE_WITHIN_TRAIN,
    )
    df = attach_split_labels(df, split)

    print("[INFO] Extracting deep image embeddings with ResNet-18...")
    embeddings, corrupted_ids = extract_resnet18_embeddings(df, image_col="image_path", device=device)

    print("[INFO] Preparing tabular features...")
    preprocessor = fit_tabular_preprocessor(df, BASE_FEATURES, split.train_idx)
    tab_arr = transform_tabular(df, BASE_FEATURES, preprocessor)

    y = df[TARGET_COL].astype(float).values
    x_img = embeddings
    x_multi = np.concatenate([embeddings, tab_arr], axis=1).astype(np.float32)

    idx_train = split.train_idx
    idx_val = split.val_idx
    idx_test = split.test_idx

    print("[INFO] Training image-only MLP baseline...")
    img_model, img_hist, img_y_scaler = train_mlp(
        x_train=x_img[idx_train],
        y_train=y[idx_train],
        x_val=x_img[idx_val],
        y_val=y[idx_val],
        args=args,
        model_name="image_only_mlp",
        device=device,
    )

    print("[INFO] Training multimodal MLP (image + tabular)...")
    multi_model, multi_hist, multi_y_scaler = train_mlp(
        x_train=x_multi[idx_train],
        y_train=y[idx_train],
        x_val=x_multi[idx_val],
        y_val=y[idx_val],
        args=args,
        model_name="multimodal_mlp",
        device=device,
    )

    # Evaluate both models on test.
    img_pred_test = predict_mlp(
        img_model, x_img[idx_test], img_y_scaler, device=device
    )
    multi_pred_test = predict_mlp(
        multi_model, x_multi[idx_test], multi_y_scaler, device=device
    )
    y_test = y[idx_test]

    img_metrics = metrics(y_test, img_pred_test)
    multi_metrics = metrics(y_test, multi_pred_test)

    model_comparison = pd.DataFrame(
        [
            {
                "model": "image_only_mlp",
                "test_mae": img_metrics["mae"],
                "test_rmse": img_metrics["rmse"],
                "test_r2": img_metrics["r2"],
            },
            {
                "model": "multimodal_mlp",
                "test_mae": multi_metrics["mae"],
                "test_rmse": multi_metrics["rmse"],
                "test_r2": multi_metrics["r2"],
            },
        ]
    ).sort_values("test_mae")
    model_comparison_path = args.reports_dir / "model_comparison.csv"
    model_comparison.to_csv(model_comparison_path, index=False)

    best_model_name = str(model_comparison.iloc[0]["model"])
    print(f"[INFO] Best Phase 2 model: {best_model_name}")

    # Build predictions for all rows using the best model.
    if best_model_name == "multimodal_mlp":
        best_model = multi_model
        best_scaler = multi_y_scaler
        x_best = x_multi
        use_tabular = True
    else:
        best_model = img_model
        best_scaler = img_y_scaler
        x_best = x_img
        use_tabular = False

    y_pred_all = predict_mlp(best_model, x_best, best_scaler, device=device)
    pred_df = df[
        [
            "ID",
            "specimen",
            "series",
            "Treatment",
            "week",
            "split",
            TARGET_COL,
        ]
    ].copy()
    pred_df = pred_df.rename(columns={TARGET_COL: "y_true"})
    pred_df["y_pred"] = y_pred_all
    pred_df["residual"] = pred_df["y_pred"] - pred_df["y_true"]
    pred_df_path = args.reports_dir / "predictions_best_model.csv"
    pred_df.to_csv(pred_df_path, index=False)

    history_df = pd.concat([img_hist, multi_hist], ignore_index=True)
    history_path = args.reports_dir / "training_history.csv"
    history_df.to_csv(history_path, index=False)
    plot_learning_curves(history_df, FIGURES_DIR / "00_learning_curves.png")

    figures = create_visualizations(
        pred_df=pred_df,
        figures_dir=FIGURES_DIR,
        per_material_dir=PER_MATERIAL_DIR,
        model_comparison=model_comparison,
    )

    by_treatment = pd.read_csv(args.reports_dir / "metrics_by_treatment.csv")
    by_series = pd.read_csv(args.reports_dir / "metrics_by_series.csv")
    by_specimen = pd.read_csv(args.reports_dir / "metrics_by_specimen.csv")

    # Save artifacts for deployment.
    model_state_path = args.artifacts_dir / "best_model_state.pt"
    torch.save(best_model.state_dict(), model_state_path)
    preprocessor_path = args.artifacts_dir / "tabular_preprocessor.joblib"
    scaler_path = args.artifacts_dir / "target_scaler.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    joblib.dump(best_scaler, scaler_path)

    run_info = {
        "device": str(device),
        "random_state": args.random_state,
        "dataset": {
            **summary_dict(df),
            "corrupted_images_count": len(corrupted_ids),
            "corrupted_image_ids": corrupted_ids,
        },
        "phase2_model": {
            "best_model": best_model_name,
            "input_dim": int(x_best.shape[1]),
            "use_tabular": bool(use_tabular),
            "tabular_feature_columns": BASE_FEATURES,
            "artifacts": {
                "model_state": str(model_state_path.resolve()),
                "tabular_preprocessor": str(preprocessor_path.resolve()),
                "target_scaler": str(scaler_path.resolve()),
            },
        },
        "reports": {
            "model_comparison": str(model_comparison_path.resolve()),
            "predictions": str(pred_df_path.resolve()),
            "training_history": str(history_path.resolve()),
            "figures_dir": str(FIGURES_DIR.resolve()),
        },
    }
    run_info_path = args.artifacts_dir / "run_info.json"
    run_info_path.write_text(json.dumps(run_info, indent=2), encoding="utf-8")

    report_path = args.reports_dir / "phase2_scientific_report.md"
    write_scientific_report(
        report_path=report_path,
        run_info=run_info,
        model_metrics=model_comparison,
        figures=figures,
        by_treatment=by_treatment,
        by_series=by_series,
        by_specimen=by_specimen,
    )

    print("[INFO] Phase 2 training completed.")
    print(f"[INFO] Best model: {best_model_name}")
    print(f"[INFO] Run info: {run_info_path.resolve()}")
    print(f"[INFO] Report: {report_path.resolve()}")
    print(f"[INFO] Figures: {FIGURES_DIR.resolve()}")


if __name__ == "__main__":
    main()

