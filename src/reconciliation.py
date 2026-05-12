"""Reconciliation module.

Compares today's batch file totals against yesterday's: trade counts,
total notional, and record counts across files.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def load_previous_day(file_path: str) -> pd.DataFrame:
    """Load a previous day's batch file for comparison."""
    pass


def compare_trade_counts(today: pd.DataFrame, yesterday: pd.DataFrame) -> dict:
    """Return a dict with today/yesterday counts and the absolute difference."""
    pass


def compare_notional(
    today: pd.DataFrame, yesterday: pd.DataFrame, tolerance_pct: float
) -> dict:
    """Return notional totals, percentage change, and whether it exceeds tolerance."""
    pass


def compare_record_counts(files: dict[str, pd.DataFrame]) -> dict:
    """Return a mapping of filename -> record count for each file in files."""
    pass
