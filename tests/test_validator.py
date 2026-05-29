"""Tests for the validator module."""

import pandas as pd
import pytest

from src.validator import (
    check_duplicate_trade_ids,
    check_missing_keys,
    check_numeric_columns,
    validate_columns,
)

def test_validate_columns_positive():
    df = pd.DataFrame({
        "a": [1],
        "b": [2],
    })

    validate_columns(df, ["a", "b"])


def test_validate_columns_negative():
    df = pd.DataFrame({
        "a": [1],
        "b" : [2],
    })

    with pytest.raises(ValueError):
        validate_columns(df, ["a", "b", "c"])


def test_check_missing_keys_positive():
    df = pd.DataFrame({
        "A": ["a"],
         "B": ["b"],
    })

    result = check_missing_keys(df, ["A", "B"])
    assert result.empty


def test_check_missing_keys_negative():
    df = pd.DataFrame({
        "A": ["a", "b"],
        "B": ["", "b"],
        "C": ["a", None]
    })

    result = check_missing_keys(df, ["A", "B", "C"])
    assert len(result) == 2


def test_check_duplicate_trade_ids_positive():
    df = pd.DataFrame({
        "trade_id": [1, 2, 3, 4]
    })

    result = check_duplicate_trade_ids(df)
    assert len(result) == 0


def test_check_duplicate_trade_ids_negative():
    df = pd.DataFrame({
        "trade_id": [1, 2, 1, 3, 3, 4]
    })

    result = check_duplicate_trade_ids(df)
    assert len(result) == 4


def test_check_numeric_columns_positive():
    df = pd.DataFrame({
        "a": [1, 2],
        "b" : [2, 3],
    })

    result = check_numeric_columns(df, ["a", "b"])
    assert len(result) == 0


def test_check_numeric_columns_negative():
    df = pd.DataFrame({
        "a": [1, "2"],
        "b" : ["hi", 3],
        "c": [4, 5]
    })

    result = check_numeric_columns(df , ["a", "b", "c"])
    assert len(result) == 1