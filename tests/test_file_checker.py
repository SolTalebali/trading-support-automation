"""Tests for the file_checker module."""

import os
from src.file_checker import arrived_on_time, get_missing_files
from datetime import datetime

def test_get_missing_files_all_files_present(tmp_path):
    (tmp_path / "trades_20260512.csv").touch()
    (tmp_path / "positions_20260512.csv").touch()
    (tmp_path / "pnl_20260512.csv").touch()

    result = get_missing_files(
        str(tmp_path),
        "20260512",
        ["trades_{date}.csv", "positions_{date}.csv", "pnl_{date}.csv"]
    )

    assert result == []


def test_get_missing_files_one_missing_file(tmp_path):
    (tmp_path / "trades_20260512.csv").touch()
    (tmp_path / "positions_20260512.csv").touch()

    result = get_missing_files(
        str(tmp_path),
        "20260512",
        ["trades_{date}.csv", "positions_{date}.csv", "pnl_{date}.csv"]
    )

    assert result == ["pnl_20260512.csv"]


def test_get_missing_files_all_files_missing(tmp_path):
    result = get_missing_files(
        str(tmp_path),
        "20260512",
        ["trades_{date}.csv", "positions_{date}.csv", "pnl_{date}.csv"]
    )

    assert result == ["trades_20260512.csv", "positions_20260512.csv", "pnl_20260512.csv"]


def test_arrived_on_time_positive(tmp_path):
    (tmp_path / "trades_20260512.csv").touch()

    timestamp = datetime(2026, 5, 12, 7 ,30).timestamp()
    os.utime(tmp_path / "trades_20260512.csv", (timestamp, timestamp))

    result = arrived_on_time(tmp_path / "trades_20260512.csv", "08:00", "20260512")

    assert result


def test_arrived_on_time_negative(tmp_path):
    (tmp_path / "trades_20260512.csv").touch()

    timestamp = datetime(2026, 5, 12, 8 ,30).timestamp()
    os.utime(tmp_path / "trades_20260512.csv", (timestamp, timestamp))

    result = arrived_on_time(tmp_path / "trades_20260512.csv", "08:00", "20260512")

    assert not result
