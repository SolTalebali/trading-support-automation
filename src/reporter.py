"""Reporting module.

Builds the daily support summary and writes output in three formats:
console report, plain-text file, and CSV exception report.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def build_summary(
    file_results: dict,
    validation_results: dict,
    recon_results: dict,
) -> dict:
    """Assemble a summary dict from file check, validation, and reconciliation results."""
    
    summary = {
        "missing_files": file_results["missing"],
        "late_files": file_results["late"],
        "files_received": len(file_results["missing"]) == 0
    }


def write_console_report(summary: dict) -> None:
    """Print the daily support summary to stdout."""
    pass


def write_text_report(summary: dict, output_path: str) -> None:
    """Write the daily summary as a plain-text file."""
    pass


def write_exception_csv(exceptions: pd.DataFrame, output_path: str) -> None:
    """Write exception rows to a CSV file."""
    pass
