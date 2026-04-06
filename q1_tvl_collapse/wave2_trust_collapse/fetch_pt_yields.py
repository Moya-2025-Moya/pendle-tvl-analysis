"""
Wave 2 – Pendle PT implied yields on sUSDE/USDe, Sep–Dec 2025.

Goal: Document the carry inversion — PT yield dropping from ~13% to sub-5%
      while Aave USDC borrow stayed at 5–7%.

Method:
  Call readState() on the Pendle Market AMM contract at weekly historical
  blocks. The market stores lastLnImpliedRate (log of 1 + implied rate in
  WAD units). Convert to APY%:
      implied_rate = exp(lastLnImpliedRate / 1e18) - 1
      implied_APY% = implied_rate * 100

  Market addresses (confirmed via Pendle API /markets?pt=<address>):
    PT-sUSDE-25SEP2025 : 0xa36b60a14a1a5247912584768c6e53e1a269a9f7
    PT-USDe-25SEP2025  : 0x6d98a2b6cdbf44939362a3e99793339ba2016af4
    PT-sUSDE-27NOV2025 : 0xb6ac3d5da138918ac4e84441e924a20daa60dbdd
    PT-USDe-27NOV2025  : 0x4eaa571eafcd96f51728756bd7f396459bb9b869

Output: data/pt_implied_yields_sep_dec_2025.csv
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import get_web3, blocks_for_dates, save_csv
import pandas as pd
from web3 import Web3

OUT = Path(__file__).parent / "data" / "pt_implied_yields_sep_dec_2025.csv"

# Pendle V2 Market AMM ABI (readState returns MarketState struct)
PENDLE_ROUTER = "0x888888888889758F76e7103c6CbF23ABbF58F946"

MARKET_ABI = [
    {
        "inputs": [{"type": "address", "name": "router"}],
        "name": "readState",
        "outputs": [
            {"components": [
                {"name": "totalPt",             "type": "int256"},
                {"name": "totalSy",             "type": "int256"},
                {"name": "totalLp",             "type": "uint256"},
                {"name": "treasury",            "type": "address"},
                {"name": "scalarRoot",          "type": "int256"},
                {"name": "expiry",              "type": "uint256"},
                {"name": "lnFeeRateRoot",       "type": "uint256"},
                {"name": "reserveFeePercent",   "type": "uint256"},
                {"name": "lastLnImpliedRate",   "type": "uint256"},
            ], "type": "tuple"}],
        "stateMutability": "view",
        "type": "function",
    },
]

MARKETS = {
    "PT-sUSDE-25SEP2025": {
        "market":  "0xa36b60a14a1a5247912584768c6e53e1a269a9f7",
        "expiry":  "2025-09-25",
    },
    "PT-USDe-25SEP2025": {
        "market":  "0x6d98a2b6cdbf44939362a3e99793339ba2016af4",
        "expiry":  "2025-09-25",
    },
    "PT-sUSDE-27NOV2025": {
        "market":  "0xb6ac3d5da138918ac4e84441e924a20daa60dbdd",
        "expiry":  "2025-11-27",
    },
    "PT-USDe-27NOV2025": {
        "market":  "0x4eaa571eafcd96f51728756bd7f396459bb9b869",
        "expiry":  "2025-11-27",
    },
}

# Weekly snapshots: pre-expiry, post-expiry, and through Dec 2025
DATES = [
    "2025-08-01", "2025-08-15",
    "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
    "2025-09-24",  # day before Sep-25 expiry
    # Sep-25 PT pools expire here; Nov-27 pools take over
    "2025-10-01", "2025-10-08", "2025-10-15", "2025-10-22", "2025-10-29",
    "2025-11-05", "2025-11-12", "2025-11-19", "2025-11-26",
    "2025-12-01", "2025-12-08", "2025-12-15", "2025-12-22", "2025-12-29",
]


def ln_implied_rate_to_apy(last_ln_implied_rate: int, expiry_date: str,
                            query_date: str) -> float | None:
    """
    Convert Pendle's lastLnImpliedRate (WAD, 1e18) to annualised APY%.
    lastLnImpliedRate = ln(1 + implied_rate_per_year) * WAD
    implied_rate = exp(lastLnImpliedRate / WAD) - 1
    """
    from datetime import date
    try:
        # Cannot compute meaningful yield after expiry
        exp_d   = date.fromisoformat(expiry_date)
        query_d = date.fromisoformat(query_date)
        if query_d >= exp_d:
            return None

        wad = 1e18
        ln_rate = last_ln_implied_rate / wad
        implied_rate = math.exp(ln_rate) - 1
        return round(implied_rate * 100, 4)
    except Exception:
        return None


def main():
    print("=== Pendle PT implied yields: Aug–Dec 2025 ===\n")

    w3 = get_web3()

    print("Finding blocks…")
    date_blocks = blocks_for_dates(DATES, w3)

    rows = []
    for pool_name, pool_info in MARKETS.items():
        market_addr = pool_info["market"]
        expiry      = pool_info["expiry"]
        print(f"\n{pool_name}  ({market_addr})")

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(market_addr),
            abi=MARKET_ABI,
        )

        for date, block in date_blocks.items():
            try:
                state           = contract.functions.readState(
                    Web3.to_checksum_address(PENDLE_ROUTER)
                ).call(block_identifier=block)
                ln_implied_rate = state[8]   # lastLnImpliedRate (index 8 in struct)
                total_pt        = state[0]   # totalPt
                total_sy        = state[1]   # totalSy
                total_lp        = state[2]   # totalLp

                implied_apy = ln_implied_rate_to_apy(ln_implied_rate, expiry, date)

                rows.append({
                    "date":              date,
                    "pool":              pool_name,
                    "implied_APY_%":     implied_apy,
                    "lastLnImpliedRate": ln_implied_rate,
                    "totalPt_raw":       total_pt,
                    "totalSy_raw":       total_sy,
                    "totalLp_raw":       total_lp,
                })

                if implied_apy is not None:
                    print(f"  {date}: impliedAPY = {implied_apy:6.2f}%")
                else:
                    print(f"  {date}: (post-expiry or N/A)")
            except Exception as e:
                print(f"  {date}: ERROR – {e}")

    df = pd.DataFrame(rows)
    save_csv(df, OUT, label="PT implied yields")

    # Summary: show the yield collapse timeline
    valid = df[df["implied_APY_%"].notna()].copy()
    if not valid.empty:
        print("\n=== Implied APY by pool (monthly avg) ===")
        valid["month"] = pd.to_datetime(valid["date"]).dt.to_period("M")
        summary = (
            valid.groupby(["pool", "month"])["implied_APY_%"]
            .mean().round(2)
            .unstack(level=0)
        )
        print(summary.to_string())

        # Key claim: ~13% at peak → sub-5% post-expiry
        sep_peak = valid[valid["date"] <= "2025-09-22"]["implied_APY_%"]
        oct_onward = valid[valid["date"] >= "2025-10-01"]["implied_APY_%"]
        if not sep_peak.empty and not oct_onward.empty:
            print(f"\nPre-expiry peak (≤Sep-22): {sep_peak.max():.1f}%")
            print(f"Post-expiry avg (Oct+):    {oct_onward.mean():.1f}%")
            print("Claim: ~13% → sub-5%  →  " +
                  ("SUPPORTED" if sep_peak.max() > 10 and oct_onward.mean() < 6
                   else "CHECK VALUES"))


if __name__ == "__main__":
    main()
