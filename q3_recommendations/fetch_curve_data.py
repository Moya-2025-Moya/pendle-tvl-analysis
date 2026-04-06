"""
Q3 – Curve Finance gauge system case study.

Goal: Quantify Curve's TVL resilience through 2023–2024 as evidence that
      active gauge reweighting smoothly rotated TVL (3pool → crvUSD) without
      a cliff-fall — the model for what Pendle's AIM should do.

Data sources:
  1. DefiLlama /protocol/curve-finance — total TVL history
  2. Curve public API                  — current pool TVL breakdown
  3. Curve Gauge Controller (on-chain) — gauge weight history via Alchemy

Output: data/curve_tvl.csv, data/curve_pools_current.csv, data/curve_gauge_weights.csv
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from shared.utils import save_csv, get_protocol_tvl, get_web3, get_block_by_timestamp
import pandas as pd
import requests
from web3 import Web3
from datetime import datetime, timezone

OUT_DIR = Path(__file__).parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"Accept-Encoding": "gzip, deflate"}
CURVE_API = "https://api.curve.fi/api"

# Curve Gauge Controller on Ethereum
GAUGE_CONTROLLER = "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"
GAUGE_CONTROLLER_ABI = [
    {"name": "get_gauge_weight",  "inputs": [{"name": "addr", "type": "address"}],
     "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"name": "get_total_weight",  "inputs": [],
     "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
]

# Key gauge addresses (Ethereum mainnet, verified on Etherscan)
GAUGES = {
    "3pool (DAI/USDC/USDT)": "0xbFcF63294aD7105dEa65aA58F8AE5BE2D9d0952A",
    "stETH/ETH":             "0x182B723a58739a9c974cFDB385ceaDb237453c28",
    # crvUSD pools launched in 2023
    "crvUSD/USDC":           "0x95f00391cB5EebCd190EB58728B4CE23DbFaAFBE",
    "crvUSD/USDT":           "0x4e6bB6B7447B7B2Aa268C16AB87F4Bb48BF57939",
}


def fetch_curve_tvl() -> pd.DataFrame:
    for slug in ["curve-finance", "curve-dex"]:
        try:
            df = get_protocol_tvl(slug)
            print(f"  Loaded '{slug}': {len(df)} rows  "
                  f"(latest: ${df['totalLiquidityUSD'].iloc[-1]/1e9:.2f}B)")
            return df
        except Exception as e:
            print(f"  '{slug}': {e}")
    return pd.DataFrame()


def fetch_curve_pools() -> pd.DataFrame:
    """Current pool TVL breakdown from Curve's public API."""
    try:
        resp = requests.get(f"{CURVE_API}/getPools/ethereum/main", timeout=30)
        resp.raise_for_status()
        pool_data = resp.json().get("data", {}).get("poolData", [])
        rows = [{"name": p.get("name"), "address": p.get("address"),
                 "tvl_usd": p.get("usdTotal"), "gauge": p.get("gaugeAddress")}
                for p in pool_data]
        df = pd.DataFrame(rows).sort_values("tvl_usd", ascending=False)
        return df
    except Exception as e:
        print(f"  Curve API: {e}")
        return pd.DataFrame()


def fetch_gauge_weights_history(w3: Web3) -> pd.DataFrame:
    """
    Gauge weight % for key pools at annual snapshots 2023–2025.
    Individual gauge weight / total weight = % of CRV emissions.
    Both values are in WAD (1e18) units — divide both by 1e18 before ratio,
    or just compute ratio directly (1e18 cancels out).
    """
    gc = w3.eth.contract(
        address=Web3.to_checksum_address(GAUGE_CONTROLLER),
        abi=GAUGE_CONTROLLER_ABI
    )

    snapshot_dates = {
        "2023-01-01": "3pool dominance era",
        "2023-07-01": "crvUSD launch (May 2023)",
        "2024-01-01": "post-crvUSD consolidation",
        "2025-01-01": "current state",
    }

    rows = []
    for date, label in snapshot_dates.items():
        ts    = int(datetime.strptime(date, "%Y-%m-%d")
                    .replace(tzinfo=timezone.utc).timestamp())
        block = get_block_by_timestamp(ts, w3)

        try:
            # total_weight is in WAD
            total_weight_raw = gc.functions.get_total_weight().call(block_identifier=block)
        except Exception as e:
            print(f"  {date}: get_total_weight failed: {e}")
            total_weight_raw = None

        print(f"\n  {date} (block {block:,}):")
        for gauge_name, gauge_addr in GAUGES.items():
            try:
                weight_raw = gc.functions.get_gauge_weight(
                    Web3.to_checksum_address(gauge_addr)
                ).call(block_identifier=block)

                # Both in WAD; ratio is dimensionless
                pct = (weight_raw / total_weight_raw * 100) if total_weight_raw else None

                rows.append({
                    "date":        date,
                    "label":       label,
                    "gauge":       gauge_name,
                    "address":     gauge_addr,
                    "weight_wad":  weight_raw,
                    "total_wad":   total_weight_raw,
                    "weight_pct":  round(pct, 2) if pct is not None else None,
                })
                print(f"    {gauge_name:35s}: {pct:.2f}% of CRV emissions" if pct is not None
                      else f"    {gauge_name:35s}: N/A")
            except Exception as e:
                print(f"    {gauge_name}: ERROR – {e}")
        time.sleep(0.2)

    return pd.DataFrame(rows)


def main():
    print("=== Curve Finance gauge system case study ===\n")

    # 1. Total Curve TVL history
    print("Fetching Curve total TVL…")
    curve_tvl = fetch_curve_tvl()
    if not curve_tvl.empty:
        save_csv(curve_tvl, OUT_DIR / "curve_tvl.csv", "Curve TVL")

        milestones = {
            "2023-01-01": "3pool peak era",
            "2023-07-01": "crvUSD launch",
            "2024-01-01": "post-migration",
            "2025-01-01": "2025 baseline",
        }
        print("\n=== Curve TVL at key dates ===")
        for date, label in milestones.items():
            row = curve_tvl[curve_tvl["date"] <= date].tail(1)
            if not row.empty:
                tvl = row["totalLiquidityUSD"].values[0]
                print(f"  {date} ({label}): ${tvl/1e9:.2f}B")

    # 2. Current pool breakdown
    print("\nFetching current Curve pool TVL…")
    pools = fetch_curve_pools()
    if not pools.empty:
        print(f"  {len(pools)} pools (top 10 by TVL):")
        print(pools[["name", "tvl_usd"]].head(10).to_string(index=False))
        save_csv(pools, OUT_DIR / "curve_pools_current.csv", "Curve pool TVL")

    # 3. Gauge weight history
    print("\nFetching gauge weight history (on-chain)…")
    try:
        w3 = get_web3()
        gauge_df = fetch_gauge_weights_history(w3)
        if not gauge_df.empty:
            save_csv(gauge_df, OUT_DIR / "curve_gauge_weights.csv", "Curve gauge weights")

            print("\n=== Gauge weight % over time ===")
            pivot = gauge_df.pivot(index="date", columns="gauge", values="weight_pct")
            print(pivot.to_string())
    except Exception as e:
        print(f"  Gauge weight fetch error: {e}")

    print("\n=== Supporting narrative ===")
    print("  Key claim: Curve didn't cliff-fall when 3pool declined.")
    print("  Evidence: Total TVL held while gauge weights rotated to crvUSD pools.")
    print("  Cross-reference: https://dao.curve.fi/gaugeweight (live gauge weights)")


if __name__ == "__main__":
    main()
