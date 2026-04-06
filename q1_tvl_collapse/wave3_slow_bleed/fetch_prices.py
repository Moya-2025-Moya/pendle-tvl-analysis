"""
Wave 3 – Asset price history: BTC, ETH, PENDLE (Jan–Apr 2026).

Goal:
  1. Pin BTC/ETH entry prices on Jan 1, 2026.
  2. Document the market beta drawdown (~37% BTC, ~31% ETH) from the analysis.
  3. Provide PENDLE price history for the token section (Q2 Metric 5).

Method: CoinGecko free API (no key needed, 30 req/min limit).

Output: data/prices_jan_apr_2026.csv
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import save_csv
import pandas as pd
import requests
from datetime import datetime, timezone

OUT = Path(__file__).parent / "data" / "prices_jan_apr_2026.csv"

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "pendle": "PENDLE",
}

# Wave 3 window + some context from before
FROM_DATE = datetime(2025, 11, 1, tzinfo=timezone.utc)
TO_DATE   = datetime(2026, 4,  6, tzinfo=timezone.utc)


def fetch_coin_history(coin_id: str, from_ts: int, to_ts: int,
                        vs: str = "usd") -> pd.DataFrame:
    url = (
        f"{COINGECKO_BASE}/coins/{coin_id}/market_chart/range"
        f"?vs_currency={vs}&from={from_ts}&to={to_ts}"
    )
    for attempt in range(3):
        resp = requests.get(url, timeout=30)
        if resp.status_code == 429:
            wait = 65 * (attempt + 1)
            print(f"    Rate limited, sleeping {wait}s…")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break

    raw    = resp.json()
    prices = pd.DataFrame(raw.get("prices", []), columns=["ts_ms", "price_usd"])
    prices["date"] = pd.to_datetime(prices["ts_ms"], unit="ms").dt.date.astype(str)
    # One row per day (last price of the day)
    prices = prices.groupby("date")["price_usd"].last().reset_index()
    prices["coin"] = coin_id
    return prices


def main():
    print("=== Price history: BTC / ETH / PENDLE (Nov 2025 – Apr 2026) ===\n")

    from_ts = int(FROM_DATE.timestamp())
    to_ts   = int(TO_DATE.timestamp())

    all_dfs = []
    for coin_id, ticker in COINS.items():
        print(f"  Fetching {ticker} ({coin_id})…")
        try:
            df = fetch_coin_history(coin_id, from_ts, to_ts)
            all_dfs.append(df)
            print(f"    {len(df)} daily rows")
        except Exception as e:
            print(f"    ERROR: {e}")
        time.sleep(2)  # avoid rate limit between coins

    if not all_dfs:
        print("No data retrieved.")
        return

    # Pivot to wide format: date | BTC | ETH | PENDLE
    combined = pd.concat(all_dfs)
    wide = combined.pivot(index="date", columns="coin", values="price_usd").reset_index()
    wide.columns.name = None
    wide = wide.rename(columns={c: COINS.get(c, c) for c in wide.columns})

    save_csv(wide, OUT, label="Price history")

    # Key claims validation
    print("\n=== Key price claims ===")
    if "BTC" in wide.columns:
        jan1 = wide[wide["date"] == "2026-01-01"]
        apr4 = wide[wide["date"] == "2026-04-04"]
        if not jan1.empty and not apr4.empty:
            btc_jan = jan1["BTC"].values[0]
            btc_apr = apr4["BTC"].values[0]
            pct = (btc_apr - btc_jan) / btc_jan * 100
            print(f"  BTC Jan 1: ${btc_jan:,.0f}  →  Apr 4: ${btc_apr:,.0f}  ({pct:+.1f}%)")
            print("  Claim: ~-37%  →  " + ("SUPPORTED" if pct < -30 else "NEEDS REVIEW"))

    if "ETH" in wide.columns:
        eth_jan29 = wide[wide["date"] == "2026-01-29"]
        eth_apr4  = wide[wide["date"] == "2026-04-04"]
        if not eth_jan29.empty and not eth_apr4.empty:
            eth1 = eth_jan29["ETH"].values[0]
            eth2 = eth_apr4["ETH"].values[0]
            pct  = (eth2 - eth1) / eth1 * 100
            print(f"  ETH Jan 29: ${eth1:,.0f}  →  Apr 4: ${eth2:,.0f}  ({pct:+.1f}%)")
            print("  Claim: ~-31%  →  " + ("SUPPORTED" if pct < -25 else "NEEDS REVIEW"))

    if "PENDLE" in wide.columns:
        p_aug = wide[wide["date"] == "2025-11-01"]
        p_mar = wide[wide["date"] == "2026-03-01"]
        if not p_aug.empty and not p_mar.empty:
            p1 = p_aug["PENDLE"].values[0]
            p2 = p_mar["PENDLE"].values[0]
            pct = (p2 - p1) / p1 * 100
            print(f"  PENDLE Nov 1: ${p1:.3f}  →  Mar 1: ${p2:.3f}  ({pct:+.1f}%)")

    print("\nFull data saved to:", OUT)


if __name__ == "__main__":
    main()
