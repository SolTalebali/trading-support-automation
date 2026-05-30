"""Tests for the reconciliation module."""

import pandas as pd

from src.reconciliation import (
    compare_notional,
    compare_record_counts,
    compare_trade_counts,
)


def test_compare_trade_counts():
    today_df = pd.DataFrame({
        "a": [1, 2],
        "b": [3, 4],
    })

    yersterday_df = pd.DataFrame({
        "a": [1, 2, 3, 4],
        "b": [5, 6 ,7, 8],
    })

    result = compare_trade_counts(today_df, yersterday_df)
    assert result['today'] == 2
    assert result['yesterday'] == 4
    assert result['difference'] == 2


def test_compare_notional():
    today_df = pd.DataFrame({
        "notional": [50, 100, 50]
    })

    yesterday_df = pd.DataFrame({
        "notional": [20, 30, 50]
    })

    result = compare_notional(today_df, yesterday_df, 20)
    assert result['today'] == 200
    assert result['yesterday'] == 100
    assert result['pct_change'] == 100
    assert result['exceeds_tolerance'] == True


def test_compare_record_counts():
    df1 = pd.DataFrame({
        "a": [1, 2, 4],
        "b": [7, 9, 8],
    })

    df2 = pd.DataFrame({
        "a": [1],
        "b": [2],
    })

    files = {
        "df1": df1,
        "df2": df2,
    }

    result = compare_record_counts(files)
    assert result['df1'] == 3
    assert result['df2'] == 1