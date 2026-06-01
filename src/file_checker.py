"""File monitoring module.

Identifies missing overnight batch files and verifies that files which
did arrive came in before the configured cut-off time.
"""

import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def arrived_on_time(file_path: Path, cutoff_time: str, run_date: str) -> bool:
    """Return True if the file's modification datetime is before run_date + cutoff_time."""

    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
    cutoff_datetime = datetime.strptime(f"{run_date} {cutoff_time}", "%Y%m%d %H:%M")

    return file_modified < cutoff_datetime


def get_missing_files(input_dir: str, date: str, expected_files: list[str]) -> list[str]:
    """Return a list of expected filenames that are absent from input_dir."""
    
    missing_files = []
    
    for file in expected_files:
        file_name = file.replace("{date}", date)
        input_path = Path(input_dir) / file_name

        if not input_path.exists():
            missing_files.append(file_name)
    
    return missing_files
