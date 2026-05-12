"""File monitoring module.

Checks whether expected overnight batch files exist in the input directory,
verifies they arrived before the configured cut-off time, and identifies
any missing files.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_files_exist(input_dir: str, date: str, expected_files: list[str]) -> dict[str, bool]:
    """Return a mapping of filename -> exists for each expected file."""
    pass


def check_arrival_time(file_path: Path, cutoff_time: str) -> bool:
    """Return True if the file's modification time is before cutoff_time on its date."""
    pass


def get_missing_files(input_dir: str, date: str, expected_files: list[str]) -> list[str]:
    """Return a list of expected filenames that are absent from input_dir."""
    pass
