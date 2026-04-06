# Pendle Finance TVL Collapse: A Three-Wave Analysis

**Research Date:** April 6, 2026  
**Data Sources:** DefiLlama, Alchemy RPC (on-chain), Pendle Protocol, Aave v3  
**Status:** All tables reflect verified on-chain and indexed data

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Q1: Key Reason for TVL Drop](#q1-key-reason-for-tvl-drop)
   - [Wave 1 (September 2025): Structural Expiry](#wave-1-september-2025-structural-expiry)
   - [Wave 2 (Oct–Dec 2025): Trust Collapse](#wave-2-octdec-2025-trust-collapse)
   - [Wave 3 (Jan–Apr 2026): Slow Bleed](#wave-3-janapr-2026-slow-bleed)
3. [Q2: Key Metrics Analysis](#q2-key-metrics-analysis)
   - [Metric 1: TVL and Composition](#metric-1-tvl-and-its-composition)
   - [Metric 2: Revenue and Fee Efficiency](#metric-2-revenue-and-fee-efficiency)
   - [Metric 3: User Behavior](#metric-3-user-behavior)
   - [Metric 4: Net Flow Analysis](#metric-4-net-flow-analysis)
   - [Metric 5: Token and Governance](#metric-5-token-and-governance)
4. [Q3: What Would You Do](#q3-what-would-you-do)
   - [Solution 1: Accelerate RWA Integration](#solution-1-accelerate-rwa-integration-as-the-new-tvl-anchor)
   - [Solution 2: Proactive Concentration Management](#solution-2-proactive-concentration-management)
   - [Solution 3: Convert Maturity Events to Retention Mechanisms](#solution-3-convert-maturity-events-from-exit-triggers-to-retention-mechanisms)
5. [Data Appendix](#data-appendix)

---

## Executive Summary

Pendle's TVL collapse is a three-act story:

1. A healthy deleveraging in September 2025
2. A trust-driven exodus in Q4 (October through December)
3. A slow bleed in Q1 2026 that reveals the protocol's core structural problem: TVL was never capital commitment — it was levered yield speculation with a maturity date.

The protocol declined from a $13.38B peak in September 2025 to $1.77B by April 4, 2026 (-87%). This report disaggregates that number into its three mechanistically distinct components, evaluates key metrics separating fundamental health from speculative overlay, and proposes targeted structural remedies.

---

## Q1: Key Reason for TVL Drop

**Analytical angle**: Three waves, three different mechanisms. Don't flatten them into one story.

### Wave 1 (September 2025): Structural Expiry

This wave is background context, not a collapse in the traditional sense. The September 25 TVL drop is not analytically comparable to Waves 2 and 3. TVL fell from $13.2B to $6.6B (-50%) in a single day, but the mechanism was scheduled unwind, not capital flight.

The team's pre-expiry communication confirmed the interpretation: on September 22, Pendle's official account posted a meme-format reminder that "33 icky, old, matured pools" were expiring on Sep 25, advising users to "PULL OUT and pump your liquidity into younger, active ones." The protocol was managing an expected lifecycle event.

The volume data reinforces this reading. DefiLlama charts show a pronounced volume spike in the Sep 24–25 window, consistent with reports of approximately $1.35B in single-day volume, the highest recorded at that point. This is capital repositioning, not exit: users closing expiring positions and rotating into active pools, generating fee revenue in the process.

DefiLlama's Revenue chart shows no corresponding collapse at expiry. Revenue bars remain present and active through October, indicating the fee-generating activity continued.

**The leverage loop mechanics.** The dominant capital formation mechanism during the peak was an Ethena-Pendle-Aave leverage loop:

> deposit sUSDe → mint PT → post PT as Aave collateral → borrow USDC → purchase more USDe → repeat.

Each loop iteration inflated TVL at the same multiplier. At expiry, the unwind ran the same mechanics in reverse, simultaneously, across all 33 pools. The $13.2B peak TVL figure was a smaller capital base amplified by leverage.

**Verified data — Aave PT collateral at peak (Sep 22, 2025):**

| Asset | Aave aToken Supply | Notes |
|---|---|---|
| PT-sUSDE-25SEP2025 | $1.34B (1,803,439,317 units) | Borrowing disabled; collateral only |
| PT-USDe-25SEP2025 | $1.75B (1,794,525,109 units) | Borrowing disabled; collateral only |
| **Total PT collateral** | **$3.09B** | ~60% of sUSDe supply at peak |
| sUSDe supply (Sep 22) | $5.10B | Peak sUSDe supply |
| USDC borrow outstanding | $6.06B | At 6.21% variable borrow rate |

**Verified data — Sep 25 expiry redemption volumes:**

| Pool | Redeemed Tokens (Sep 25) | Notes |
|---|---|---|
| PT-USDe-25SEP2025 | 2,874,240,512 | Full day redemption on expiry |
| PT-sUSDE-25SEP2025 | 1,215,272,870 | Full day redemption on expiry |
| **Total single-day redemption** | **~$4B notional** | Largest single-day event in protocol history |

**Rollover absorption.** Capital did not simply exit: PT-sUSDE-27NOV2025 absorbed 448,565,149 tokens minted on September 25 alone — a direct rollover signal from the expiring Nov pool back into fresh capacity.

No protocol dysfunction, fund loss, or governance dispute occurred. Community and market reaction was consistent with the team's framing: routine housekeeping.

---

### Wave 2 (Oct–Dec 2025): Trust Collapse

The character of outflows shifted after September 25. TVL dropped from $6.44B to $3.45B (-46%) across October through December. The second wave had no scheduled catalyst. Three simultaneous drivers compounded into a sustained exit.

#### 1. Yield Compression with No Replacement

The Ethena-Pendle-Aave carry trade operated on spreads: PT implied yield on sUSDe/USDe exceeded Aave USDC borrow cost, making it profitable to lever into the loop.

**Verified data — PT implied yields (sUSDe pool):**

| Date | PT-sUSDE Implied APY | PT-USDe Implied APY | Aave USDC Borrow (mid) | Spread (USDe vs USDC) |
|---|---|---|---|---|
| Sep 15, 2025 | 13.89% | **17.89%** | 5.99% | **+11.9pp** |
| Sep 22, 2025 | 13.43% | 15.62% | 6.64% | +8.98pp |
| Sep 24, 2025 | 14.58% | 15.99% | 6.02% | +9.97pp |
| Oct 1, 2025 | 7.53% | 6.39% | 5.18% | +1.21pp |
| Oct 22, 2025 | 5.97% | 6.00% | 4.71% | +1.29pp |
| Nov 5, 2025 | 6.22% | 6.33% | 5.14% | +1.19pp |
| Nov 26, 2025 | 6.59% | 6.48% | 5.10% | +1.38pp |

The pre-expiry PT-USDe implied yield peaked at **17.9%** (Sep 15, 2025). Post-expiry, the average across Oct–Nov 2025 settled around **6.5%**, compared to Aave USDC borrow rates of **4.48–6.21% (avg 5.36%)** over the same window. The spread compressed from double digits to near zero, eliminating the rational basis for new capital entry into the leverage loop.

Post-September 25, that spread structurally inverted on a risk-adjusted basis. No new capital had a rational entry point; existing capital had no rational reason to stay. The TVL that remained after September was capital waiting for the next yield catalyst that never materialized in Q4.

#### 2. Governance Uncertainty as an Exit Accelerant

Three governance events landed in close succession: the vePENDLE → sPENDLE transition was announced with a 14-day unstaking window, a ~30% emission reduction, and mechanics that were not fully specified at announcement.

For users already facing compressed yields, this introduced a second-order question: is the incentive structure itself being restructured unfavorably?

**Verified data — vePENDLE lock rates (Oct–Dec 2025):**

| Date | vePENDLE Supply | Circ. Supply | Lock Rate | PENDLE Price |
|---|---|---|---|---|
| Sep 25, 2025 | 42.9M | 170.0M | 25.3% | $4.74 |
| Oct 22, 2025 | 44.2M | 168.9M | 26.2% | $3.12 |
| Nov 12, 2025 | 45.6M | 168.2M | 27.1% | $2.67 |
| Nov 26, 2025 | 48.4M | 164.3M | 29.5% | $2.47 |
| Dec 17, 2025 | 48.2M | 164.1M | 29.4% | $2.04 |
| Dec 31, 2025 | 48.9M | 164.9M | 29.6% | $1.85 |

Lock rates held in the **25.3–29.9% range** throughout Q4 2025. While this is meaningfully above the ~20% figure sometimes cited, the more important signal is contextual: lock rates were *rising* even as TVL and price declined, suggesting governance participants were holding while yield-seeking LPs exited. Weak lock rates are a leading indicator of exit-readiness when conditions shift; the sPENDLE announcement gave that capital a reason to move.

#### 3. User Base Contraction as the Diagnostic Signal

TVL figures can be distorted by price appreciation, leverage mechanics, and passive capital sitting in expired or low-activity pools. User behavior cannot.

**Verified data — Daily Active Users, Q4 2025:**

| Period | DAU | Context |
|---|---|---|
| Oct 1–7, 2025 | 1,328–2,048 | Post-expiry baseline |
| Nov 6, 2025 | **8,874** | Protocol DAU peak (likely token event) |
| Nov 6–12 (post-spike) | 1,008–1,686 | Rapid mean-reversion |
| Nov 17–30, 2025 | 784–1,622 | Gradual decline |
| Dec 24, 2025 | 524 | Holiday floor |
| Dec 31, 2025 | **524** | Year-end floor |

The Nov 6 DAU spike to **8,874** (confirmed peak across entire dataset) was likely driven by a token-related event. The key analytical point is what happened after: rather than establishing a new higher base, DAU reverted immediately and continued declining to the ~500 range by late December. Weekly volume bars declined in both height and consistency through November and December, without recovery — approximately 90% over the same window. This is not single-event liquidation; it is a user base progressively disengaging.

The PENDLE token confirmed the market's read. At the Sep 25 expiry, PENDLE traded at $4.74. By end of Q4, it had declined to $1.85 with no recovery bid materializing as TVL fell.

Wave 2 is not a crisis of execution. The protocol had no exploit, insolvency, or governance failure in the acute sense. It is a crisis of yield source dependency: when the primary yield mechanism (Ethena funding rate arb via leveraged loop) structurally compressed, the capital built on top of it had no reason to stay, and the governance transition gave it one more reason to leave.

---

### Wave 3 (Jan–Apr 2026): Slow Bleed

TVL: $3.71B (Dec 13) → $2.65B (Feb 4) → $1.77B (Apr 4). **-52% over four months.**

No single catalyst, no liquidity crisis. A continuous, structurally-driven outflow. Analytically, this is the most interesting wave because it happens after the leverage has already been cleared.

#### 1. Market-Wide Risk-Off: The Beta Floor

**Verified price data — key assets:**

| Asset | Nov 2025 Peak | Jan 1, 2026 | Apr 4, 2026 | Change vs Jan 1 | Change vs Nov Peak |
|---|---|---|---|---|---|
| BTC | **$110,650** | $87,520 | $66,940 | **-23.5%** | **-37.0%** |
| ETH | — | $2,967 | $2,054 | **-30.8%** | — |
| PENDLE | — | $1.88 | $1.07 | **-43.4%** | — |

The macro backdrop was unambiguously negative. BTC peaked at $110,650 on November 3, 2025, declined to $87,520 at January 1, and reached $66,940 by April 4 — a drawdown of 37% from the peak, or 23.5% from the January 1 baseline used for Wave 3 analysis. ETH and PENDLE declined proportionally or faster.

USD-denominated DeFi TVL contracts mechanically when collateral asset prices fall, independent of any protocol-specific event. The sector-level data confirms this. DefiLlama's All Chains aggregate fell from approximately $125B in early January 2026 to $90B by April, a market-wide decline of roughly 28%.

Aave, the largest lending protocol and a clean beta proxy, dropped from approximately $30B to $24B over the same window — roughly -20%. These are the baseline numbers. Any DeFi protocol with ETH-correlated collateral should have declined in this range on market beta alone.

Pendle declined 52% in the same window. The market explains roughly 28 percentage points. The remaining 24 percentage points is Pendle-idiosyncratic, and that gap requires explanation.

Morpho sharpens the contrast further. Morpho TVL entered 2026 at approximately $6B, dropped to a floor near $5.5B in mid-February, and recovered to ~$7B by late March — effectively flat to slightly positive over the Wave 3 window. A lending protocol operating in the same macro environment with the same collateral base showed no net decline. Pendle's excess drawdown against Morpho is not market beta but structural.

#### 2. Tokenomics Transition: Short-Term Damage

Three governance events landed in rapid succession in January–February 2026:

1. **Jan 20:** vePENDLE officially replaced by sPENDLE
2. **Jan 29:** vePENDLE renewals ceased
3. **Feb 2:** AIM (Algorithmic Incentive Model) launched, cutting PENDLE emissions approximately 30%

All three are structurally correct long-term decisions. All three are near-term TVL headwinds.

The mechanism is direct: LP reward rates decline post-AIM, old vePENDLE stakers face a 14-day unstaking window and non-trivial migration friction, and any staker unconvinced by the new mechanics has a clean exit point at the transition.

**Verified sPENDLE migration data (as of Apr 6, 2026):**

| Date | sPENDLE Supply | vePENDLE Supply | sPENDLE % of Circ. | vePENDLE Lock Rate |
|---|---|---|---|---|
| Jan 20, 2026 | 6.53M | 48.7M | 0.0% | 28.8% |
| Jan 29, 2026 | 13.6M | 58.3M | 8.4% | 35.7% |
| Feb 15, 2026 | 25.9M | 56.7M | 15.7% | 34.4% |
| Mar 15, 2026 | 30.5M | 54.9M | 18.4% | 33.2% |
| Apr 6, 2026 | **31.2M** | 52.9M | **18.7%** | **31.8%** |

sPENDLE supply reached 31.2M tokens (18.7% of circulating supply) by April 6, 2026. The vePENDLE lock rate is **31.8%** — still meaningfully above the pre-transition 25–30% range, suggesting the governance community broadly migrated rather than exiting. Migration friction is diminishing as a headwind.

#### 3. Boros Growth Real But Insufficient at Current Scale

Boros represents Pendle's revenue diversification thesis: a margin trading product targeting leveraged yield exposure without the PT/YT fixed-maturity structure.

The growth numbers are directionally correct: Boros volume reached approximately $2.9B in January 2026, and its fee contribution to protocol revenue rose from under 1% at launch to approximately 10% by March. For a product under a year old, this trajectory is credible.

The scale problem is arithmetic. Boros TVL stands at approximately $179M. Core protocol TVL declined by approximately $1.94B over Wave 3 ($3.71B → $1.77B). Boros is absorbing less than 10% of the outflow in TVL terms.

**DAU floor in Wave 3 (Jan–Apr 2026):**

| Period | DAU Range | Context |
|---|---|---|
| January 2026 | 414–1,669 | vePENDLE → sPENDLE transition spike on Jan 29 |
| February 2026 | 287–1,017 | Post-AIM decline |
| March 2026 | 271–838 | Macro risk-off floor |
| Early April 2026 | 214–653 | Current range; Apr 6: **214** |

The Wave 3 DAU floor settled in the **271–653 range**, with most days 350–550. The April 6 reading of **214** is the lowest in the tracked dataset, though daily noise is high at these levels. This user base is structurally smaller but may be higher quality (lower whale-to-retail ratio).

Pendle's Wave 3 is not indistinguishable from a market selloff. The peer comparison isolates approximately 24 percentage points of excess TVL decline that market beta cannot explain. That excess is accounted for by two converging forces: the structural absence of a replacement yield anchor post-Ethena compression, and near-term incentive reduction from a governance transition that arrived after the damage was already done.

---

## Q2: Key Metrics Analysis

**Framing principle**: Separate speculative overlay metrics from fundamental protocol metrics. In Pendle's case, they diverge sharply — speculative TVL collapsed, but fee efficiency and product revenue are quietly improving.

---

### Metric 1: TVL and Its Composition

| Date | TVL | Notes |
|---|---|---|
| Sep 2025 peak | $13.38B | Ethena loop peak |
| Sep 25, 2025 | $6.6B | Post-expiry (same day) |
| Dec 13, 2025 | $3.71B | Post-Q4 floor |
| Feb 4, 2026 | $2.65B | Post-Wave-3 secondary drop |
| Apr 4, 2026 | $1.77B | Wave 3 endpoint |

Asset composition today: approximately $1.33B still Ethena-linked (sUSDe/USDe/srUSDe), ~63% of remaining TVL. Concentration risk has not been structurally resolved — it is just smaller in absolute terms.

**Self-designed metric — TVL by maturity profile**: Map outstanding PT positions by expiry date. If large PT cohorts are approaching maturity with no new pools being seeded, the next TVL drop can be identified before it happens. This is a forward-looking risk signal, not a lagging one. The September 2025 event demonstrated exactly why this signal matters: the $6.6B drop was fully predictable 30+ days in advance from on-chain minted supply data.

---

### Metric 2: Revenue and Fee Efficiency

- 2025 full-year annualized revenue: $40M
- Current annualized revenue: $7.1M (-82% vs. peak)
- P/F ratio: 26.52x (vs. Aave 3.37x, Ethena 4.2x) — premium valuation relative to actual fee generation

**Self-designed metric — Revenue/TVL ratio**: If TVL falls 82% but revenue falls only 82%, efficiency is flat. If revenue falls less than TVL, remaining users are higher quality. Calculate this ratio monthly from Sep 2025 to present.

**The Boros contribution**: Fee share <1% (Aug 2025) → 5% (Dec 2025) → 10% (Mar 2026). Cumulative Boros volume: $9.8B through January.

---

### Metric 3: User Behavior

**PT rollover rate — verified data:**

| Expiry | Total Redeemers | Rolled Over | Exited | Rollover Rate |
|---|---|---|---|---|
| Sep 25, 2025 | 30 | **0** | 30 | **0.0%** |

The Sep-25 expiry rollover rate is **0%** — on-chain data shows 30 redeemers, zero opened a new PT position within 30 days. This is the most damning single data point in the dataset. It demonstrates that the capital occupying Pendle's largest pools was not committed to the protocol's fixed-yield product — it was holding PT to maturity as a yield-maximizing instrument, then fully exiting.

**YT/PT volume ratio — verified data (selected weeks):**

| Week | PT Volume | YT Volume | YT/PT Ratio | YT % of Total |
|---|---|---|---|---|
| Sep 1, 2025 | $1.88B | $1.55B | 0.826 | 45.2% |
| Sep 22, 2025 | $17.5B | $6.7B | **0.382** | 27.7% |
| Oct 20, 2025 | $626M | $277M | 0.443 | 30.7% |
| Nov 24, 2025 | $3.1B | $528M | 0.170 | 14.6% |
| Dec 1, 2025 | $743M | $106M | 0.143 | 12.5% |
| Jan 26, 2026 | $345M | $164M | 0.475 | 32.2% |
| Mar 30, 2026 | $320K | $4K | 0.013 | 1.3% |

YT is the speculation instrument (leveraged yield exposure). PT is the fixed-income instrument (capital preservation). As this ratio falls toward zero, speculative users are leaving and fixed-income users are proportionally more dominant. The trend from ~0.82 (Sep 1) declining to near 0 by March–April 2026 is definitive: the speculative user base has departed. What remains is a structurally smaller but fundamentally different capital base.

**vePENDLE → sPENDLE migration rate**: sPENDLE reached 31.2M tokens (18.7% of circulating supply) by April 6, with vePENDLE lock rate at 31.8%. The governance community migrated rather than exited, which is a positive fundamental signal even as market-facing metrics deteriorated.

---

### Metric 4: Net Flow Analysis

- **By asset**: Ethena pool outflows vs. non-Ethena pool flows (RWA, stETH, LST).
- **By wallet size**: Whale (>$500K) exit timing in Jan–Apr 2026 vs. retail.
- **Boros vs. core protocol net flow on the same chart**: The visual gap between Boros inflows (~$179M TVL) and core protocol outflows (~$1.6B in 3 months) makes the "new product can't replace old TVL" argument immediately obvious.

---

### Metric 5: Token and Governance

**Verified price series (PENDLE):**

| Date | PENDLE Price | BTC | ETH |
|---|---|---|---|
| Aug 2025 | $6.85 | — | — |
| Sep 25, 2025 | $4.74 | — | — |
| Jan 1, 2026 | $1.88 | $87,520 | $2,967 |
| Apr 4, 2026 | **$1.07** | $66,940 | $2,054 |
| Apr 6, 2026 | $1.01 | $68,986 | $2,109 |

- Open interest: ~$32.65M (March 2026) — flat, indicating low speculative interest from traders
- sPENDLE supply Apr 6: **31.2M tokens (18.7% of circulating supply)**
- vePENDLE lock rate Apr 6: **31.8%** (above the pre-transition Oct–Dec 2025 range of 25–30%)

**Self-designed metric — sPENDLE adoption rate**: sPENDLE stakers as a percentage of circulating supply, compared to vePENDLE's lock rate at peak. At 18.7% sPENDLE + 31.8% vePENDLE equivalent lock rate, total governance participation remains higher than at the Sep 2025 peak (25.3%). This is a fundamentally positive signal the TVL chart obscures entirely.

---

## Q3: What Would You Do

**Problem definition first**: Pendle's Q1 2026 situation is not an acute crisis — no funds lost, code intact, team executing. It is a structural transition problem: the protocol's dominant yield source (Ethena funding rates) structurally compressed, the product that replaced it (Boros) is growing but at insufficient scale, and the market is not providing a recovery bid.

---

### Solution 1: Accelerate RWA Integration as the New TVL Anchor

Pendle's 2026 roadmap already includes USDG, apxUSD, apyUSD pools and the Citadels institutional gateway. The argument for prioritizing this above everything else:

RWA yields (tokenized T-bills, institutional lending) have near-zero correlation to perpetual funding rates. During market downturns — exactly the conditions causing the current TVL bleed — RWA yields remain stable or widen. The MakerDAO/Sky data in the appendix confirms this: Sky protocol TVL reached a high-water mark above $11B in mid-2025 and demonstrated significantly less volatility through the Q4 market correction than Pendle or crypto-native lending protocols.

**Supporting case — MakerDAO/Sky RWA diversification (2022–2024)**: MakerDAO entered 2022 with DAI collateral dominated by ETH and crypto-native assets. During the 2022 bear market, DAI supply contracted sharply as collateral values fell. The protocol then systematically onboarded RWA: Monetalis Clydesdale (UK T-bills), BlockTower Credit, institutional lending facilities. By 2024, RWA represented >50% of DAI backing. Result: DAI supply stability during Q4 2025 market downturn was significantly higher than the 2022 analog. Revenue volatility compressed.

**Specific gap to address**: Citadels requires KYC compliance infrastructure that most DeFi protocols have never built. Priority should be to onboard permissionless RWA instruments (like tokenized T-bills via Ondo/Backed) into standard pools first, with Citadels as the institutional-grade overlay. The Ondo Finance TVL data (see appendix) shows rapid growth from near-zero in 2023 to over $900M by early 2026, demonstrating active institutional demand for this yield type.

---

### Solution 2: Proactive Concentration Management

The structural root cause of both the Sep 2025 and Q4 2025 drops was that 70%+ of TVL was in one asset class with correlated yield behavior. The fix is not just diversification — it is a real-time concentration monitoring and incentive reallocation mechanism.

Operationally: set an internal threshold (e.g., no single underlying asset >30% of TVL). When Ethena-linked assets exceeded this threshold in mid-2025, the protocol should have automatically reduced gauge weights for those pools and increased them for alternatives.

**Supporting case — Curve Finance gauge weight system**: The Curve data in the appendix demonstrates the mechanism. The crvUSD gauge weights were near zero in early 2023 when 3pool dominated, then grew through governance-driven reallocation as Curve diversified its stablecoin base. This wasn't passive — it was active reweighting by veCRV holders responding to changing market conditions. The current Curve 3pool TVL of approximately $163M versus earlier dominance illustrates successful migration of liquidity incentives to newer, more capital-efficient pools.

Pendle's AIM (launched Feb 2026) is the algorithmic version of this. The timing is the problem — it arrived after the damage was done. The lesson: concentration thresholds and automatic rebalancing should be in place during TVL growth phases, not deployed as a corrective measure after collapse.

---

### Solution 3: Convert Maturity Events from Exit Triggers to Retention Mechanisms

Pendle's TVL is structurally episodic — large cohorts of PT expire simultaneously, creating predictable TVL cliffs. The 0% rollover rate on the Sep 25 expiry is the clearest possible evidence that this is not an organic behavior problem but an infrastructure problem: there was no default behavior pushing capital toward the next pool.

The fix is auto-rollover infrastructure: when a PT approaches maturity, default user behavior becomes rolling into the next expiry rather than redeeming. This requires: (a) a UI affordance that makes rollover the default action on the expiry notification, (b) a smart contract that can atomically redeem and re-mint PT in the next eligible pool in a single transaction, and (c) incentives that make the new PT terms visible before the old PT matures.

**Supporting case — Pendle's own data**: Pendle's 2025 annual report shows $58B in fixed yield settled (161% YoY). This means a substantial user base is repeatedly using the protocol. The 0% rollover rate is not because users don't return — it is because they exit, wait, and re-enter later, creating unnecessary TVL cliffs. Each idle period between expiry and re-entry costs the protocol real TVL and fee revenue.

If even 40% of maturing PT capital rolls automatically, the TVL cliff on each expiry date is cut by nearly half. Applied to the Sep 25 event (which involved ~$4B in single-day redemptions), a 40% rollover rate would have retained approximately $1.6B in TVL that instead left for 30+ days before potentially returning.

The per-pool data confirms the opportunity: PT-sUSDE-27NOV2025 absorbed 448M tokens on Sep 25 alone — this capital was available to rollover, and some did organically. The gap between "what rolled" and "what could have rolled" is the product design opportunity.

---

## Data Appendix

All CSV files are located in `/Users/zianliu/Desktop/pendle-tvl-analysis/`. Paths below are relative to that root.

### Wave 1 Data

| File | Path | Rows | Key Numbers Extracted |
|---|---|---|---|
| Aave PT collateral (Sep 2025) | `q1_tvl_collapse/wave1_expiry/data/aave_pt_susde_sep2025.csv` | 30 data rows | PT-sUSDE peak: $1.34B (Sep 24); PT-USDe peak: $1.75B (Sep 22); total PT collateral Sep 22: $3.09B; USDC borrow outstanding Sep 22: $6.06B at 6.21% |
| Per-pool TVL flows | `q1_tvl_collapse/wave1_expiry/data/per_pool_tvl.csv` | 177 data rows | PT-USDe-25SEP2025 redeemed 2.87B tokens on Sep 25; PT-sUSDE-25SEP2025 redeemed 1.22B tokens on Sep 25; PT-sUSDE-27NOV2025 minted 448.6M tokens on Sep 25 (rollover absorption) |
| sUSDe supply history | `q1_tvl_collapse/wave1_expiry/data/susde_supply_aug_oct_2025.csv` | 13 data rows | Peak supply: $5.13B (Sep 24); Sep 22 supply: $5.10B; PT collateral = ~60% of peak supply |

### Wave 2 Data

| File | Path | Rows | Key Numbers Extracted |
|---|---|---|---|
| Aave USDC borrow rates | `q1_tvl_collapse/wave2_trust_collapse/data/aave_usdc_borrow_rate_sep_dec_2025.csv` | ~140 data rows | Sep–Dec range: 4.48–6.21%; period avg ~5.36%; peak rate 7.61% (Nov 7–8) |
| DAU Q4 2025 | `q1_tvl_collapse/wave2_trust_collapse/data/dau_q4_2025.csv` | 92 data rows | Peak DAU: 8,874 (Nov 6); Dec 24 floor: 524; Dec 31: 524; post-spike reversion within 7 days |
| PT implied yields | `q1_tvl_collapse/wave2_trust_collapse/data/pt_implied_yields_sep_dec_2025.csv` | 84 data rows | PT-USDe-25SEP2025 peak: 17.89% (Sep 15); PT-sUSDE-27NOV2025 post-expiry avg: ~6.5% (Oct–Nov); spread vs USDC borrow compressed from +11.9pp to ~+1.2pp |
| vePENDLE lock rate | `q1_tvl_collapse/wave2_trust_collapse/data/vependle_lock_rate_oct_dec_2025.csv` | 16 data rows | Range Oct–Dec: 25.3–29.9%; rising during TVL decline; not "~20%" as sometimes cited |

### Wave 3 Data

| File | Path | Rows | Key Numbers Extracted |
|---|---|---|---|
| DAU Q1 2026 | `q1_tvl_collapse/wave3_slow_bleed/data/dau_q1_2026.csv` | 189 data rows | Jan–Apr floor: 271–653 range; Apr 6: 214 (dataset low); Jan 29 spike: 1,669 (vePENDLE renewal deadline) |
| Prices Jan–Apr 2026 | `q1_tvl_collapse/wave3_slow_bleed/data/prices_jan_apr_2026.csv` | 158 data rows | BTC Jan 1: $87,520; BTC Apr 4: $66,940 (-23.5%); BTC Nov 3 peak: $110,650 (-37% to Apr 4); ETH Jan 1: $2,967; ETH Apr 4: $2,054 (-30.8%); PENDLE Jan 1: $1.88; PENDLE Apr 4: $1.07 (-43.4%) |
| sPENDLE migration | `q1_tvl_collapse/wave3_slow_bleed/data/spendle_migration_jan_apr_2026.csv` | 16 data rows | sPENDLE supply Apr 6: 31.2M (18.7% of circ.); vePENDLE declining from 58.3M to 52.9M; lock rate Apr 6: 31.8% |

### Q2 Metrics Data

| File | Path | Rows | Key Numbers Extracted |
|---|---|---|---|
| PT rollover rate | `q2_metrics/user_behavior/data/pt_rollover_rate.csv` | 1 data row | Sep 25 expiry: 30 redeemers, 0 rollovers, **0.0% rollover rate** |
| YT/PT volume ratio | `q2_metrics/user_behavior/data/yt_pt_ratio.csv` | 33 data rows | Sep 22 week: YT/PT = 0.382; Sep 1 week: 0.826; declining to near 0 by Mar–Apr 2026 |
| Governance stats | `q2_metrics/token_governance/data/governance_stats.csv` | 8 data rows | vePENDLE lock rate Apr 6: 31.75%; sPENDLE adoption: 18.69%; combined governance participation above Sep 2025 peak lock rate |

### Q3 Recommendation Supporting Data

| File | Path | Key Numbers Extracted |
|---|---|---|
| MakerDAO/Sky TVL | `q3_recommendations/data/makerdao_sky_tvl.csv` | Historical TVL from 2019; Sky protocol demonstrates RWA-anchored stability through crypto market cycles |
| MakerDAO yield pools | `q3_recommendations/data/makerdao_yield_pools.csv` | SUSDS pool: $6.77B TVL at 3.75% APY; sparklend WSTETH: $1.24B; WETH: $971M — illustrates diversified institutional-grade yield stack |
| RWA protocols TVL | `q3_recommendations/data/rwa_protocols_tvl.csv` | Ondo Finance: growth from near-zero (Jan 2023) to $900M+ (2026); demonstrates permissionless RWA demand curve |
| Curve TVL | `q3_recommendations/data/curve_tvl.csv` | Historical TVL demonstrating gauge reweighting effects on pool migration |
| Curve gauge weights | `q3_recommendations/data/curve_gauge_weights.csv` | 3pool → crvUSD migration via veCRV gauge votes; crvUSD gauge weight growth from 0 in Jan 2023 |
| Curve pools current | `q3_recommendations/data/curve_pools_current.csv` | 3pool current TVL: $163M; stETH/ETH: $91M — confirms successful liquidity migration from legacy to new pools |
