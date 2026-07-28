-- Task 1: WHERE Filtering (row-level filters applied before GROUP BY)
-- This removes invalid or incomplete transactions before any aggregation.
SELECT
    customer_id,
    SUM(amount) AS annual_revenue,
    COUNT(*) AS transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'          -- Filter date range first
  AND amount > 0                                      -- Remove refunds and negative adjustments
  AND transaction_status = 'completed'                -- Include only completed/valid purchases
  AND customer_type = 'Enterprise'                    -- Scope to Enterprise customers
GROUP BY customer_id
ORDER BY annual_revenue DESC;

-- Task 2: GROUP BY and Aggregation (multiple dimensions with 3+ aggregates)
-- WHERE filters are applied before grouping, ensuring the aggregated groups only include valid rows.
SELECT
    c.customer_type,
    DATE_TRUNC('month', t.transaction_date)::DATE AS month,
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS monthly_revenue,
    AVG(t.amount) AS avg_transaction
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'        -- Date filter before grouping
  AND t.amount > 0                                    -- Only positive revenue rows
  AND t.transaction_status = 'completed'              -- Valid transactions only
GROUP BY c.customer_type, DATE_TRUNC('month', t.transaction_date)
ORDER BY month DESC, monthly_revenue DESC;

-- Task 3: HAVING Filtering (group-level filters after aggregation)
-- Use HAVING to keep only customer groups meeting business thresholds.
SELECT
    customer_id,
    COUNT(*) AS transaction_count,
    SUM(amount) AS annual_revenue
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'          -- Row-level filter before GROUP BY
  AND amount > 0
  AND transaction_status = 'completed'
GROUP BY customer_id
HAVING SUM(amount) > 10000                             -- Group threshold: > $10k annual spend
   AND COUNT(*) >= 5                                   -- Group threshold: at least 5 purchases
ORDER BY annual_revenue DESC;

-- Task 4: WHERE + HAVING Combined (quality filters plus business thresholds)
-- WHERE removes bad rows, HAVING removes groups that do not meet the aggregated business rules.
SELECT
    c.customer_type,
    COUNT(DISTINCT t.customer_id) AS segment_customers,
    SUM(t.amount) AS segment_revenue,
    ROUND(AVG(t.amount), 2) AS avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'        -- WHERE: time window filter
  AND t.transaction_status = 'completed'              -- WHERE: data quality filter
  AND t.amount > 0                                    -- WHERE: valid revenue only
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100          -- HAVING: only large segments
   AND SUM(t.amount) > 100000                         -- HAVING: business revenue threshold
ORDER BY segment_revenue DESC;

-- Task 5: ORDER BY Ranking (top performers with window functions)
-- ORDER BY sorts final results; RANK() computes relative position by revenue.
SELECT
    c.customer_type,
    c.industry,
    COUNT(DISTINCT t.customer_id) AS customers,
    SUM(t.amount) AS total_revenue,
    ROUND(AVG(t.amount), 2) AS avg_order,
    RANK() OVER (ORDER BY SUM(t.amount) DESC) AS revenue_rank
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'        -- WHERE: applied before aggregation
  AND t.amount > 0
  AND t.transaction_status = 'completed'
GROUP BY c.customer_type, c.industry
HAVING COUNT(DISTINCT t.customer_id) >= 10            -- HAVING: require at least 10 customers per segment
ORDER BY total_revenue DESC
LIMIT 20;                                             -- Top 20 segments

-- Bonus: Enterprise customers with > $10k annual spending
-- Use WHERE for row-level quality and enterprise-only filtering,
-- then HAVING for the annual revenue threshold after aggregation.
SELECT
    customer_id,
    SUM(amount) AS annual_revenue,
    COUNT(*) AS transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'
  AND amount > 0
  AND transaction_status = 'completed'
  AND customer_type = 'Enterprise'                    -- Row-level filter for Enterprise customers
GROUP BY customer_id
HAVING SUM(amount) > 10000                             -- Group-level filter for annual spend
ORDER BY annual_revenue DESC;
