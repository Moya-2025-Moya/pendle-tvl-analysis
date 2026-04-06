"""
Wave 2 – vePENDLE lock rate and circulating supply, Oct–Dec 2025.

Goal: Confirm the "~20% lock rate" claim as a signal of weak long-term
      governance conviction before the sPENDLE transition.

Method:
  1. Call vePENDLE.totalSupply() at weekly blocks through Oct–Dec 2025.
     (vePENDLE totalSupply returns total locked PENDLE, not vote-power-weighted)
  2. Fetch PENDLE circulating supply from CoinGecko for the same dates.
  3. Compute lock rate = vePENDLE supply / PENDLE circulating supply.

Note on vePENDLE mechanics:
  vePENDLE is a non-standard vote-escrowed token. Its totalSupply() returns
  the vote-power weighted sum (decays over time). For the raw locked PENDLE
  quantity, we ideally want the sum of locked amounts, not vote power.
  However, at the aggregate level, totalSupply() is the best on-chain proxy.
  Cross-reference with the Pendle governance dashboard for vote power figures.

Output: data/vependle_lock_rate_oct_dec_2025.csv
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import (
    get_web3, blocks_for_dates, erc20_total_supply,
    coingecko_price_range, save_csv, ADDRESSES
)
import pandas as pd
from web3 import Web3

OUT = Path(__file__).parent / "data" / "vependle_lock_rate_oct_dec_2025.csv"

# Weekly snapshots covering Wave 2
DATES = [
    "2025-09-25", "2025-10-01", "2025-10-08", "2025-10-15", "2025-10-22", "2025-10-29",
    "2025-11-05", "2025-11-12", "2025-11-19", "2025-11-26",
    "2025-12-03", "2025-12-10", "2025-12-17", "2025-12-24", "2025-12-31",
]

# vePENDLE contract – standard ERC20-like totalSupply exists
# (returns vote-power-weighted total, decays linearly until lock expiry)
VEPENDLE_ADDRESS = ADDRESSES["vePENDLE"]

# vePENDLE ABI: it has totalSupply() returning the current vote power total
# This is different from total PENDLE locked, but is the on-chain proxy used
# by most analytics tools
VEPENDLE_ABI = [
    {"inputs": [], "name": "totalSupplyStored",
     "outputs": [{"type": "uint128"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply",
     "outputs": [{"type": "uint128"}], "stateMutability": "view", "type": "function"},
]


def get_vependle_supply(block: int, w3: Web3) -> float:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(VEPENDLE_ADDRESS),
        abi=VEPENDLE_ABI,
    )
    # Try totalSupplyStored first (returns raw PENDLE-weighted supply),
    # then fall back to totalSupply()
    for fn_name in ["totalSupplyStored", "totalSupply"]:
        try:
            raw = contract.functions[fn_name]().call(block_identifier=block)
            return raw / 1e18
        except Exception:
            continue
    raise RuntimeError(f"Could not read vePENDLE supply at block {block}")


def fetch_pendle_circulating_supply_coingecko() -> pd.DataFrame:
    """
    CoinGecko /coins/pendle/market_chart/range returns market_cap and
    current_price. We derive circulating supply = market_cap / price.
    Covers Oct–Dec 2025.
    """
    from datetime import datetime, timezone
    from_ts = int(datetime(2025, 9, 20, tzinfo=timezone.utc).timestamp())
    to_ts   = int(datetime(2026, 1, 5,  tzinfo=timezone.utc).timestamp())

    import requests
    url = (
        f"https://api.coingecko.com/api/v3/coins/pendle/market_chart/range"
        f"?vs_currency=usd&from={from_ts}&to={to_ts}"
    )
    resp = requests.get(url, timeout=30)
    if resp.status_code == 429:
        print("CoinGecko rate limit – sleeping 60s")
        time.sleep(60)
        resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    prices      = pd.DataFrame(raw.get("prices", []),      columns=["ts_ms", "price"])
    market_caps = pd.DataFrame(raw.get("market_caps", []), columns=["ts_ms", "market_cap"])
    df = prices.merge(market_caps, on="ts_ms")
    df["date"] = pd.to_datetime(df["ts_ms"], unit="ms").dt.date.astype(str)
    df = df.groupby("date").last().reset_index()
    df["circ_supply"] = df["market_cap"] / df["price"]
    return df[["date", "price", "market_cap", "circ_supply"]]


def main():
    print("=== vePENDLE lock rate: Sep–Dec 2025 ===\n")

    w3 = get_web3()

    # Get blocks
    print("Finding blocks…")
    date_blocks = blocks_for_dates(DATES, w3)

    # Get vePENDLE totalSupply at each block
    vependle_rows = []
    for date, block in date_blocks.items():
        try:
            supply = get_vependle_supply(block, w3)
            print(f"  {date} (block {block:,}): vePENDLE supply = {supply:,.0f}")
            vependle_rows.append({"date": date, "block": block, "vePENDLE_supply": round(supply, 2)})
        except Exception as e:
            print(f"  {date}: ERROR – {e}")
            vependle_rows.append({"date": date, "block": block, "error": str(e)})

    ve_df = pd.DataFrame(vependle_rows)

    # Get PENDLE circulating supply from CoinGecko
    print("\nFetching PENDLE circulating supply from CoinGecko…")
    try:
        cg_df = fetch_pendle_circulating_supply_coingecko()
        print(f"  Got {len(cg_df)} rows from CoinGecko")
    except Exception as e:
        print(f"  CoinGecko failed: {e}")
        cg_df = pd.DataFrame(columns=["date", "circ_supply"])

    # Merge
    df = ve_df.merge(cg_df[["date", "circ_supply", "price"]], on="date", how="left")

    # Compute lock rate
    if "vePENDLE_supply" in df.columns and "circ_supply" in df.columns:
        df["lock_rate_%"] = (df["vePENDLE_supply"] / df["circ_supply"] * 100).round(2)

    save_csv(df, OUT, label="vePENDLE lock rate")

    # Summary
    if "lock_rate_%" in df.columns:
        print("\n=== vePENDLE lock rate (weekly) ===")
        print(df[["date", "vePENDLE_supply", "circ_supply", "lock_rate_%"]].dropna().to_string(index=False))

        avg_lock = df["lock_rate_%"].dropna().mean()
        print(f"\nAverage lock rate over period: {avg_lock:.1f}%")
        print("Claim: ~20%  →  " + ("SUPPORTED" if 15 < avg_lock < 25 else "NEEDS REVIEW"))


if __name__ == "__main__":
    main()
