"""Reconciliation module.

Compares today's batch file totals against yesterday's: trade counts,
total notional, and record counts across files.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def compare_trade_counts(today: pd.DataFrame, yesterday: pd.DataFrame) -> dict:
    """Return a dict with today/yesterday counts and the absolute difference."""
    
    today_count = len(today)
    yesterday_count = len(yesterday)
    difference = abs(today_count - yesterday_count)

    trade_counts = {
        "today": today_count,
        "yesterday": yesterday_count,
        "difference": difference
    }

    return trade_counts


def compare_notional(
    today: pd.DataFrame, yesterday: pd.DataFrame, tolerance_pct: float) -> dict:
    """Return notional totals, percentage change, and whether it exceeds tolerance."""
    
    today_notional_sum = today["notional"].sum()
    yesterday_notional_sum = yesterday["notional"].sum()
    pct_change = abs(today_notional_sum - yesterday_notional_sum) / yesterday_notional_sum * 100
    
    notional_data = {
        "today": round(float(today_notional_sum), 2),
        "yesterday": round(float(yesterday_notional_sum), 2),
        "pct_change": round(float(pct_change), 2),
        "exceeds_tolerance": bool(pct_change > tolerance_pct)
    }

    return notional_data


def compare_record_counts(files: dict[str, pd.DataFrame]) -> dict:
    """Return a mapping of filename -> record count for each file in files."""
    
    record_counts = {}

    for filename, df in files.items():
        record_counts[filename] = len(df)

    return record_counts