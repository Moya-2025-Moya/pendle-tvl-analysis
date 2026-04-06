-- ============================================================
-- YT / PT Volume Ratio: Sep 2025 – Apr 2026 (weekly)
-- Paste into dune.com → New Query → Run → Export CSV
-- ============================================================
-- Measures the ratio of speculative (YT) vs fixed-income (PT)
-- activity by comparing weekly ERC20 transfer volume.
-- A falling YT/PT ratio = speculative users leaving,
-- fixed-income users becoming proportionally dominant.
--
-- Method: sum CAST(value/1e18) for transfers between non-zero
-- addresses (i.e., actual trading/LP movements, not mints/burns).
--
-- PT tokens (Sep-25, Nov-27, Feb-5 maturities):
--   0x9F56094C450763769BA0EA9Fe2876070c0fD5F77  PT-sUSDE-25SEP2025
--   0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a  PT-USDe-25SEP2025
--   0xe6A934089BBEe34F832060CE98848359883749B3  PT-sUSDE-27NOV2025
--   0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7  PT-USDe-27NOV2025
--   0xE8483517077afa11A9B07f849cee2552f040d7b2  PT-sUSDE-5FEB2026
--   0x1F84a51296691320478c98b8d77f2Bbd17D34350  PT-USDe-5FEB2026
--
-- YT tokens (corresponding):
--   0x029d6247ADb0A57138c62E3019C92d3dfC9c1840  YT-sUSDE-25SEP2025
--   0x48bbbEdc4d2491cc08915D7a5c7cc8A8EdF165da  YT-USDe-25SEP2025
--   0x28E626b560F1FaaC01544770425e2De8FD179c79  YT-sUSDE-27NOV2025
--   0x99C92D4Da7a81c7698EF33a39D7538d0f92623f7  YT-USDe-27NOV2025
--   0xe36c6c271779C080Ba2e68E1E68410291a1b3F7A  YT-sUSDE-5FEB2026
--   0x5a62AE8118536CF2De315E2c42f9Af035d8129f2  YT-USDe-5FEB2026
-- ============================================================

WITH transfers AS (
    SELECT
        date_trunc('week', evt_block_time)                              AS week,
        CASE
            WHEN contract_address IN (
                0x9F56094C450763769BA0EA9Fe2876070c0fD5F77,
                0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a,
                0xe6A934089BBEe34F832060CE98848359883749B3,
                0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7,
                0xE8483517077afa11A9B07f849cee2552f040d7b2,
                0x1F84a51296691320478c98b8d77f2Bbd17D34350
            ) THEN 'PT'
            ELSE 'YT'
        END                                                              AS token_type,
        CAST(value AS DOUBLE) / 1e18                                    AS amount
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address IN (
        -- PT tokens
        0x9F56094C450763769BA0EA9Fe2876070c0fD5F77,
        0xBC6736d346a5eBC0dEbc997397912CD9b8FAe10a,
        0xe6A934089BBEe34F832060CE98848359883749B3,
        0x62C6E813b9589C3631Ba0Cdb013acdB8544038B7,
        0xE8483517077afa11A9B07f849cee2552f040d7b2,
        0x1F84a51296691320478c98b8d77f2Bbd17D34350,
        -- YT tokens
        0x029d6247ADb0A57138c62E3019C92d3dfC9c1840,
        0x48bbbEdc4d2491cc08915D7a5c7cc8A8EdF165da,
        0x28E626b560F1FaaC01544770425e2De8FD179c79,
        0x99C92D4Da7a81c7698EF33a39D7538d0f92623f7,
        0xe36c6c271779C080Ba2e68E1E68410291a1b3F7A,
        0x5a62AE8118536CF2De315E2c42f9Af035d8129f2
    )
    AND "from" != 0x0000000000000000000000000000000000000000
    AND "to"   != 0x0000000000000000000000000000000000000000
    AND evt_block_time >= TIMESTAMP '2025-09-01 00:00:00'
    AND evt_block_time <  TIMESTAMP '2026-04-07 00:00:00'
),

weekly AS (
    SELECT
        week,
        SUM(CASE WHEN token_type = 'PT' THEN amount ELSE 0 END)  AS pt_volume,
        SUM(CASE WHEN token_type = 'YT' THEN amount ELSE 0 END)  AS yt_volume
    FROM transfers
    GROUP BY 1
)

SELECT
    week,
    ROUND(pt_volume, 0)                                                            AS pt_volume,
    ROUND(yt_volume, 0)                                                            AS yt_volume,
    ROUND(yt_volume / NULLIF(pt_volume, 0), 4)                                     AS yt_pt_ratio,
    ROUND(yt_volume * 100.0 / NULLIF(yt_volume + pt_volume, 0), 2)                AS yt_pct_of_total
FROM weekly
ORDER BY week
