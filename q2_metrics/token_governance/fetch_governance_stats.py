"""
Q2 Metric 5 – Token & governance: sPENDLE adoption rate vs. vePENDLE peak.

Goal:
  1. sPENDLE stakers as % of circulating supply (vs. vePENDLE's ~20% peak).
  2. PENDLE open interest from CoinGecko/CoinMarketCap proxy.
  3. PENDLE price drawdown timeline: $6.85 → $2.13 → ~$1.05.

Method:
  - sPENDLE totalSupply via Alchemy (once contract address confirmed).
  - PENDLE circulating supply via CoinGecko.
  - Price history already pulled in wave3/fetch_prices.py; load from there.

Output: data/governance_stats.csv
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import (
    get_web3, blocks_for_dates, save_csv, ADDRESSES,
    coingecko_price_range
)
import pandas as pd
import requests
from web3 import Web3
from datetime import datetime, timezone

OUT = Path(__file__).parent / "data" / "governance_stats.csv"

# Comparison dates
DATES = [
    "2025-10-01",   # vePENDLE baseline (pre-sPENDLE)
    "2026-01-20",   # sPENDLE launch
    "2026-01-29",   # vePENDLE renewals ceased
    "2026-02-02",   # AIM launch
    "2026-02-15",
    "2026-03-01",
    "2026-03-15",
    "2026-04-01",
    "2026-04-06",   # current
]

ERC20_ABI = [
    {"inputs": [], "name": "totalSupply",
     "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
]
VEPENDLE_ABI = [
    {"inputs": [], "name": "totalSupplyStored",
     "outputs": [{"type": "uint128"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply",
     "outputs": [{"type": "uint128"}], "stateMutability": "view", "type": "function"},
]


def get_supply(address: str, abi: list, block: int, w3: Web3,
               decimals: int = 18, fn_names: list = None) -> float | None:
    if not address or address == "0x":
        return None
    try:
        contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
        for fn in (fn_names or ["totalSupply"]):
            try:
                return contract.functions[fn]().call(block_identifier=block) / 10**decimals
            except Exception:
                continue
    except Exception as e:
        print(f"    Error reading {address[:8]}…: {e}")
    return None


def fetch_pendle_market_data() -> dict:
    """Pull current PENDLE market data from CoinGecko."""
    url = ("https://api.coingecko.com/api/v3/coins/pendle"
           "?localization=false&tickers=false&market_data=true"
           "&community_data=false&developer_data=false")
    resp = requests.get(url, timeout=30)
    if resp.status_code == 429:
        time.sleep(65)
        resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    md   = data.get("market_data", {})
    return {
        "current_price_usd":     md.get("current_price", {}).get("usd"),
        "market_cap_usd":        md.get("market_cap",    {}).get("usd"),
        "circulating_supply":    md.get("circulating_supply"),
        "total_supply":          md.get("total_supply"),
        "ath_usd":               md.get("ath",           {}).get("usd"),
        "ath_date":              md.get("ath_date",      {}).get("usd"),
    }


def main():
    print("=== Governance stats: vePENDLE vs sPENDLE adoption ===\n")

    w3 = get_web3()

    print("Finding blocks…")
    date_blocks = blocks_for_dates(DATES, w3)

    spendle_addr = ADDRESSES.get("sPENDLE", "0x")

    # Fetch circulating supply from CoinGecko
    from_ts = int(datetime(2025, 10, 1, tzinfo=timezone.utc).timestamp())
    to_ts   = int(datetime(2026, 4, 7, tzinfo=timezone.utc).timestamp())
    print("\nFetching PENDLE price/market cap from CoinGecko…")
    try:
        url = (
            f"https://api.coingecko.com/api/v3/coins/pendle/market_chart/range"
            f"?vs_currency=usd&from={from_ts}&to={to_ts}"
        )
        resp = requests.get(url, timeout=30)
        if resp.status_code == 429:
            time.sleep(65)
            resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        raw = resp.json()
        prices      = pd.DataFrame(raw.get("prices", []), columns=["ts_ms", "price"])
        market_caps = pd.DataFrame(raw.get("market_caps", []), columns=["ts_ms", "mktcap"])
        cg = prices.merge(market_caps, on="ts_ms")
        cg["date"] = pd.to_datetime(cg["ts_ms"], unit="ms").dt.date.astype(str)
        cg = cg.groupby("date").last().reset_index()
        cg["circ_supply"] = cg["mktcap"] / cg["price"]
        print(f"  {len(cg)} rows")
    except Exception as e:
        print(f"  CoinGecko error: {e}")
        cg = pd.DataFrame(columns=["date", "price", "circ_supply"])

    # On-chain queries
    rows = []
    for date, block in date_blocks.items():
        ve = get_supply(ADDRESSES["vePENDLE"], VEPENDLE_ABI, block, w3,
                        fn_names=["totalSupplyStored", "totalSupply"])
        sp = get_supply(spendle_addr, ERC20_ABI, block, w3) if spendle_addr != "0x" else None

        cg_row = cg[cg["date"] == date]
        circ   = cg_row["circ_supply"].values[0] if not cg_row.empty else None
        price  = cg_row["price"].values[0]        if not cg_row.empty else None

        row = {
            "date":             date,
            "block":            block,
            "vePENDLE_supply":  round(ve, 0) if ve else None,
            "sPENDLE_supply":   round(sp, 0) if sp else None,
            "PENDLE_circ_supply": round(circ, 0) if circ else None,
            "PENDLE_price_usd": round(price, 4) if price else None,
        }

        # Staking rates
        if ve and circ:
            row["vePENDLE_lock_rate_%"] = round(ve / circ * 100, 2)
        if sp and circ:
            row["sPENDLE_adoption_%"] = round(sp / circ * 100, 2)

        rows.append(row)
        ve_str = f"{ve:>12,.0f}" if ve else "           N/A"
        sp_str = f"{sp:>12,.0f}" if sp else "           N/A"
        print(f"  {date}: vePENDLE={ve_str}  sPENDLE={sp_str}  price=${price:.3f}" if price
              else f"  {date}: vePENDLE={ve_str}  sPENDLE={sp_str}")

    df = pd.DataFrame(rows)
    save_csv(df, OUT, label="Governance stats")

    # Print governance summary
    print("\n=== Summary ===")
    cols = ["date", "vePENDLE_supply", "sPENDLE_supply", "PENDLE_circ_supply",
            "vePENDLE_lock_rate_%", "sPENDLE_adoption_%", "PENDLE_price_usd"]
    print(df[[c for c in cols if c in df.columns]].dropna(
        subset=["vePENDLE_supply"]).to_string(index=False))

    # Current CoinGecko snapshot
    print("\n=== Current PENDLE market data ===")
    try:
        md = fetch_pendle_market_data()
        for k, v in md.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    main()
