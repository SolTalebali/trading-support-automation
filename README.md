# Trading Support Automation

A Python automation tool that replaces the morning manual checklist run by an equities trading-support team. It monitors overnight batch files, validates their content, reconciles totals against the previous day, and produces a daily summary plus an exception CSV — the kind of operational tooling used to keep a trading desk safe at 08:00.

## What it does

Each run, driven by `config.yaml`:

1. **File monitoring** — checks the expected overnight files (`trades`, `positions`, `pnl`) are present in `data/raw/` and arrived before the configured cut-off (08:00 by default).
2. **Content validation** — for each file, checks column structure, key-field completeness, duplicate trade IDs, and numeric column integrity.
3. **Reconciliation** — compares today's trade count and total notional against the previous day, flagging if notional moves more than the configured tolerance (10% by default). Also reports per-file record counts.
4. **Reporting** — emits a console summary, a plain-text report (`data/processed/`), an exception CSV of bad rows (`data/errors/`), and a structured log (`logs/`).
5. **Recommendation** — concludes with `PASS` or `REVIEW REQUIRED` based on whether anything was missing, late, invalid, or out of tolerance.

## Project structure

```
trading-support-automation/
├── src/
│   ├── file_checker.py    # Missing-file and cut-off arrival checks
│   ├── validator.py       # Column, key, duplicate, and numeric checks
│   ├── reconciliation.py  # Trade count and notional comparisons vs prior day
│   ├── reporter.py        # Summary builder + console / text / CSV writers
│   └── main.py            # Pipeline entry point
├── tests/                 # PyTest tests for each module
├── data/
│   ├── raw/               # Overnight batch files land here
│   ├── processed/         # Daily summary text reports (gitignored)
│   └── errors/            # Exception CSVs (gitignored)
├── scripts/
│   └── generate_sample_data.py
├── logs/                  # Pipeline log output (gitignored)
├── config.yaml
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS / Linux
pip install -r requirements.txt
```

## Generate sample data

```bash
python scripts/generate_sample_data.py
```

Writes six files to `data/raw/`:

- **Yesterday (`20260511`)** — three clean files, all stamped before the cut-off, used as the reconciliation baseline.
- **Today (`20260512`)** — three files with deliberate issues injected (missing trade IDs, duplicates, non-numeric prices, etc.) so the pipeline has something to catch. `positions` is also stamped at 08:30 to exercise the late-arrival check.

## Run the pipeline

```bash
python -m src.main
```

Outputs:

- Console summary
- `data/processed/summary_<run_date>.txt`
- `data/errors/exceptions_<run_date>.csv` (only when validation errors were found)
- `logs/pipeline.log` (overwritten each run)

## Configuration

All behaviour is driven by `config.yaml`:

- `input_dir`, `output_path`, `error_path`, `log_path` — pipeline I/O locations.
- `run_date` — the date being checked, in `YYYYMMDD` format. Change this for replays.
- `cutoff_time` — the latest acceptable arrival time, `HH:MM`.
- `expected_files` — list of filename patterns with a `{date}` placeholder.
- `notional_tolerance_pct` — max acceptable day-on-day notional change before flagging.
- `schemas` — per-file column lists, key columns, numeric columns, and whether the file has trade IDs. Used by the validator.

## Filename convention assumption

The pipeline assumes incoming files are named `<prefix>_YYYYMMDD.csv`, with the prefix matching a key in the `schemas:` block of `config.yaml`. If an upstream feed changes its naming convention, you'll either need to update the `expected_files` pattern (if it's still templatable on a date) or pre-rename incoming files into the canonical form before the pipeline picks them up.

## Running tests

```bash
pytest
```

Each module has its own test file in `tests/`. Tests use `pytest`'s built-in `tmp_path` and `capsys` fixtures and require no external setup.
