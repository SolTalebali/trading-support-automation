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
    
    records_processed = sum(v["total_rows"] for v in validation_results.values())
    validation_errors = sum(
        v["missing_keys"] + v["duplicates"] + v["bad_numerics"] 
        for v in validation_results.values()
    )

    recommendation = "REVIEW REQUIRED"

    if (not file_results["missing"] 
            and not file_results["late"] 
            and validation_errors == 0 
            and (recon_results is None or not recon_results["notional"]["exceeds_tolerance"])):
        
        recommendation = "PASS"

    summary = {
        "missing_files": file_results["missing"],
        "late_files": file_results["late"],
        "files_received": len(file_results["missing"]) == 0,
        "records_processed": records_processed,
        "validation_errors": validation_errors,
        "validation_details": validation_results,
        "reconciliation": recon_results,
        "recommendation": recommendation,
    }

    return summary


def write_console_report(summary: dict) -> None:
    """Print the daily support summary to stdout."""
    
    for k, v in summary.items():
        print(f"{k}: {v}")


def write_text_report(summary: dict, output_path: str) -> None:
    """Write the daily summary as a plain-text file."""
    pass


def write_exception_csv(exceptions: pd.DataFrame, output_path: str) -> None:
    """Write exception rows to a CSV file."""
    pass
