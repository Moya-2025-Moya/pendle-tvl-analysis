"""
Q3 – MakerDAO/Sky RWA diversification case study (2022–2025).

Goal: Quantify the claim that MakerDAO systematically onboarded RWA
      (>50% of DAI backing by 2024) and stabilized revenue and DAI supply
      during the 2022 bear market and Q4 2025 downturn.

Data sources (all free, no API key):
  1. DefiLlama /protocol/makerdao and /protocol/sky  — TVL history
  2. DefiLlama Yields                                — sDAI/DSR yield pools
  3. RWA-adjacent protocols (Ondo, Centrifuge, Maple) — ecosystem context
  4. makerburn.com API                               — collateral breakdown (if up)

Output: data/makerdao_sky_tvl.csv, data/rwa_protocols_tvl.csv
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from shared.utils import save_csv, get_protocol_tvl, get_all_pendle_pools
import pandas as pd
import requests

OUT_DIR = Path(__file__).parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"Accept-Encoding": "gzip, deflate"}


def fetch_maker_collateral() -> pd.DataFrame:
    """Fetch current MakerDAO collateral composition from makerburn.com."""
    try:
        resp = requests.get("https://api.makerburn.com/collateral", timeout=20, headers=HEADERS)
        resp.raise_for_status()
        return pd.DataFrame(resp.json())
    except Exception as e:
        print(f"  makerburn.com: {e}")
        return pd.DataFrame()


def fetch_maker_yield_pools() -> pd.DataFrame:
    """Find MakerDAO/Sky-related yield pools from DefiLlama Yields."""
    try:
        resp = requests.get("https://yields.llama.fi/pools", timeout=60, headers=HEADERS)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json()["data"])
        mask = df["project"].str.contains("maker|sky|spark|sdai", case=False, na=False)
        return df[mask].copy()
    except Exception as e:
        print(f"  DefiLlama Yields: {e}")
        return pd.DataFrame()


def main():
    print("=== MakerDAO RWA diversification case study ===\n")

    # 1. MakerDAO / Sky TVL history
    print("Fetching MakerDAO / Sky TVL history…")
    dfs = []
    for slug in ["makerdao", "sky"]:
        try:
            df = get_protocol_tvl(slug)
            latest = df["totalLiquidityUSD"].iloc[-1]
            print(f"  {slug}: {len(df)} rows  (latest: ${latest/1e9:.2f}B)")
            dfs.append(df)
            time.sleep(0.5)
        except Exception as e:
            print(f"  {slug}: {e}")

    if dfs:
        maker_tvl = pd.concat(dfs).sort_values("date")
        save_csv(maker_tvl, OUT_DIR / "makerdao_sky_tvl.csv", "MakerDAO+Sky TVL")

        milestones = {
            "2022-01-01": "Bear market start",
            "2022-06-15": "ETH collateral stress (3AC/Celsius)",
            "2022-11-01": "FTX collapse",
            "2023-06-01": "RWA expansion underway",
            "2024-01-01": "RWA >50% DAI backing claim",
            "2025-01-01": "2025 start",
            "2025-10-01": "Q4 2025 downturn reference",
        }
        print("\n=== MakerDAO/Sky TVL at key dates ===")
        for date, label in milestones.items():
            row = maker_tvl[maker_tvl["date"] <= date].tail(1)
            if not row.empty:
                tvl = row["totalLiquidityUSD"].values[0]
                print(f"  {date} ({label}): ${tvl/1e9:.2f}B")

    # 2. Collateral breakdown
    print("\nFetching MakerDAO collateral composition…")
    collateral = fetch_maker_collateral()
    if not collateral.empty:
        print(f"  {len(collateral)} collateral types:")
        print(collateral.head(10).to_string(index=False))
        save_csv(collateral, OUT_DIR / "makerdao_collateral.csv", "Collateral breakdown")

    # 3. RWA protocols for context
    print("\nFetching RWA protocol TVL…")
    rwa_slugs = ["ondo-finance", "centrifuge", "maple", "goldfinch"]
    rwa_dfs = []
    for slug in rwa_slugs:
        try:
            df = get_protocol_tvl(slug)
            rwa_dfs.append(df)
            print(f"  {slug}: {len(df)} rows, latest ${df['totalLiquidityUSD'].iloc[-1]/1e6:.0f}M")
            time.sleep(0.3)
        except Exception as e:
            print(f"  {slug}: {e}")

    if rwa_dfs:
        rwa_df = pd.concat(rwa_dfs, ignore_index=True)
        save_csv(rwa_df, OUT_DIR / "rwa_protocols_tvl.csv", "RWA protocol TVL")

    # 4. MakerDAO yield pools (sDAI, DSR)
    print("\nFetching MakerDAO-related yield pools from DefiLlama Yields…")
    maker_pools = fetch_maker_yield_pools()
    if not maker_pools.empty:
        print(f"  Found {len(maker_pools)} pools:")
        print(maker_pools[["pool", "symbol", "project", "apy", "tvlUsd"]].head(10).to_string(index=False))
        save_csv(maker_pools, OUT_DIR / "makerdao_yield_pools.csv", "MakerDAO yield pools")

    print("\n=== Supporting data points for case study ===")
    print("  Key URLs to cross-reference (manual):")
    print("  → makerburn.com/#/collateral  (live RWA % of backing)")
    print("  → daistats.com                (DAI supply history)")
    print("  → gov.makerdao.com            (Monetalis, BlockTower proposal dates)")


if __name__ == "__main__":
    main()
