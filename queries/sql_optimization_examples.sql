-- Query 1: Original (Inefficient SELECT *)
SELECT *
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;

-- Query 1: Optimized - Explicit columns only
SELECT
    t.transaction_id,       -- Needed to identify the transaction
    t.transaction_date,      -- Needed to analyze recency and time-based performance
    t.amount,                -- Needed to calculate revenue metrics
    t.customer_id,           -- Needed to join back to customer context
    c.customer_name,         -- Needed for reporting and stakeholder identification
    c.country,               -- Needed to segment by geography
    c.account_type           -- Needed to classify customer tier
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;

-- Query 2: Original (filters after JOIN)
SELECT
    t.transaction_id,
    t.amount,
    c.customer_name,
    p.product_name
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN products p ON t.product_id = p.id
WHERE t.transaction_date >= '2024-01-01'
  AND t.amount > 100
  AND c.country = 'USA'
LIMIT 5000;

-- Query 2: Optimized - filter transactions before joining
WITH filtered_trans AS (
    SELECT
        transaction_id,
        transaction_date,
        amount,
        customer_id,
        product_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
      AND amount > 100
)
SELECT
    ft.transaction_id,
    ft.amount,
    c.customer_name,
    p.product_name
FROM filtered_trans ft
JOIN customers c ON ft.customer_id = c.id
JOIN products p ON ft.product_id = p.id
WHERE c.country = 'USA'
LIMIT 5000;

-- Query 3: Original (nested subqueries)
SELECT customer_segment, AVG(revenue_per_transaction) AS avg_transaction_value
FROM (
    SELECT 
        c.customer_segment,
        AVG(t.amount) AS revenue_per_transaction,
        COUNT(DISTINCT t.transaction_id) AS transaction_count
    FROM (
        SELECT t.transaction_id, t.amount, t.customer_id
        FROM transactions t
        WHERE t.transaction_date >= '2024-01-01'
    ) t
    JOIN customers c ON t.customer_id = c.id
    GROUP BY c.customer_segment
) grouped
ORDER BY avg_transaction_value DESC;

-- Query 3: Optimized with CTEs for readability
WITH recent_transactions AS (
    -- Step 1: filter to the relevant date window
    SELECT transaction_id, amount, customer_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
),
customer_with_segment AS (
    -- Step 2: attach customer segment information to filtered transactions
    SELECT
        rt.transaction_id,
        rt.amount,
        c.customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id
),
segment_metrics AS (
    -- Step 3: calculate segment-level metrics clearly and independently
    SELECT
        customer_segment,
        COUNT(DISTINCT transaction_id) AS transaction_count,
        AVG(amount) AS avg_transaction_value,
        SUM(amount) AS total_revenue
    FROM customer_with_segment
    GROUP BY customer_segment
)
SELECT
    customer_segment,
    avg_transaction_value,
    transaction_count,
    total_revenue
FROM segment_metrics
ORDER BY avg_transaction_value DESC;
