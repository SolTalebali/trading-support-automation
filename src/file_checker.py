"""File monitoring module.

Identifies missing overnight batch files and verifies that files which
did arrive came in before the configured cut-off time.
"""

import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def arrived_on_time(file_path: Path, cutoff_time: str) -> bool:
    """Return True if the file's modification time is before cutoff_time on its date."""

    file_modified_time = datetime.fromtimestamp(file_path.stat().st_mtime).time()
    cutoff_time_datetime = datetime.strptime(cutoff_time, "%H:%M").time()

    return file_modified_time < cutoff_time_datetime


def get_missing_files(input_dir: str, date: str, expected_files: list[str]) -> list[str]:
    """Return a list of expected filenames that are absent from input_dir."""
    
    missing_files = []
    
    for file in expected_files:
        file_name = file.replace("{date}", date)
        input_path = Path(input_dir) / file_name

        if not input_path.exists():
            missing_files.append(file_name)
    
    return missing_files
