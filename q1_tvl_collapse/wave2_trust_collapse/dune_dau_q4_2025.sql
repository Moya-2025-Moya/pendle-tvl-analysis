-- ============================================================
-- Pendle DAU: Oct 1 – Dec 31 2025
-- Paste into dune.com → New Query → Run → Export CSV
-- ============================================================
-- Counts unique wallets calling the Pendle V3 Router per day.
-- Validates claim: DAU fell from ~9,900 (early Oct) to 624 (Dec),
-- a 94% contraction.
--
-- Pendle V3 Router (Ethereum): 0x888888888889758F76e7103c6CbF23ABbF58F946
-- ============================================================

SELECT
    date_trunc('day', block_time)                                          AS day,
    COUNT(DISTINCT "from")                                                 AS dau,
    COUNT(*)                                                               AS txn_count,
    ROUND(AVG(COUNT(DISTINCT "from")) OVER (
        ORDER BY date_trunc('day', block_time)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 1)                                                                   AS dau_7d_ma
FROM ethereum.transactions
WHERE "to" = 0x888888888889758F76e7103c6CbF23ABbF58F946
    AND block_time >= TIMESTAMP '2025-10-01 00:00:00'
    AND block_time <  TIMESTAMP '2026-01-01 00:00:00'
    AND success = true
GROUP BY 1
ORDER BY 1
