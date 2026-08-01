# Churn Metric Discrepancy Analysis

## Observed Difference
- SQL churn: 5.2%
- Python churn: 6.8%

## Investigation
- Compared SQL and Python definitions of month boundaries.
- Hand-checked sample orders at month boundaries.
- Discovered that the SQL query used `MONTH(order_date) = MONTH(CURRENT_DATE) - 1` and `MONTH(order_date) = MONTH(CURRENT_DATE)`.
- This approach fails across year boundaries and ignores year context.
- Example: December and January both have `MONTH() = 1` comparisons in January, causing incorrect inclusion/exclusion.

## Root Cause
- SQL used month-only comparison without year context.
- Python used explicit date ranges for the previous month and current month.
- The mismatch created false negatives/positives in churn calculation.

## Fix Applied
- Updated SQL to use explicit date ranges instead of `MONTH()` only.
- Example corrected SQL condition:
  - `order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')`
  - `order_date < DATE_TRUNC('month', CURRENT_DATE)`
- This ensures the previous month is defined precisely.

## Validation
- After fix, SQL and Python churn counts matched on the audited dataset.
- The comparison script now reports PASS for churn when both results are aligned.

## Lessons Learned
- Always include year context when filtering by month.
- For date-range metrics, use explicit bounds rather than function-based month comparisons.
- Automated validation scripts help catch drift, but hand verification is essential to diagnose root cause.
