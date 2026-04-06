-- ============================================================
-- Pendle: PT token supply snapshots around Sep-25-2025 expiry
-- Paste into dune.com → New Query → Run → Export CSV
-- ============================================================
-- Shows the daily supply (outstanding balance) of the two main
-- Sep-25-2025 PT tokens as a TVL proxy.
-- Mint   = transfer FROM 0x000...000  (new PT created)
-- Redeem = transfer TO   0x000...000  (PT burned at expiry)
--
-- Known addresses:
--   PT-sUSDE-25SEP2025 : 0x9F56094C450763769BA0EA9Fe2876070c0fD5F77
--   PT-USDe-25SEP2025  : 0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a
--   PT-sUSDE-27NOV2025 : 0xe6A934089BBEe34F832060CE98848359883749B3  (next maturity)
--   PT-USDe-27NOV2025  : 0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7  (next maturity)
-- ============================================================

WITH daily_flows AS (
    SELECT
        date_trunc('day', evt_block_time)                                          AS day,
        contract_address                                                            AS pt_token,
        CASE
            WHEN contract_address = 0x9F56094C450763769BA0EA9Fe2876070c0fD5F77 THEN 'PT-sUSDE-25SEP2025'
            WHEN contract_address = 0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a THEN 'PT-USDe-25SEP2025'
            WHEN contract_address = 0xe6A934089BBEe34F832060CE98848359883749B3 THEN 'PT-sUSDE-27NOV2025'
            WHEN contract_address = 0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7 THEN 'PT-USDe-27NOV2025'
        END                                                                         AS pool_name,
        SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000
                 THEN CAST(value AS DOUBLE) / 1e18 ELSE 0 END)                     AS daily_minted,
        SUM(CASE WHEN "to"   = 0x0000000000000000000000000000000000000000
                 THEN CAST(value AS DOUBLE) / 1e18 ELSE 0 END)                     AS daily_redeemed
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address IN (
        0x9F56094C450763769BA0EA9Fe2876070c0fD5F77,
        0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a,
        0xe6A934089BBEe34F832060CE98848359883749B3,
        0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7
    )
    AND (
        "from" = 0x0000000000000000000000000000000000000000
        OR "to" = 0x0000000000000000000000000000000000000000
    )
    AND evt_block_time >= TIMESTAMP '2025-09-01 00:00:00'
    AND evt_block_time <  TIMESTAMP '2025-10-15 00:00:00'
    GROUP BY 1, 2, 3
),

running_supply AS (
    SELECT
        day,
        pool_name,
        daily_minted,
        daily_redeemed,
        daily_minted - daily_redeemed                                               AS net_daily,
        SUM(daily_minted - daily_redeemed) OVER (
            PARTITION BY pool_name ORDER BY day
        )                                                                            AS cumulative_supply
    FROM daily_flows
)

SELECT
    day,
    pool_name,
    ROUND(daily_minted, 0)       AS minted_tokens,
    ROUND(daily_redeemed, 0)     AS redeemed_tokens,
    ROUND(net_daily, 0)          AS net_flow,
    ROUND(cumulative_supply, 0)  AS outstanding_supply
FROM running_supply
ORDER BY pool_name, day
