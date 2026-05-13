"""Content validation module.

Validates column structure, key field completeness, duplicate trade IDs,
and numeric column integrity for each incoming batch file.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_columns(df: pd.DataFrame, expected_columns: list[str]) -> None:
    """Raise ValueError if any expected column is missing from df."""
    
    missing = set(expected_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns {missing}")


def check_missing_keys(df: pd.DataFrame, key_columns: list[str]) -> pd.DataFrame:
    """Return rows where any key column is null or empty."""
    
    rows_with_missing_values = df[df[key_columns].isnull().any(axis=1)]
    empty_rows = df[df[key_columns].eq("").any(axis=1)]

    return pd.concat([rows_with_missing_values, empty_rows]).drop_duplicates()


def check_duplicate_trade_ids(df: pd.DataFrame, id_column: str = "trade_id") -> pd.DataFrame:
    """Return rows with duplicate values in id_column."""
    
    duplicate_rows = df[df.duplicated(subset=[id_column], keep=False)]

    return duplicate_rows


def check_numeric_columns(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Return rows where any numeric column contains a non-numeric or null value."""
    
    df = df.copy()
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    rows_with_nulls = df[df.isnull().any(axis=1)]

    return rows_with_nulls
