-- View: vw_revenue_by_region
-- Purpose: Provide region-level revenue and order volume for sales and operations dashboards.
-- Business question: Which geographic regions are driving revenue and where should we allocate resources?
-- Used by: Sales performance dashboard, executive regional scorecard, operations planning.

CREATE OR REPLACE VIEW vw_revenue_by_region AS
SELECT
    c.country AS region,
    DATE_TRUNC('month', o.order_date)::DATE AS revenue_month,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.order_amount) AS revenue,
    AVG(o.order_amount) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days'
  AND c.deleted_at IS NULL
GROUP BY c.country, DATE_TRUNC('month', o.order_date)
ORDER BY revenue_month DESC, revenue DESC;
