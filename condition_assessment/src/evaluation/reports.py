from __future__ import annotations

from pathlib import Path

import pandas as pd


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    show = df.head(max_rows).copy() if max_rows is not None else df.copy()
    if show.empty:
        return "_No data available._"
    try:
        return show.to_markdown(index=False)
    except Exception:
        return "```\n" + show.to_string(index=False) + "\n```"


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
