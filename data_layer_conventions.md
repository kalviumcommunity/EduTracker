# Clean Data Layer Naming Conventions

## Views
- Prefix: `vw_`
- Pattern: `vw_[business_entity]_[metric]`
- Use descriptive names that indicate the business concept and metric focus.
- Examples:
  - `vw_active_customers` - customers with recent activity and revenue metrics
  - `vw_revenue_by_region` - geographic revenue performance by month

## Pre-Aggregated Tables
- Prefix: `agg_`
- Pattern: `agg_[grain]_[subject]`
- Include the aggregation frequency and subject domain.
- Examples:
  - `agg_daily_metrics` - daily performance metrics aggregated for dashboards
  - `agg_customer_revenue` - pre-aggregated customer-level revenue metrics

## Columns in Aggregated Tables
- Always include a grain column such as `aggregation_date`, `aggregation_hour`, or `customer_id`.
- Always include `updated_at` to show when the aggregation was last computed.
- Always include `row_count` to validate the aggregation coverage.

## Applied Names in This Project
- Views created:
  - `vw_active_customers` - follows `vw_[entity]_[metric]`
  - `vw_revenue_by_region` - follows `vw_[metric]_[dimension]`
- Aggregated table created:
  - `agg_daily_metrics` - follows `agg_[grain]_[subject]`

## Benefits
- Clear object type from name alone
- Standardized naming reduces drift in dashboard queries
- Makes it easy for teams to find authoritative data sources
- Improves cross-team consistency for analytics
