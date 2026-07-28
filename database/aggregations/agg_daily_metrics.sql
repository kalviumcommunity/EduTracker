-- Table: agg_daily_metrics
-- Purpose: Store pre-aggregated daily metrics for fast dashboard queries.
-- Business question: What are the daily revenue and order volumes, and when was the aggregation last refreshed?
-- Used by: high-performance dashboards and trend reports.

CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP
);
