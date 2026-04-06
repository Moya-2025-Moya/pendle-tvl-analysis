"""
Wave 1 – Ethena: sUSDe total supply at Sep-25 peak.

Goal: Quantify what fraction of sUSDe supply was inside the Pendle
      Ethena-Aave loop at peak.

Method:
  Call sUSDe.totalSupply() at a series of blocks spanning Aug–Oct 2025.
  Compare with the Aave PT-sUSDe collateral figure from fetch_aave_pt_susde.py
  to estimate what % of sUSDe supply was captured by the loop.

Output: data/susde_supply_aug_oct_2025.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import get_web3, blocks_for_dates, erc20_total_supply, save_csv, ADDRESSES
import pandas as pd

OUT = Path(__file__).parent / "data" / "susde_supply_aug_oct_2025.csv"

# Weekly snapshots covering the build-up and collapse around Sep 25
DATES = [
    "2025-08-01", "2025-08-15",
    "2025-09-01", "2025-09-10", "2025-09-15",
    "2025-09-22", "2025-09-24", "2025-09-25", "2025-09-26",
    "2025-09-30", "2025-10-07", "2025-10-15",
]


def main():
    print("=== sUSDe total supply: Aug–Oct 2025 ===\n")

    w3 = get_web3()

    print("Finding blocks…")
    date_blocks = blocks_for_dates(DATES, w3)

    rows = []
    for date, block in date_blocks.items():
        try:
            supply = erc20_total_supply(ADDRESSES["sUSDe"], block, w3, decimals=18)
            print(f"  {date} (block {block:,}): sUSDe supply = {supply:,.2f}")
            rows.append({"date": date, "block": block, "sUSDe_supply": round(supply, 2)})
        except Exception as e:
            print(f"  {date}: ERROR – {e}")
            rows.append({"date": date, "block": block, "error": str(e)})

    df = pd.DataFrame(rows)
    save_csv(df, OUT, label="sUSDe total supply")

    # Show peak and post-expiry drop
    valid = df.dropna(subset=["sUSDe_supply"])
    if not valid.empty:
        peak_idx = valid["sUSDe_supply"].idxmax()
        print(f"\nPeak supply: {valid.loc[peak_idx, 'sUSDe_supply']:,.0f} on {valid.loc[peak_idx, 'date']}")
        sep25 = valid[valid["date"] == "2025-09-25"]
        if not sep25.empty:
            print(f"Sep-25 supply: {sep25['sUSDe_supply'].values[0]:,.0f}")


if __name__ == "__main__":
    main()
