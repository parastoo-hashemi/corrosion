from __future__ import annotations

import os
from pathlib import Path

from .utils_paths import OUTPUT_DIR, ensure_dir

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid")


def save_barplot(df: pd.DataFrame, x: str, y: str, title: str, path: Path, rotation: int = 0):
    ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x=x, y=y, ax=ax, color="#4C78A8")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=rotation)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_histograms(df: pd.DataFrame, columns: list[str], path: Path, bins: int = 30):
    ensure_dir(path.parent)
    fig, axes = plt.subplots(len(columns), 1, figsize=(10, 4 * len(columns)))
    if len(columns) == 1:
        axes = [axes]
    for ax, column in zip(axes, columns):
        sns.histplot(df[column].dropna(), bins=bins, kde=True, ax=ax, color="#59A14F")
        ax.set_title(column)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_missingness_plot(missing_df: pd.DataFrame, path: Path):
    ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=missing_df, x="column", y="missing_count", ax=ax, color="#E15759")
    ax.set_title("Column Missingness")
    ax.tick_params(axis="x", rotation=60)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_lineplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: str,
    title: str,
    path: Path,
    style: str | None = None,
):
    ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x=x, y=y, hue=hue, style=style, ax=ax, linewidth=1.4)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_boxplot(df: pd.DataFrame, x: str, y: str, title: str, path: Path, rotation: int = 0):
    ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x=x, y=y, ax=ax, color="#76B7B2")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=rotation)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_feature_importance_plot(df: pd.DataFrame, title: str, path: Path, top_n: int = 20):
    ensure_dir(path.parent)
    plot_df = df.head(top_n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.3)))
    sns.barplot(data=plot_df, x="importance", y="feature", ax=ax, color="#F28E2B")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
