-- ============================================================
-- PT Rollover Rate: Sep-25-2025 expiry
-- Paste into dune.com → New Query → Run → Export CSV
-- ============================================================
-- For every wallet that redeemed (burned) Sep-25 PT tokens,
-- checks whether that same wallet also minted a LATER-maturity
-- PT token within 30 days — indicating they "rolled over"
-- rather than exiting entirely.
--
-- Redeem  = ERC20 Transfer FROM wallet TO 0x000...000
-- New mint = ERC20 Transfer FROM 0x000...000 TO wallet
--
-- Sep-25 pools (expiring):
--   PT-sUSDE-25SEP2025 : 0x9F56094C450763769BA0EA9Fe2876070c0fD5F77
--   PT-USDe-25SEP2025  : 0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a
--
-- Next-maturity pools (rollover targets):
--   PT-sUSDE-27NOV2025 : 0xe6A934089BBEe34F832060CE98848359883749B3
--   PT-USDe-27NOV2025  : 0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7
--   PT-sUSDE-5FEB2026  : 0xE8483517077afa11A9B07f849cee2552f040d7b2
--   PT-USDe-5FEB2026   : 0x1F84a51296691320478c98b8d77f2Bbd17D34350
-- ============================================================

WITH redeemers AS (
    SELECT DISTINCT
        "from"                          AS wallet,
        date_trunc('day', evt_block_time) AS redeem_day,
        SUM(CAST(value AS DOUBLE)) OVER (PARTITION BY "from") / 1e18 AS total_redeemed
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address IN (
        0x9F56094C450763769BA0EA9Fe2876070c0fD5F77,
        0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a
    )
    AND "to" = 0x0000000000000000000000000000000000000000
    AND evt_block_time >= TIMESTAMP '2025-09-25 00:00:00'
    AND evt_block_time <  TIMESTAMP '2025-10-10 00:00:00'
    AND "from" != 0x0000000000000000000000000000000000000000
),

new_minters AS (
    SELECT DISTINCT "to" AS wallet
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address IN (
        0xe6A934089BBEe34F832060CE98848359883749B3,
        0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7,
        0xE8483517077afa11A9B07f849cee2552f040d7b2,
        0x1F84a51296691320478c98b8d77f2Bbd17D34350
    )
    AND "from" = 0x0000000000000000000000000000000000000000
    AND evt_block_time >= TIMESTAMP '2025-09-25 00:00:00'
    AND evt_block_time <  TIMESTAMP '2025-10-25 00:00:00'
    AND "to" != 0x0000000000000000000000000000000000000000
),

joined AS (
    SELECT
        r.wallet,
        r.redeem_day,
        CASE WHEN m.wallet IS NOT NULL THEN 1 ELSE 0 END AS rolled_over
    FROM redeemers r
    LEFT JOIN new_minters m ON r.wallet = m.wallet
)

SELECT
    COUNT(*)                                                    AS total_redeemers,
    SUM(rolled_over)                                            AS rolled_over,
    COUNT(*) - SUM(rolled_over)                                 AS exited,
    ROUND(SUM(rolled_over) * 100.0 / COUNT(*), 2)              AS rollover_rate_pct
FROM joined
