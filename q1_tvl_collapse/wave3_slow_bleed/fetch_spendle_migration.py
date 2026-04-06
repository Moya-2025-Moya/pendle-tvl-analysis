"""
Wave 3 – sPENDLE migration rate vs vePENDLE decay (Jan–Apr 2026).

Goal:
  After vePENDLE renewals ceased (Jan 29, 2026) and sPENDLE launched
  (Jan 20, 2026), measure:
    a) How fast vePENDLE.totalSupply() decays (stakers exiting vs. migrating).
    b) How fast sPENDLE.totalSupply() grows (new stakers adopting).
  The gap = stakers who took the unstaking window as an exit.

Method:
  Weekly on-chain calls to both contracts' totalSupply() at blocks
  spanning Jan 1 – Apr 6, 2026.

IMPORTANT – sPENDLE contract address:
  The sPENDLE contract was deployed around Jan 20, 2026.
  ADDRESS MUST BE VERIFIED before running this script.
  Steps to find it:
    1. Check https://docs.pendle.finance (Contracts section).
    2. Check the governance announcement at https://gov.pendle.finance.
    3. Search Etherscan for transactions from the Pendle deployer wallet
       around Jan 15–25, 2026.
  Update ADDRESSES["sPENDLE"] in shared/utils.py once confirmed.

Output: data/spendle_migration_jan_apr_2026.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from shared.utils import (
    get_web3, blocks_for_dates, save_csv, ADDRESSES
)
import pandas as pd
from web3 import Web3

OUT = Path(__file__).parent / "data" / "spendle_migration_jan_apr_2026.csv"

# Weekly snapshots: start before sPENDLE launch (Jan 20) for baseline
DATES = [
    "2026-01-05", "2026-01-12", "2026-01-20",  # sPENDLE launch date
    "2026-01-27", "2026-01-29",                 # vePENDLE renewal ceased
    "2026-02-02", "2026-02-09", "2026-02-16", "2026-02-23",
    "2026-03-02", "2026-03-09", "2026-03-16", "2026-03-23", "2026-03-30",
    "2026-04-06",
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
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(address), abi=abi
    )
    for fn_name in (fn_names or ["totalSupply"]):
        try:
            raw = contract.functions[fn_name]().call(block_identifier=block)
            return raw / 10**decimals
        except Exception:
            continue
    return None


def main():
    print("=== sPENDLE migration tracking: Jan–Apr 2026 ===\n")

    spendle_addr = ADDRESSES.get("sPENDLE", "0x")
    if not spendle_addr or spendle_addr == "0x":
        print("WARNING: sPENDLE contract address not set in shared/utils.py")
        print("  → vePENDLE decay will still be tracked")
        print("  → Update ADDRESSES['sPENDLE'] once address is confirmed\n")

    w3 = get_web3()

    print("Finding blocks…")
    date_blocks = blocks_for_dates(DATES, w3)

    rows = []
    for date, block in date_blocks.items():
        # vePENDLE supply
        ve = get_supply(
            ADDRESSES["vePENDLE"], VEPENDLE_ABI, block, w3,
            fn_names=["totalSupplyStored", "totalSupply"]
        )

        # sPENDLE supply (may be None until address is set)
        sp = get_supply(spendle_addr, ERC20_ABI, block, w3) if spendle_addr != "0x" else None

        row = {"date": date, "block": block,
               "vePENDLE_supply": round(ve, 2) if ve else None,
               "sPENDLE_supply":  round(sp, 2) if sp else None}

        # Migration ratio: what fraction of old vePENDLE locked amount moved to sPENDLE
        # (rough proxy; actual migration requires comparing to pre-launch baseline)
        if ve is not None and sp is not None:
            row["sPENDLE_adoption_proxy"] = sp  # sPENDLE is net new, not a direct 1:1 migration

        rows.append(row)

        ve_str = f"{ve:>14,.0f}" if ve else "         N/A"
        sp_str = f"{sp:>14,.0f}" if sp else "         N/A"
        print(f"  {date} (block {block:,}): vePENDLE={ve_str}  sPENDLE={sp_str}")

    df = pd.DataFrame(rows)
    save_csv(df, OUT, label="sPENDLE migration")

    # Show decay rate
    ve_valid = df.dropna(subset=["vePENDLE_supply"])
    if len(ve_valid) >= 2:
        first = ve_valid.iloc[0]
        last  = ve_valid.iloc[-1]
        pct   = (last["vePENDLE_supply"] - first["vePENDLE_supply"]) / first["vePENDLE_supply"] * 100
        print(f"\nvePENDLE decay: {first['date']} → {last['date']}: {pct:+.1f}%")

    if "sPENDLE_supply" in df.columns:
        sp_valid = df.dropna(subset=["sPENDLE_supply"])
        if len(sp_valid) >= 2:
            first_sp = sp_valid.iloc[0]
            last_sp  = sp_valid.iloc[-1]
            print(f"sPENDLE growth: {first_sp['date']} → {last_sp['date']}: "
                  f"{first_sp['sPENDLE_supply']:,.0f} → {last_sp['sPENDLE_supply']:,.0f}")


if __name__ == "__main__":
    main()
