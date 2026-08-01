-- View: vw_active_customers
-- Purpose: Identify customers with recent purchasing activity in the last 30 days.
-- Business question: Which customers are active and how much revenue have they generated recently?
-- Used by: Sales dashboard, customer success engagement reports, and revenue health monitoring.

CREATE OR REPLACE VIEW vw_active_customers AS
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) AS order_count_30d,
    COALESCE(SUM(o.order_amount), 0) AS revenue_30d,
    MAX(o.order_date) AS last_order_date,
    DATE_PART('day', CURRENT_DATE - MAX(o.order_date)) AS days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
    AND o.order_date >= CURRENT_DATE - INTERVAL '30 days'
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment;
