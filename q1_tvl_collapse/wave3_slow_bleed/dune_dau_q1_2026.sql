-- ============================================================
-- Pendle DAU: Jan 1 – Apr 6 2026
-- Paste into dune.com → New Query → Run → Export CSV
-- ============================================================
-- Checks whether DAU stabilised at a floor of 350–600
-- (the "genuine retained user base" after mercenary capital exited).
-- Also shows the peak-to-floor decline for the full Oct 2025 – Apr 2026 period.
--
-- Pendle V3 Router (Ethereum): 0x888888888889758F76e7103c6CbF23ABbF58F946
-- ============================================================

WITH daily AS (
    SELECT
        date_trunc('day', block_time)   AS day,
        COUNT(DISTINCT "from")          AS dau,
        COUNT(*)                        AS txn_count
    FROM ethereum.transactions
    WHERE "to" = 0x888888888889758F76e7103c6CbF23ABbF58F946
        AND block_time >= TIMESTAMP '2025-10-01 00:00:00'
        AND block_time <= TIMESTAMP '2026-04-06 23:59:59'
        AND success = true
    GROUP BY 1
)

SELECT
    day,
    dau,
    txn_count,
    ROUND(AVG(dau) OVER (ORDER BY day ROWS BETWEEN 6  PRECEDING AND CURRENT ROW), 1)  AS dau_7d_ma,
    ROUND(AVG(dau) OVER (ORDER BY day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 1)  AS dau_30d_ma,
    MAX(dau) OVER ()                                                                    AS period_peak_dau,
    ROUND(dau * 100.0 / MAX(dau) OVER (), 1)                                           AS pct_of_peak
FROM daily
ORDER BY day
