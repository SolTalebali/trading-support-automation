# Trading Support Automation

A Python automation script that performs daily morning support checks for an equities technology team: overnight file monitoring, content validation, reconciliation against prior day, and exception reporting.

## Project structure

```
trading-support-automation/
├── src/
│   ├── file_checker.py    # File arrival checks and missing file detection
│   ├── validator.py       # Column, key field, duplicate, and numeric validation
│   ├── reconciliation.py  # Trade count and notional comparisons vs prior day
│   ├── reporter.py        # Console, text, and CSV exception output
│   └── main.py            # Pipeline entry point
├── tests/                 # Per-module PyTest test files
├── data/
│   ├── raw/               # Overnight batch files land here (trades, positions, pnl)
│   ├── processed/         # Daily summary reports (gitignored)
│   └── errors/            # Exception CSVs (gitignored)
├── scripts/
│   └── generate_sample_data.py
├── logs/                  # Pipeline log output (gitignored)
└── config.yaml
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Generate sample data

```bash
python scripts/generate_sample_data.py
```

Writes six files to `data/raw/`: clean baseline files for yesterday (`20260511`) and deliberately flawed files for today (`20260512`) for the pipeline to process.

## Usage

```bash
python -m src.main
```

## Configuration

Edit `config.yaml` to change the run date, input directory, cut-off time, expected file names, or notional tolerance threshold.

## Running tests

```bash
pytest
```
