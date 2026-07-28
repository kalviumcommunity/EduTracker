# SQL Optimization Comparison

## Summary Table
| Metric | Original | Optimized |
|---|---|---|
| Columns Selected | All columns (SELECT *) | Explicit required columns |
| Intermediate Rows | Joined full tables | Filtered smaller dataset before join |
| Filters Applied Before Join | No | Yes |
| Nesting Depth | Multiple nested subqueries | Single layer CTEs |
| Readability Score | Hard to follow | Clear and testable |

## Before / After Queries

### Query 1: SELECT * → explicit columns
- Original inefficiency: `SELECT *` pulls every column, increasing IO and memory usage.
- Optimized change: selected only transaction_id, transaction_date, amount, customer_id, customer_name, country, account_type.
- Improvement: fewer columns mean less data transferred and lower memory pressure.

### Query 2: filter before join
- Original inefficiency: joined `transactions` to `customers` and `products` before reducing rows.
- Optimized change: filter `transactions` first in a CTE, then join only relevant rows.
- Improvement: smaller intermediate result set, reducing join work and memory consumption.

### Query 3: nested subqueries → CTEs
- Original inefficiency: deeply nested subqueries are hard to read and harder to validate.
- Optimized change: split into `recent_transactions`, `customer_with_segment`, and `segment_metrics` CTEs.
- Improvement: each step is independently testable and easier for developers to maintain.

## Specific Improvements Identified
- `SELECT *` removed: less network traffic, smaller row width, fewer unnecessary columns.
- Filters pushed before joins: reduces the number of rows that participate in expensive join operations.
- CTEs improved readability: clear logical stages instead of nested query nesting.

## Best Practices Applied
- Query 1: explicit column projection to minimize I/O.
- Query 2: predicate pushdown before joins to reduce intermediate dataset size.
- Query 3: CTEs for readable and maintainable transformation pipelines.

## Follow-up Notes
- High-cardinality indexes on filtered columns can speed query execution, but they add write and storage overhead.
- Most modern databases can cache CTE results when referenced multiple times; some support explicit materialized CTEs.
- When datasets are still large, additional techniques include partitioning, materialized views, and pre-aggregating data.
