"""Pipeline entry point.

Wires together file_checker, validator, reconciliation, and reporter stages
into a single end-to-end daily support run driven by config.yaml.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def run() -> None:
    """Run the end-to-end daily support automation."""
    pass


if __name__ == "__main__":
    run()
