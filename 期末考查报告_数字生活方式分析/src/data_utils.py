from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from urllib.request import urlretrieve

import pandas as pd

try:
    from .config import (
        DATASET_NAME,
        DATASET_PAGE_URL,
        DATASET_URL,
        FIGURES_DIR,
        PROCESSED_DATA_PATH,
        PROCESSED_DATA_DIR,
        RAW_DATA_PATH,
        RAW_DATA_DIR,
        REPORT_TABLES_DIR,
        REQUIRED_COLUMNS,
        RESULTS_DIR,
    )
except ImportError:
    from config import (
        DATASET_NAME,
        DATASET_PAGE_URL,
        DATASET_URL,
        FIGURES_DIR,
        PROCESSED_DATA_PATH,
        PROCESSED_DATA_DIR,
        RAW_DATA_PATH,
        RAW_DATA_DIR,
        REPORT_TABLES_DIR,
        REQUIRED_COLUMNS,
        RESULTS_DIR,
    )


def ensure_project_dirs() -> None:
    """Create output directories used by notebooks and scripts."""
    for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, RESULTS_DIR, REPORT_TABLES_DIR]:
        Path(path).mkdir(parents=True, exist_ok=True)


def download_dataset(force: bool = False) -> Path:
    """Download the canonical CSV if it does not already exist."""
    ensure_project_dirs()
    if RAW_DATA_PATH.exists() and not force:
        return RAW_DATA_PATH
    urlretrieve(DATASET_URL, RAW_DATA_PATH)
    return RAW_DATA_PATH


def load_raw_dataset(download: bool = True) -> pd.DataFrame:
    """Load the raw dataset, downloading it when requested."""
    if download:
        download_dataset(force=False)
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_DATA_PATH}. "
            "Run download_dataset() or place the CSV there manually."
        )
    return pd.read_csv(RAW_DATA_PATH)


def save_processed_dataset(df: pd.DataFrame, path: Path = PROCESSED_DATA_PATH) -> Path:
    """Save the processed dataset as CSV."""
    ensure_project_dirs()
    df.to_csv(path, index=False)
    return path


def load_processed_dataset(fallback_to_raw: bool = True) -> pd.DataFrame:
    """Load processed data, optionally falling back to raw data."""
    if PROCESSED_DATA_PATH.exists():
        return pd.read_csv(PROCESSED_DATA_PATH)
    if fallback_to_raw:
        return load_raw_dataset(download=True)
    raise FileNotFoundError(f"Processed dataset not found: {PROCESSED_DATA_PATH}")


def validate_required_columns(df: pd.DataFrame, required: Iterable[str] = REQUIRED_COLUMNS) -> pd.DataFrame:
    """Return a column-level schema check table."""
    rows = []
    columns = set(df.columns)
    for column in required:
        rows.append(
            {
                "column": column,
                "present": column in columns,
                "dtype": str(df[column].dtype) if column in columns else "",
                "missing_count": int(df[column].isna().sum()) if column in columns else None,
            }
        )
    return pd.DataFrame(rows)


def dataset_compliance_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact dataset source and reproducibility summary."""
    return pd.DataFrame(
        [
            {"item": "dataset_name", "value": DATASET_NAME},
            {"item": "source_page", "value": DATASET_PAGE_URL},
            {"item": "canonical_csv", "value": DATASET_URL},
            {"item": "license", "value": "CC BY 4.0, according to the Hugging Face dataset card"},
            {"item": "row_count", "value": int(df.shape[0])},
            {"item": "column_count", "value": int(df.shape[1])},
            {"item": "random_state", "value": 42},
            {"item": "cpu_only", "value": True},
            {"item": "deep_learning", "value": False},
        ]
    )


def save_json(data: dict, path: Path) -> Path:
    """Write a small JSON file with UTF-8 encoding."""
    ensure_project_dirs()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def describe_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a numeric summary table that is stable for CSV export."""
    summary = df.describe(include="all").transpose().reset_index().rename(columns={"index": "column"})
    return summary


def missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a missing-value summary sorted by missing rate."""
    out = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": df.isna().sum().astype(int).values,
            "missing_rate": df.isna().mean().values,
        }
    )
    return out.sort_values(["missing_rate", "missing_count"], ascending=False).reset_index(drop=True)

