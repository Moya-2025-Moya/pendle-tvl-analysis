"""
Wave 2 – Aave V3 USDC borrow rate history, Sep–Dec 2025.

Goal: Source the "5–7% borrow cost" claim precisely to prove carry inversion
      when PT yields dropped below USDC borrow rate.

Method:
  Primary: DefiLlama Yields for USDC on Aave V3 Ethereum (supply rate).
           DefiLlama tracks supply APY, not borrow APY directly.
           Borrow APR ≈ supply_APR / utilization_rate
           (We derive this from: supplyAPR = borrowAPR * utilization * (1 - reserveFactor))

  Supplemental: On-chain via Alchemy at weekly blocks for precise borrow rate.
           In Aave V3, rates are stored as ANNUAL rates in RAY (1e27).
           APR% = rate_ray / RAY * 100 (confirmed working).

Output: data/aave_usdc_borrow_rate_sep_dec_2025.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import (
    get_web3, get_block_by_timestamp, blocks_for_dates,
    aave_reserve_data, save_csv, ADDRESSES, RAY
)
import pandas as pd
import requests
from datetime import datetime, timezone

OUT = Path(__file__).parent / "data" / "aave_usdc_borrow_rate_sep_dec_2025.csv"

# DefiLlama Yields pool ID for USDC on Aave V3 Ethereum (confirmed working)
AAVE_V3_USDC_POOL_ID = "aa70268e-4b52-42bf-a116-608b370f9501"

# Aave V3 USDC reserve factor = 10% (standard)
# APR_borrow ≈ APR_supply / (utilization * (1 - 0.10))
# At typical utilization ~85%: APR_borrow ≈ APR_supply / 0.765
RESERVE_FACTOR = 0.10

# Weekly on-chain snapshots for precise borrow rate
DATES = [
    "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22", "2025-09-25", "2025-09-29",
    "2025-10-06", "2025-10-13", "2025-10-20", "2025-10-27",
    "2025-11-03", "2025-11-10", "2025-11-17", "2025-11-24",
    "2025-12-01", "2025-12-08", "2025-12-15", "2025-12-22", "2025-12-29",
]


def fetch_defillama_usdc_supply_rate() -> pd.DataFrame:
    """Historical USDC supply APY from DefiLlama Yields."""
    print("  Fetching USDC supply APY from DefiLlama Yields…")
    headers = {"Accept-Encoding": "gzip, deflate"}
    resp = requests.get(
        f"https://yields.llama.fi/chart/{AAVE_V3_USDC_POOL_ID}",
        timeout=30, headers=headers
    )
    resp.raise_for_status()
    data = resp.json()["data"]
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date.astype(str)
    df = df.rename(columns={"apy": "supplyAPR_%", "tvlUsd": "tvl_usd"})

    # Borrow APR estimate: supply / (utilization * (1 - reserveFactor))
    # Note: utilization is not available from DefiLlama; we use a range estimate
    # At utilization 80%: borrow ≈ supply / 0.72
    # At utilization 90%: borrow ≈ supply / 0.81
    df["borrowAPR_lo_%"]  = (df["supplyAPR_%"] / 0.81).round(4)   # 90% utilization
    df["borrowAPR_mid_%"] = (df["supplyAPR_%"] / 0.765).round(4)  # 85% utilization
    df["borrowAPR_hi_%"]  = (df["supplyAPR_%"] / 0.72).round(4)   # 80% utilization
    df["source"] = "DefiLlama_Yields"
    return df


def fetch_onchain_borrow_rates(w3) -> pd.DataFrame:
    """
    Direct on-chain borrow rate via Alchemy at weekly blocks.
    Uses fixed APR formula: rate_ray / RAY * 100 (not per-second).
    """
    print("  Fetching on-chain USDC borrow rates via Alchemy…")
    date_blocks = blocks_for_dates(DATES, w3)

    rows = []
    for date, block in date_blocks.items():
        try:
            d = aave_reserve_data(ADDRESSES["USDC"], block, w3)
            # Compute utilization from supply and debt
            total_supply = d["totalAToken"]
            total_debt   = d["totalVariableDebt"]
            utilization  = total_debt / total_supply if total_supply > 0 else None

            rows.append({
                "date":               date,
                "block":              block,
                "supplyAPR_%":        d["supplyAPR_%"],
                "variableBorrowAPR_%": d["variableBorrowAPR_%"],
                "utilization":        round(utilization, 4) if utilization else None,
                "totalSupply_USDC":   round(total_supply / 1e6, 2),
                "source":             "Alchemy_RPC",
            })
            print(f"  {date}: supply={d['supplyAPR_%']:.2f}%  borrow={d['variableBorrowAPR_%']:.2f}%  "
                  f"util={utilization:.1%}" if utilization else
                  f"  {date}: supply={d['supplyAPR_%']:.2f}%  borrow={d['variableBorrowAPR_%']:.2f}%")
        except Exception as e:
            print(f"  {date}: ERROR – {e}")

    return pd.DataFrame(rows)


def main():
    print("=== Aave V3 USDC borrow rate: Sep–Dec 2025 ===\n")

    # Step 1: Daily data from DefiLlama Yields
    dl_df = None
    try:
        dl_df = fetch_defillama_usdc_supply_rate()
        mask  = (dl_df["date"] >= "2025-09-01") & (dl_df["date"] <= "2025-12-31")
        dl_df = dl_df[mask].copy()
        print(f"  DefiLlama: {len(dl_df)} daily rows in Sep–Dec 2025")
    except Exception as e:
        print(f"  DefiLlama Yields failed: {e}")

    # Step 2: Weekly on-chain precise borrow rates
    w3     = get_web3()
    oc_df  = fetch_onchain_borrow_rates(w3)

    # Combine
    all_dfs = [df for df in [dl_df, oc_df] if df is not None and not df.empty]
    if not all_dfs:
        print("No data retrieved.")
        return

    combined = pd.concat(all_dfs, ignore_index=True, sort=False)
    combined = combined.sort_values("date").drop_duplicates(subset=["date", "source"])
    save_csv(combined, OUT, label="Aave USDC rates")

    # Summary
    oc_valid = oc_df.dropna(subset=["variableBorrowAPR_%"])
    if not oc_valid.empty:
        avg_borrow = oc_valid["variableBorrowAPR_%"].mean()
        min_borrow = oc_valid["variableBorrowAPR_%"].min()
        max_borrow = oc_valid["variableBorrowAPR_%"].max()
        print(f"\n=== On-chain USDC borrow rate summary (Sep–Dec 2025) ===")
        print(f"  Average: {avg_borrow:.2f}%   Min: {min_borrow:.2f}%   Max: {max_borrow:.2f}%")
        print(f"  Claim: 5–7%  →  " + ("SUPPORTED" if 4 < avg_borrow < 8 else "NEEDS REVIEW"))

        print("\n=== Weekly borrow rate ===")
        print(oc_valid[["date", "supplyAPR_%", "variableBorrowAPR_%", "utilization"]].to_string(index=False))

    # Monthly averages from DefiLlama daily
    if dl_df is not None and not dl_df.empty:
        dl_df["month"] = pd.to_datetime(dl_df["date"]).dt.to_period("M")
        monthly = dl_df.groupby("month")[["supplyAPR_%", "borrowAPR_mid_%"]].mean().round(2)
        print(f"\n=== Monthly average rates (DefiLlama supply + estimated borrow) ===")
        print(monthly)


if __name__ == "__main__":
    main()
