"""
Wave 1 – Aave V3: PT-sUSDE / PT-USDe collateral at Sep-2025 peak.

Goal: Quantify how much PT-sUSDE and PT-USDe was posted as Aave V3
      collateral at the peak of the Ethena-Pendle-Aave loop.

Method:
  1. Use getAllReservesTokens() to confirm PT token addresses on Aave V3.
  2. Call getReserveData at daily blocks Sep 22–26, 2025.
  3. Combine with USDC borrow rate on the same days (for spread calc).

Key finding: Aave V3 rates are stored as ANNUAL rates in RAY (1e27).
  APR% = rate_ray / 1e27 * 100  (no SECONDS_PER_YEAR multiplier)

Output: data/aave_pt_susde_sep2025.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import (
    get_web3, blocks_for_dates, aave_reserve_data, save_csv,
    ADDRESSES, RAY
)
import pandas as pd
from web3 import Web3

OUT = Path(__file__).parent / "data" / "aave_pt_susde_sep2025.csv"

# Real PT addresses on Aave V3 Ethereum (confirmed via getAllReservesTokens)
PT_RESERVES = {
    "PT-sUSDE-25SEP2025": "0x9F56094C450763769BA0EA9Fe2876070c0fD5F77",
    "PT-USDe-25SEP2025":  "0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a",
    # Earlier maturities for context (also Ethena-related)
    "PT-sUSDE-31JUL2025": "0x3b3fB9C57858EF816833dC91565EFcd85D96f634",
    "PT-USDe-31JUL2025":  "0x917459337CaAC939D41d7493B3999f571D20D667",
}
USDC_ADDRESS = ADDRESSES["USDC"]

# Daily snapshots around the Sep-25 expiry
DATES = [
    "2025-09-22", "2025-09-23", "2025-09-24",
    "2025-09-25", "2025-09-26", "2025-09-30",
]


def get_all_aave_reserves(w3: Web3) -> list[dict]:
    """List all Aave V3 reserves to verify PT token addresses."""
    abi = [{"inputs":[],"name":"getAllReservesTokens","outputs":[{"components":[
        {"type":"string","name":"symbol"},{"type":"address","name":"tokenAddress"}
    ],"type":"tuple[]"}],"stateMutability":"view","type":"function"}]
    dp = w3.eth.contract(
        address=Web3.to_checksum_address(ADDRESSES["AAVE_DATA_PROVIDER"]), abi=abi
    )
    tokens = dp.functions.getAllReservesTokens().call()
    return [{"symbol": t[0], "address": t[1]} for t in tokens]


def main():
    print("=== Aave V3: PT-sUSDE/USDe collateral at Sep-2025 peak ===\n")

    w3 = get_web3()

    # Verify addresses
    print("Verifying PT token addresses via getAllReservesTokens…")
    all_reserves = get_all_aave_reserves(w3)
    pt_reserves = [r for r in all_reserves if r["symbol"].startswith("PT-")]
    print(f"  All PT reserves on Aave V3 ({len(pt_reserves)}):")
    for r in pt_reserves:
        print(f"    {r['symbol']:40s}  {r['address']}")

    # Find blocks
    print("\nFinding blocks…")
    date_blocks = blocks_for_dates(DATES, w3)

    rows = []
    for date, block in date_blocks.items():
        print(f"\n--- {date} (block {block:,}) ---")

        # PT reserves (no borrow rate — collateral only, borrowing disabled)
        for label, addr in PT_RESERVES.items():
            try:
                d = aave_reserve_data(addr, block, w3)
                total = d["totalAToken"] / 1e18
                rows.append({
                    "date":              date,
                    "block":             block,
                    "asset":             label,
                    "address":           addr,
                    "totalAToken_units": round(total, 2),
                    "supplyAPR_%":       d["supplyAPR_%"],
                    "variableBorrowAPR_%": d["variableBorrowAPR_%"],
                    "note":              "PT collateral; borrowing disabled",
                })
                print(f"  {label}: collateral = ${total:>16,.2f}")
            except Exception as e:
                print(f"  {label}: ERROR – {e}")

        # USDC borrow rate (the cost of levering up)
        try:
            d = aave_reserve_data(USDC_ADDRESS, block, w3)
            usdc_borrow = d["variableBorrowAPR_%"]
            usdc_supply = d["supplyAPR_%"]
            usdc_total  = d["totalAToken"] / 1e6
            rows.append({
                "date":              date,
                "block":             block,
                "asset":             "USDC_borrow",
                "address":           USDC_ADDRESS,
                "totalAToken_units": round(usdc_total, 2),
                "supplyAPR_%":       usdc_supply,
                "variableBorrowAPR_%": usdc_borrow,
                "note":              "USDC borrow cost for carry loop",
            })
            print(f"  USDC supply = ${usdc_total:>16,.2f}  "
                  f"borrow APR = {usdc_borrow:.2f}%  supply APR = {usdc_supply:.2f}%")
        except Exception as e:
            print(f"  USDC: ERROR – {e}")

    df = pd.DataFrame(rows)
    save_csv(df, OUT, label="Aave PT-sUSDE collateral")

    # Summary: peak PT collateral before expiry
    print("\n=== PT Collateral Summary (Sep 24 — day before expiry) ===")
    sep24 = df[(df["date"] == "2025-09-24") & df["asset"].str.startswith("PT-")]
    if not sep24.empty:
        total_pt = sep24["totalAToken_units"].sum()
        print(sep24[["asset", "totalAToken_units"]].to_string(index=False))
        print(f"\nTotal PT collateral on Aave V3 at Sep-24: ${total_pt:,.2f}")

        # Leverage multiplier estimate
        # sUSDe supply at peak (from wave1/fetch_susde_supply.py): ~$5.13B
        susde_supply_peak = 5_132_966_920
        # With 85% LTV on Aave V3 for these assets, geometric series: 1/(1-0.85) ≈ 6.7x
        # But effective multiplier = Pendle TVL peak / base capital
        # Base capital proxy: sUSDe supply not in the loop
        print(f"\nLoop scale estimate:")
        print(f"  Total PT on Aave:         ${total_pt/1e9:.3f}B")
        print(f"  sUSDe supply at peak:     ${susde_supply_peak/1e9:.3f}B")
        print(f"  PT/sUSDe ratio:           {total_pt/susde_supply_peak*100:.1f}% of sUSDe supply was in loop")


if __name__ == "__main__":
    main()
