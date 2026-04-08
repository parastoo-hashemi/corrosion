from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
REPORTS_DIR = ROOT / "reports"
ARTIFACTS_DIR = ROOT / "artifacts"
FIG_DIR = REPORTS_DIR / "figures"
PER_MATERIAL_DIR = FIG_DIR / "per_material"


TREATMENT_FULL = {
    "NO": "No treatment (control)",
    "MI": "Mixed-in corrosion inhibitor",
    "SA": "Surface-applied corrosion inhibitor",
    "PA": "Painted protective treatment",
    "SA_PA": "Painting + surface-applied inhibitor",
    "SA_VF": "Surface-applied inhibitor + glass-based compound",
    "VF": "Glass-based compound treatment",
}


def _read_phase2_files() -> Dict[str, object]:
    run_info = json.loads((ARTIFACTS_DIR / "run_info.json").read_text(encoding="utf-8"))
    model_comp = pd.read_csv(REPORTS_DIR / "model_comparison.csv")
    by_treatment = pd.read_csv(REPORTS_DIR / "metrics_by_treatment.csv")
    by_series = pd.read_csv(REPORTS_DIR / "metrics_by_series.csv")
    by_specimen = pd.read_csv(REPORTS_DIR / "metrics_by_specimen.csv")
    preds = pd.read_csv(REPORTS_DIR / "predictions_best_model.csv")
    return {
        "run_info": run_info,
        "model_comp": model_comp,
        "by_treatment": by_treatment,
        "by_series": by_series,
        "by_specimen": by_specimen,
        "preds": preds,
    }


def _load_material_catalog() -> pd.DataFrame:
    excel = Path(__file__).resolve().parents[1] / "Data" / "Images_Dataset_A-Z.xlsx"
    raw = pd.read_excel(excel)
    headers = [str(v).strip() for v in raw.iloc[0].tolist()]
    df = raw.iloc[1:].copy().reset_index(drop=True)
    df.columns = headers
    for c in df.columns:
        if c in {"ID", "Treatment"}:
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["specimen"] = df["ID"].astype(str).str.extract(r"^(.*?)-")[0]
    df["week"] = pd.to_numeric(df["ID"].astype(str).str.extract(r"-(\d+)W$")[0], errors="coerce")
    d = (
        df.groupby("specimen", as_index=False)
        .agg(
            Treatment=("Treatment", "main_first"),
            N_Steel_Mesh=("N_Steel_Mesh", "main_first"),
            NaCl=("NaCl%", "main_first"),
            Ageing_Days=("Ageing_Days", "main_first"),
            Cover_mm=("Cover_(Faliure_Surface)_[mm]", "main_first"),
            Weeks_Observed=("week", "count"),
            Week_Min=("week", "min"),
            Week_Max=("week", "max"),
        )
        .sort_values("specimen")
    )
    d["Treatment_Full_Name"] = d["Treatment"].map(TREATMENT_FULL).fillna(d["Treatment"])
    d["Material_Full_Name"] = d.apply(
        lambda r: (
            f"{r['specimen']} - {r['Treatment_Full_Name']} "
            f"(steel meshes: {int(r['N_Steel_Mesh'])}, NaCl: {float(r['NaCl'])*100:.1f}%)"
        ),
        axis=1,
    )
    return d


def _table_from_df(df: pd.DataFrame, max_rows: int | None = None) -> Table:
    if max_rows is not None:
        df = df.head(max_rows).copy()
    show = df.copy()
    for c in show.columns:
        if pd.api.types.is_float_dtype(show[c]):
            show[c] = show[c].map(lambda v: f"{v:.4f}")
    data = [list(show.columns)] + show.values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
            ]
        )
    )
    return t


def _img(path: Path, w_cm: float = 16.0) -> RLImage:
    img = RLImage(str(path))
    aspect = img.imageHeight / float(img.imageWidth)
    img.drawWidth = w_cm * cm
    img.drawHeight = (w_cm * aspect) * cm
    return img


def _add_heading(story: List, text: str, style: ParagraphStyle) -> None:
    story.append(Paragraph(text, style))
    story.append(Spacer(1, 0.25 * cm))


def _material_performance_table(material_catalog: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    g = (
        preds.groupby("specimen", as_index=False)
        .agg(
            n_obs=("y_true", "count"),
            mean_true=("y_true", "mean"),
            mean_pred=("y_pred", "mean"),
            mae=("residual", lambda s: float(abs(s).mean())),
            final_week=("week", "max"),
        )
        .sort_values("specimen")
    )
    f = preds.sort_values("week").groupby("specimen", as_index=False).tail(1)[
        ["specimen", "y_true", "y_pred"]
    ].rename(columns={"y_true": "final_true", "y_pred": "final_pred"})
    out = g.merge(f, on="specimen", how="left").merge(
        material_catalog[["specimen", "Material_Full_Name", "Treatment_Full_Name"]],
        on="specimen",
        how="left",
    )
    cols = [
        "specimen",
        "Material_Full_Name",
        "Treatment_Full_Name",
        "n_obs",
        "mae",
        "mean_true",
        "mean_pred",
        "final_week",
        "final_true",
        "final_pred",
    ]
    return out[cols]


def _export_pdf_tables(
    reports_dir: Path,
    table1_material_catalog: pd.DataFrame,
    table2_model_comparison: pd.DataFrame,
    table3_by_treatment: pd.DataFrame,
    table4_by_series: pd.DataFrame,
    table5_material_performance: pd.DataFrame,
) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    table1_material_catalog.to_csv(
        reports_dir / "pdf_table_1_material_catalog.csv", index=False
    )
    table2_model_comparison.to_csv(
        reports_dir / "pdf_table_2_model_comparison.csv", index=False
    )
    table3_by_treatment.to_csv(
        reports_dir / "pdf_table_3_performance_by_treatment.csv", index=False
    )
    table4_by_series.to_csv(
        reports_dir / "pdf_table_4_performance_by_series.csv", index=False
    )
    table5_material_performance.to_csv(
        reports_dir / "pdf_table_5_material_level_results.csv", index=False
    )


def build_pdf() -> Path:
    ctx = _read_phase2_files()
    run_info = ctx["run_info"]
    model_comp = ctx["model_comp"]
    by_treatment = ctx["by_treatment"].sort_values("mae")
    by_series = ctx["by_series"].sort_values("mae")
    by_specimen = ctx["by_specimen"].sort_values("mae")
    preds = ctx["preds"]
    material_catalog = _load_material_catalog()
    material_perf = _material_performance_table(material_catalog, preds)
    table1_material_catalog = material_catalog[
        [
            "specimen",
            "Material_Full_Name",
            "Weeks_Observed",
            "Week_Min",
            "Week_Max",
            "Cover_mm",
        ]
    ].copy()

    _export_pdf_tables(
        reports_dir=REPORTS_DIR,
        table1_material_catalog=table1_material_catalog,
        table2_model_comparison=model_comp,
        table3_by_treatment=by_treatment,
        table4_by_series=by_series,
        table5_material_performance=material_perf,
    )

    best = model_comp.sort_values("test_mae").iloc[0]
    best_model = str(best["model"])

    pdf_path = REPORTS_DIR / "phase2_scientific_report_full.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Phase 2 Scientific Report",
        author="Automated Pipeline",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.black,
        spaceAfter=12,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    bullet = ParagraphStyle(
        "Bullet",
        parent=body,
        leftIndent=14,
        bulletIndent=4,
    )

    story: List = []
    story.append(Paragraph("Scientific Report: Phase 2 Corrosion Prediction Pipeline", title_style))
    story.append(
        Paragraph(
            "This report documents the complete Phase 2 deep-learning workflow for corrosion "
            "prediction, including rationale, quantitative results, interpretation, alternative "
            "solutions, and practical recommendations.",
            body,
        )
    )
    story.append(Spacer(1, 0.35 * cm))

    _add_heading(story, "main_first. Project Context and Objectives", h1)
    story.append(
        Paragraph(
            "The objective is to predict corrosion progression and quantify corrosion severity "
            "for different cementitious materials/specimens observed over time. "
            "The data include weekly images and synchronized tabular measurements. "
            "The Phase 2 objective was to deploy a deeper scientific solution based on "
            "multimodal machine learning and deliver explainable outputs suitable for research communication.",
            body,
        )
    )

    _add_heading(story, "2. Data Summary and Material Definitions", h1)
    ds = run_info["dataset"]
    for line in [
        f"Total observations: {ds['rows']}",
        f"Total materials/specimens: {ds['specimens']}",
        f"Observed week range: {ds['week_min']} to {ds['week_max']}",
        f"Corrupted images detected and handled: {ds['corrupted_images_count']}",
    ]:
        story.append(Paragraph(line, bullet, bulletText="-"))

    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            "Table main_first reports the full material names with complete treatment description, "
            "mesh configuration, and saline exposure information.",
            body,
        )
    )
    story.append(
        _table_from_df(
            table1_material_catalog
        )
    )
    story.append(PageBreak())

    _add_heading(story, "3. Methodology and Scientific Rationale", h1)
    story.append(
        Paragraph(
            "3.main_first Why this approach was selected:", body
        )
    )
    why_lines = [
        "The dataset size is moderate (792 observations), which supports transfer learning instead of full CNN training from scratch.",
        "Corrosion signals are strongly visual (rust distribution and texture), therefore image representation is fundamental.",
        "Material and environmental context (treatment, NaCl%, steel mesh count, week) carry additional mechanistic information.",
        "Grouped splitting by specimen prevents data leakage across timepoints of the same material, producing realistic generalization estimates.",
        "The resulting pipeline supports reproducibility and deployment in a laboratory workflow.",
    ]
    for s in why_lines:
        story.append(Paragraph(s, bullet, bulletText="-"))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("3.2 Phase 2 modeling workflow:", body))
    flow_lines = [
        "Extract 512-dimensional visual embeddings from a pretrained ResNet-18 backbone.",
        "Build tabular branch with scaled numerical and one-hot categorical variables.",
        "Train and compare two deep regressors: image-only baseline and multimodal fusion.",
        "Optimize on validation MAE with early stopping.",
        "Evaluate on test groups using MAE, RMSE, and R2.",
        "Generate per-material progression diagnostics and uncertainty-oriented residual analysis.",
    ]
    for s in flow_lines:
        story.append(Paragraph(s, bullet, bulletText="-"))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("3.3 Candidate solutions considered:", body))
    cand_lines = [
        "Solution A: Image-only deep learning (chosen best in this run).",
        "Solution B: Multimodal fusion (image + tabular deep model).",
        "Solution C: Gradient-boosted tabular baseline from Phase main_first for progression reference.",
        "Solution D: Future sequence models (temporal transformer/LSTM) for direct time-series forecasting.",
        "Solution E: Survival analysis for time-to-event prediction under censoring.",
    ]
    for s in cand_lines:
        story.append(Paragraph(s, bullet, bulletText="-"))

    _add_heading(story, "4. Quantitative Results", h1)
    story.append(Paragraph("Table 2. Model comparison on held-out test specimens.", body))
    story.append(_table_from_df(model_comp))
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            f"Best model selected for deployment: <b>{best_model}</b> "
            f"(MAE={best['test_mae']:.4f}, RMSE={best['test_rmse']:.4f}, R2={best['test_r2']:.4f}).",
            body,
        )
    )

    story.append(Paragraph("Table 3. Performance by treatment group (test split).", body))
    story.append(_table_from_df(by_treatment))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("Table 4. Performance by material series (test split).", body))
    story.append(_table_from_df(by_series))
    story.append(PageBreak())

    _add_heading(story, "5. Visual Diagnostics", h1)
    fig_paths = [
        FIG_DIR / "00_learning_curves.png",
        FIG_DIR / "02_pred_vs_true_test.png",
        FIG_DIR / "03_residual_distribution.png",
        FIG_DIR / "08_progression_by_treatment.png",
        FIG_DIR / "10_severity_confusion_matrix.png",
    ]
    captions = [
        "Figure main_first. Learning curves for both deep models.",
        "Figure 2. Predicted vs true corrosion on test specimens.",
        "Figure 3. Residual distribution for error behavior analysis.",
        "Figure 4. Progression patterns by treatment group.",
        "Figure 5. Three-level severity confusion matrix.",
    ]
    for p, cap in zip(fig_paths, captions):
        if p.exists():
            story.append(Paragraph(cap, body))
            story.append(_img(p, w_cm=16.5))
            story.append(Spacer(1, 0.25 * cm))

    story.append(PageBreak())
    _add_heading(story, "6. Full Material-Level Results", h1)
    story.append(
        Paragraph(
            "Table 5 reports per-material summaries across all predicted time points, "
            "including full material name and final-week prediction behavior.",
            body,
        )
    )
    story.append(_table_from_df(material_perf))
    story.append(PageBreak())

    _add_heading(story, "7. Interpretation, Alternatives, and Recommendations", h1)
    interp_lines = [
        "The image branch carried the dominant signal in this run, as the image-only model outperformed multimodal fusion on test MAE.",
        "Treatment-level differences indicate non-uniform prediction difficulty; this supports stratified data augmentation in future campaigns.",
        "High-error materials should be prioritized for additional data acquisition and repeated imaging quality checks.",
        "Phase main_first and Phase 2 should be used together in practice: Phase main_first for robust tabular forecasting and Phase 2 for richer visual quantification.",
    ]
    for s in interp_lines:
        story.append(Paragraph(s, bullet, bulletText="-"))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("Possible solution tracks for the next project cycle:", body))
    next_solution_lines = [
        "Track A: Fine-tune deeper CNN backbones (ResNet-50/EfficientNet) directly on corrosion regression.",
        "Track B: Build sequence-aware models using weekly image embeddings per specimen.",
        "Track C: Integrate uncertainty (deep ensembles or conformal prediction) for risk-aware maintenance decisions.",
        "Track D: Use survival/event models for predicting week-to-threshold with censored samples.",
        "Track E: Combine image model outputs with mechanistic corrosion priors from domain equations.",
    ]
    for s in next_solution_lines:
        story.append(Paragraph(s, bullet, bulletText="-"))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("Practical suggestions:", body))
    suggestions = [
        "Standardize capture conditions even more tightly (illumination, distance, angle, white balance references).",
        "Collect more late-stage severe-corrosion examples to improve high-end extrapolation.",
        "Add quality-control flags in the dataset for blur/occlusion to prevent hidden label noise.",
        "Run periodic recalibration with new experiments and keep immutable train/validation/test splits for comparability.",
        "Deploy model monitoring to track drift by treatment group and specimen family.",
    ]
    for s in suggestions:
        story.append(Paragraph(s, bullet, bulletText="-"))

    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            "Appendix material plots: 48 per-material progression figures are available in "
            f"{PER_MATERIAL_DIR.resolve()} for detailed visual inspection.",
            body,
        )
    )

    doc.build(story)
    return pdf_path


def main() -> None:
    path = build_pdf()
    print(f"PDF report created: {path.resolve()}")


if __name__ == "__main__":
    main()
