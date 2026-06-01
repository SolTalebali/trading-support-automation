"""Generate synthetic daily batch files for development and testing.

Produces trades_{date}.csv, positions_{date}.csv, and pnl_{date}.csv for both
today (20260512) and yesterday (20260511). Yesterday's files are clean and serve
as the reconciliation baseline. Today's files have deliberate issues injected
so the validator and reconciliation modules have something to catch.

Injected issues:
  trades:    3x missing trade_id, 2x duplicate trade_id, 2x bad numeric in price,
             2x missing ticker, 2x negative quantity
  positions: 1x missing market_value, 1x negative quantity
  pnl:       2x total_pnl != realized_pnl + unrealized_pnl

Run from the project root:
    python scripts/generate_sample_data.py
"""

from __future__ import annotations

import os
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
TODAY = "20260512"
YESTERDAY = "20260511"
TICKERS = ["AAPL", "MSFT", "BARC", "HSBC", "BP", "VOD"]
N_TRADES = 50

BASE_PRICES = {
    "AAPL": 210.0,
    "MSFT": 420.0,
    "BARC": 2.10,
    "HSBC": 7.40,
    "BP": 5.20,
    "VOD": 0.75,
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def build_trades(date: str, n: int, seed_offset: int = 0) -> pd.DataFrame:
    """Build a clean trades DataFrame with n rows."""
    rng = np.random.default_rng(SEED + seed_offset)
    rand = random.Random(SEED + seed_offset)
    rows = []
    for i in range(1, n + 1):
        ticker = rand.choice(TICKERS)
        side = rand.choice(["BUY", "SELL"])
        price = round(BASE_PRICES[ticker] * (1 + rng.normal(0, 0.01)), 4)
        quantity = int(rng.integers(100, 10_000))
        notional = round(price * quantity, 2)
        hour = rand.randint(18, 23)
        minute = rand.randint(0, 59)
        second = rand.randint(0, 59)
        rows.append({
            "trade_id": f"T{i:04d}",
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "price": price,
            "notional": notional,
            "timestamp": f"{date[:4]}-{date[4:6]}-{date[6:]} {hour:02d}:{minute:02d}:{second:02d}",
        })
    return pd.DataFrame(rows)


def build_positions(seed_offset: int = 0) -> pd.DataFrame:
    """Build a clean positions DataFrame (one row per ticker)."""
    rng = np.random.default_rng(SEED + seed_offset + 100)
    rows = []
    for ticker in TICKERS:
        avg_price = round(BASE_PRICES[ticker] * (1 + rng.normal(0, 0.02)), 4)
        quantity = int(rng.integers(1_000, 50_000))
        market_value = round(avg_price * quantity, 2)
        rows.append({
            "ticker": ticker,
            "quantity": quantity,
            "avg_price": avg_price,
            "market_value": market_value,
        })
    return pd.DataFrame(rows)


def build_pnl(seed_offset: int = 0) -> pd.DataFrame:
    """Build a clean P&L DataFrame (one row per ticker)."""
    rng = np.random.default_rng(SEED + seed_offset + 200)
    rows = []
    for ticker in TICKERS:
        realized = round(rng.uniform(-50_000, 100_000), 2)
        unrealized = round(rng.uniform(-30_000, 80_000), 2)
        rows.append({
            "ticker": ticker,
            "realized_pnl": realized,
            "unrealized_pnl": unrealized,
            "total_pnl": round(realized + unrealized, 2),
        })
    return pd.DataFrame(rows)


def inject_trade_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Inject known issues into the trades DataFrame."""
    rng = random.Random(SEED)
    df = df.copy()
    indices = list(range(len(df)))

    for i in rng.sample(indices, 3):
        df.at[i, "trade_id"] = None

    dup_targets = rng.sample(indices, 2)
    for i in dup_targets:
        df.at[i, "trade_id"] = "T9999"

    df["price"] = df["price"].astype(object)
    for i in rng.sample(indices, 2):
        df.at[i, "price"] = "N/A"

    for i in rng.sample(indices, 2):
        df.at[i, "ticker"] = None

    for i in rng.sample(indices, 2):
        df.at[i, "quantity"] = -abs(int(df.at[i, "quantity"]))

    return df


def inject_position_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Inject known issues into the positions DataFrame."""
    rng = random.Random(SEED + 1)
    df = df.copy()

    for i in rng.sample(list(range(len(df))), 1):
        df.at[i, "market_value"] = None

    for i in rng.sample(list(range(len(df))), 1):
        df.at[i, "quantity"] = -abs(int(df.at[i, "quantity"]))

    return df


def inject_pnl_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Inject known issues into the P&L DataFrame."""
    rng = random.Random(SEED + 2)
    df = df.copy()

    for i in rng.sample(list(range(len(df))), 2):
        df.at[i, "total_pnl"] = round(df.at[i, "total_pnl"] + 9_999.99, 2)

    return df


def write_csv(df: pd.DataFrame, stem: str, date: str, arrival_time: str = "07:30") -> None:
    path = OUTPUT_DIR / f"{stem}_{date}.csv"
    df.to_csv(path, index=False)
    timestamp = datetime.strptime(f"{date} {arrival_time}", "%Y%m%d %H:%M").timestamp()
    os.utime(path, (timestamp, timestamp))
    print(f"Wrote {len(df)} rows to {path} (arrival {arrival_time})")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Yesterday — clean baseline for reconciliation (all on time)
    write_csv(build_trades(YESTERDAY, N_TRADES, seed_offset=10), "trades", YESTERDAY, "07:15")
    write_csv(build_positions(seed_offset=10), "positions", YESTERDAY, "07:20")
    write_csv(build_pnl(seed_offset=10), "pnl", YESTERDAY, "07:25")

    # Today — issues injected; positions deliberately late to exercise the cut-off check
    write_csv(inject_trade_issues(build_trades(TODAY, N_TRADES)), "trades", TODAY, "07:30")
    write_csv(inject_position_issues(build_positions()), "positions", TODAY, "08:30")
    write_csv(inject_pnl_issues(build_pnl()), "pnl", TODAY, "07:55")


if __name__ == "__main__":
    main()
