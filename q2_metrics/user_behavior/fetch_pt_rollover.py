"""
Q2 Metric – PT rollover rate: Sep & Dec 2025 maturities.

Goal: Of all PT positions that expired in Sep 2025 (and Dec 2025),
      what % of capital opened a new PT position vs. redeemed and left?
      High rollover = users believe yields will recover.
      Low rollover  = users treating each expiry as an exit point.

Method:
  Use DefiLlama Yields to track TVL flows:
  - Find all Pendle pools that expired ~Sep 25, 2025
  - Measure TVL in those pools 7 days before expiry
  - Measure TVL in NEW pools (next maturity, same underlying) 7 days after
  - Rollover rate ≈ (TVL in new pools) / (TVL in expired pools)

  This is an approximation; the exact figure requires on-chain event
  analysis (see dune_pt_rollover.sql for precise version).

Output: data/pt_rollover_rate.csv
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import (
    get_all_pendle_pools, get_pool_yield_history, save_csv
)
import pandas as pd
import requests

OUT = Path(__file__).parent / "data" / "pt_rollover_rate.csv"

# Expiry dates to analyze
TARGET_EXPIRIES = {
    "sep2025": "2025-09-25",
    "dec2025": "2025-12-26",  # approximate next quarterly expiry
}

# Window for TVL comparison
PRE_DAYS  = 7  # days before expiry to measure "exiting" TVL
POST_DAYS = 14 # days after expiry to measure "rolled" TVL


def main():
    print("=== PT rollover rate analysis ===\n")

    print("Fetching all Pendle pools from DefiLlama Yields…")
    pools = get_all_pendle_pools()
    print(f"  Total Pendle pools: {len(pools)}")

    if pools.empty:
        print("No pools found.")
        return

    # Print available columns for inspection
    print(f"  Columns: {list(pools.columns)}\n")

    # Show pools sorted by TVL
    tvl_col = "tvlUsd" if "tvlUsd" in pools.columns else "tvl"
    if tvl_col in pools.columns:
        top = pools.nlargest(20, tvl_col)[["pool", "symbol", "chain", tvl_col, "apy"]]
        print("Top 20 Pendle pools by TVL:")
        print(top.to_string(index=False))

    # Identify "expired" vs "active" pools by TVL pattern
    # Pools with TVL = 0 or near-zero are likely expired
    if tvl_col in pools.columns:
        active  = pools[pools[tvl_col] > 100_000].copy()
        expired = pools[pools[tvl_col] < 100_000].copy()
        print(f"\nActive pools (TVL > $100K): {len(active)}")
        print(f"Likely expired (TVL < $100K): {len(expired)}")

    # For each target expiry, try to find matching pools
    results = []
    for label, expiry_date in TARGET_EXPIRIES.items():
        print(f"\n--- Analyzing {label} expiry ({expiry_date}) ---")

        # Filter pools whose name contains the expiry date or year-month
        expiry_short = expiry_date[:7]  # "2025-09"
        matching = pools[
            pools["symbol"].str.contains(expiry_short.replace("-", ""), case=False, na=False) |
            pools["symbol"].str.contains(expiry_date, case=False, na=False)
        ]

        if matching.empty:
            print(f"  No pools found matching {expiry_date} in symbol name.")
            print("  → Use the Dune SQL query for precise rollover analysis.")
            results.append({
                "expiry": label,
                "expiry_date": expiry_date,
                "note": "No matching pools found in DefiLlama — use Dune SQL"
            })
            continue

        for _, pool_row in matching.iterrows():
            pool_id = pool_row["pool"]
            symbol  = pool_row.get("symbol", "")
            try:
                hist = get_pool_yield_history(pool_id)
                # TVL 7 days before expiry
                pre_window  = hist[hist["timestamp"] <= expiry_date].tail(PRE_DAYS)
                post_window = hist[hist["timestamp"] >  expiry_date].head(POST_DAYS)

                pre_tvl  = pre_window["tvlUsd"].mean()  if "tvlUsd" in pre_window.columns else None
                post_tvl = post_window["tvlUsd"].mean() if "tvlUsd" in post_window.columns else None

                results.append({
                    "expiry":     label,
                    "pool_id":    pool_id,
                    "symbol":     symbol,
                    "pre_tvl_avg":  round(pre_tvl,  0) if pre_tvl  else None,
                    "post_tvl_avg": round(post_tvl, 0) if post_tvl else None,
                })
                print(f"  {symbol}: pre-expiry TVL avg = {pre_tvl:,.0f}, post = {post_tvl:,.0f}")
            except Exception as e:
                print(f"  {symbol}: ERROR – {e}")
            time.sleep(0.5)

    df = pd.DataFrame(results)
    save_csv(df, OUT, label="PT rollover rate")


if __name__ == "__main__":
    main()
