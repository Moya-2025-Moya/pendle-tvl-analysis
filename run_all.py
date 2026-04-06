"""
Master runner — executes all data-fetch scripts in logical order.

Usage:
    python run_all.py              # run everything
    python run_all.py --q1        # only Q1 scripts
    python run_all.py --q2        # only Q2 scripts
    python run_all.py --q3        # only Q3 scripts
    python run_all.py --wave 1    # only Wave 1 scripts

Each script saves its output CSV to a data/ subfolder next to the script.
"""

import sys
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).parent

SCRIPTS = {
    "q1_wave1": [
        ROOT / "q1_tvl_collapse/wave1_expiry/fetch_susde_supply.py",
        ROOT / "q1_tvl_collapse/wave1_expiry/fetch_aave_pt_susde.py",
    ],
    "q1_wave2": [
        ROOT / "q1_tvl_collapse/wave2_trust_collapse/fetch_pt_yields.py",
        ROOT / "q1_tvl_collapse/wave2_trust_collapse/fetch_aave_rates.py",
        ROOT / "q1_tvl_collapse/wave2_trust_collapse/fetch_vependle_stats.py",
    ],
    "q1_wave3": [
        ROOT / "q1_tvl_collapse/wave3_slow_bleed/fetch_prices.py",
        ROOT / "q1_tvl_collapse/wave3_slow_bleed/fetch_spendle_migration.py",
    ],
    "q2": [
        ROOT / "q2_metrics/user_behavior/fetch_pt_rollover.py",
        ROOT / "q2_metrics/token_governance/fetch_governance_stats.py",
    ],
    "q3": [
        ROOT / "q3_recommendations/fetch_makerdao_rwa.py",
        ROOT / "q3_recommendations/fetch_curve_data.py",
    ],
}

DUNE_FILES = [
    ROOT / "q1_tvl_collapse/wave1_expiry/dune_per_pool_tvl.sql",
    ROOT / "q1_tvl_collapse/wave2_trust_collapse/dune_dau_q4_2025.sql",
    ROOT / "q1_tvl_collapse/wave3_slow_bleed/dune_dau_q1_2026.sql",
    ROOT / "q2_metrics/user_behavior/dune_pt_rollover.sql",
    ROOT / "q2_metrics/user_behavior/dune_yt_pt_ratio.sql",
]


def run_script(path: Path) -> bool:
    print(f"\n{'='*60}")
    print(f"Running: {path.relative_to(ROOT)}")
    print('='*60)
    result = subprocess.run([sys.executable, str(path)], capture_output=False)
    if result.returncode != 0:
        print(f"[FAILED] exit code {result.returncode}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q1",    action="store_true")
    parser.add_argument("--q2",    action="store_true")
    parser.add_argument("--q3",    action="store_true")
    parser.add_argument("--wave",  type=int, choices=[1, 2, 3])
    args = parser.parse_args()

    # Decide which groups to run
    if args.wave:
        groups = [f"q1_wave{args.wave}"]
    elif args.q1:
        groups = ["q1_wave1", "q1_wave2", "q1_wave3"]
    elif args.q2:
        groups = ["q2"]
    elif args.q3:
        groups = ["q3"]
    else:
        groups = list(SCRIPTS.keys())

    failed = []
    for group in groups:
        for script in SCRIPTS.get(group, []):
            ok = run_script(script)
            if not ok:
                failed.append(script)

    # Final summary
    print(f"\n{'='*60}")
    print("DONE")
    print(f"{'='*60}")

    if failed:
        print(f"\nFailed scripts ({len(failed)}):")
        for f in failed:
            print(f"  {f.relative_to(ROOT)}")
    else:
        print("All scripts completed successfully.")

    # Remind about Dune
    print(f"\n{'='*60}")
    print("MANUAL STEP: Run these Dune queries at dune.com/queries/new")
    print('='*60)
    for f in DUNE_FILES:
        print(f"  {f.relative_to(ROOT)}")
    print("\nExport each result as CSV and save to the data/ folder")
    print("next to the corresponding SQL file.")


if __name__ == "__main__":
    main()
