"""Tests for the reporter module."""

import pandas as pd
import pytest
from src.reporter import build_summary, write_console_report, write_exception_csv, write_text_report


def _clean_validation_results():
    return {
        "trades_20260512.csv": {
            "columns_ok": True,
            "total_rows": 5,
            "missing_keys": 0,
            "duplicates": 0,
            "bad_numerics": 0,
        },
        "positions_20260512.csv": {
            "columns_ok": True,
            "total_rows": 3,
            "missing_keys": 0,
            "duplicates": 0,
            "bad_numerics": 0,
        },
    }


def _clean_recon_results():
    return {
        "trade_counts": {"today": 5, "yesterday": 5, "difference": 0},
        "notional": {"today": 100, "yesterday": 100, "pct_change": 0, "exceeds_tolerance": False},
        "record_counts": {"trades_20260512.csv": 5, "positions_20260512.csv": 3},
    }


def test_build_summary_pass_case():
    file_results = {"missing": [], "late": []}
    summary = build_summary(file_results, _clean_validation_results(), _clean_recon_results())

    assert summary["files_received"] is True
    assert summary["records_processed"] == 8
    assert summary["validation_errors"] == 0
    assert summary["recommendation"] == "PASS"


def test_build_summary_review_when_files_missing():
    file_results = {"missing": ["pnl_20260512.csv"], "late": []}
    summary = build_summary(file_results, _clean_validation_results(), _clean_recon_results())

    assert summary["files_received"] is False
    assert summary["recommendation"] == "REVIEW REQUIRED"


def test_build_summary_review_when_validation_errors():
    file_results = {"missing": [], "late": []}
    validation = _clean_validation_results()
    validation["trades_20260512.csv"]["missing_keys"] = 2

    summary = build_summary(file_results, validation, _clean_recon_results())

    assert summary["validation_errors"] == 2
    assert summary["recommendation"] == "REVIEW REQUIRED"


def test_build_summary_review_when_tolerance_exceeded():
    file_results = {"missing": [], "late": []}
    recon = _clean_recon_results()
    recon["notional"]["exceeds_tolerance"] = True

    summary = build_summary(file_results, _clean_validation_results(), recon)

    assert summary["recommendation"] == "REVIEW REQUIRED"


def test_build_summary_handles_skipped_reconciliation():
    file_results = {"missing": [], "late": []}
    summary = build_summary(file_results, _clean_validation_results(), None)

    assert summary["reconciliation"] is None
    assert summary["recommendation"] == "REVIEW REQUIRED"


def test_write_text_report_writes_summary_to_file(tmp_path):
    summary = {"files_received": True, "recommendation": "PASS", "records_processed": 8}
    output_path = tmp_path / "summary.txt"

    write_text_report(summary, output_path)

    content = output_path.read_text()
    assert "files_received: True" in content
    assert "recommendation: PASS" in content
    assert "records_processed: 8" in content


def test_write_exception_csv_skips_when_empty(tmp_path):
    output_path = tmp_path / "exceptions.csv"
    empty_df = pd.DataFrame()

    write_exception_csv(empty_df, output_path)

    assert not output_path.exists()


def test_write_exception_csv_writes_rows(tmp_path):
    output_path = tmp_path / "exceptions.csv"
    df = pd.DataFrame({
        "trade_id": ["T1", "T2"],
        "reason": ["duplicate", "missing_key"],
        "source_file": ["trades_20260512.csv", "trades_20260512.csv"],
    })

    write_exception_csv(df, output_path)

    assert output_path.exists()
    written = pd.read_csv(output_path)
    assert len(written) == 2
    assert list(written.columns) == ["trade_id", "reason", "source_file"]


def test_write_console_report_prints_summary(capsys):
    summary = {"recommendation": "PASS", "records_processed": 8}

    write_console_report(summary)

    captured = capsys.readouterr()
    assert "recommendation" in captured.out
    assert "PASS" in captured.out
