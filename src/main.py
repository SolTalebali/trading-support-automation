"""Pipeline entry point.

Wires together file_checker, validator, reconciliation, and reporter stages
into a single end-to-end daily support run driven by config.yaml.
"""

import logging
from pathlib import Path
import yaml
import pandas as pd

from datetime import datetime, timedelta
from src.file_checker import get_missing_files, arrived_on_time
from src.validator import validate_columns, check_missing_keys, check_duplicate_trade_ids, check_numeric_columns
from src.reconciliation import compare_notional, compare_record_counts, compare_trade_counts

logger = logging.getLogger(__name__)


def run() -> None:
    """Run the end-to-end daily support automation."""
    
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    logging.basicConfig(
        filename=config["log_path"],
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger.info("Pipeline started for run_date=%s", config["run_date"])

    missing_files = get_missing_files(config["input_dir"], config["run_date"], config["expected_files"])
    late_files = []
    loaded_files = {}

    for file in config["expected_files"]:
        file_name = file.replace("{date}", config["run_date"])
        if file_name in missing_files:
            continue
        input_path = Path(config["input_dir"]) / file_name
        loaded_files[file_name] = pd.read_csv(input_path)

        if not arrived_on_time(input_path, config["cutoff_time"]):
            late_files.append(file_name)

    file_results = {
        "missing": missing_files,
        "late": late_files,
    }
    

    validation_results = {}
    exception_rows = []

    for file_name, df in loaded_files.items():
        schema_key = file_name.split("_")[0]
        schema = config["schemas"][schema_key]
        
        try:
            validate_columns(df, schema["columns"])
            columns_ok = True
        except ValueError as e:
            logger.warning("Column validation failed for %s: %s", file_name, e)
            columns_ok = False

        if columns_ok:
            missing_key_rows = check_missing_keys(df, schema["key_columns"])
            bad_numeric_rows = check_numeric_columns(df, schema["numeric_columns"])
            duplicate_rows = check_duplicate_trade_ids(df) if schema["has_trade_id"] else df.iloc[0:0]
        else:
            missing_key_rows = bad_numeric_rows = duplicate_rows = df.iloc[0:0]
        
        validation_results[file_name] = {
            "columns_ok": columns_ok,
            "total_rows": len(df),
            "missing_keys": len(missing_key_rows),
            "duplicates": len(duplicate_rows),
            "bad_numerics": len(bad_numeric_rows),
        }

        for label, bad_rows in [
            ("missing_key", missing_key_rows),
            ("bad_numeric", bad_numeric_rows),
            ("duplicate", duplicate_rows),
        ]:
            if not bad_rows.empty:
                tagged = bad_rows.copy()
                tagged["source_file"] = file_name
                tagged["reason"] = label
                exception_rows.append(tagged)


    yesterday_date = (datetime.strptime(config["run_date"], "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    yesterday_trade_path = Path(config["input_dir"]) / f"trades_{yesterday_date}.csv"
    today_trades_name = f"trades_{config['run_date']}.csv"
    recon_results = None

    if today_trades_name in loaded_files and yesterday_trade_path.exists(): 
        yesterday_trades = pd.read_csv(yesterday_trade_path)
        today_trades = loaded_files[today_trades_name]
        
        recon_results = {
            "trade_counts": compare_trade_counts(today_trades, yesterday_trades),
            "notional": compare_notional(today_trades, yesterday_trades, config["notional_tolerance_pct"]),
            "record_counts": compare_record_counts(loaded_files),
        }
    else:
        logger.warning("Skipping reconciliation: today or yesterday trades file unavailable")


if __name__ == "__main__":
    run()
