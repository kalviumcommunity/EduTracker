import os
from pathlib import Path
import time
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_DIR = BASE_DIR / 'queries'


def load_query(query_name: str) -> str:
    query_path = QUERIES_DIR / f"{query_name}.sql"
    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {query_path}")
    return query_path.read_text(encoding='utf-8')


def run_query(engine, sql: str, limit_output: bool = False):
    start = time.perf_counter()
    df = pd.read_sql(sql, engine)
    elapsed = time.perf_counter() - start
    print(f"Query executed in {elapsed:.3f}s, rows={len(df)}, cols={df.shape[1]}")
    if limit_output:
        print(df.head())
    return df, elapsed


def compare_query_1(engine):
    original_query = """
SELECT *
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;
"""
    optimized_query = """
SELECT
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.customer_id,
    c.customer_name,
    c.country,
    c.account_type
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;
"""
    print("\n--- Query 1: SELECT * vs explicit columns ---")
    original_df, original_time = run_query(engine, original_query)
    optimized_df, optimized_time = run_query(engine, optimized_query)

    print(f"Original columns: {original_df.shape[1]}")
    print(f"Optimized columns: {optimized_df.shape[1]}")
    print(f"Improvement: {((original_df.shape[1] - optimized_df.shape[1]) / original_df.shape[1]) * 100:.1f}% fewer columns")
    print(f"Time reduction: {(original_time - optimized_time):.3f}s")
    assert optimized_df.shape[0] == original_df.shape[0], "Row counts must match"


def compare_query_2(engine):
    print("\n--- Query 2: Filter before join with CTE ---")
    transactions_count = pd.read_sql('SELECT COUNT(*) AS ct FROM transactions', engine).iloc[0, 0]
    filtered_transactions = pd.read_sql(
        """
SELECT COUNT(*) AS ct
FROM transactions
WHERE transaction_date >= '2024-01-01'
  AND amount > 100
""",
        engine,
    ).iloc[0, 0]

    print(f"Original transactions table: {transactions_count:,} rows")
    print(f"Filtered transactions: {filtered_transactions:,} rows ({(filtered_transactions / transactions_count) * 100:.1f}%)")
    print(f"Reduction factor: {transactions_count / filtered_transactions:.1f}x smaller before join")

    original_query = """
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
"""
    optimized_query = """
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
"""
    original_df, _ = run_query(engine, original_query)
    optimized_df, _ = run_query(engine, optimized_query)
    assert original_df.shape == optimized_df.shape, "Result shapes should match"
    assert original_df.equals(optimized_df), "Result sets should match exactly"


def compare_query_3(engine):
    print("\n--- Query 3: Nested subqueries vs CTEs ---")
    original_query = """
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
"""
    optimized_query = """
WITH recent_transactions AS (
    SELECT transaction_id, amount, customer_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
),
customer_with_segment AS (
    SELECT
        rt.transaction_id,
        rt.amount,
        c.customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id
),
segment_metrics AS (
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
"""
    original_df, _ = run_query(engine, original_query)
    optimized_df, _ = run_query(engine, optimized_query)
    assert original_df.shape[0] == optimized_df.shape[0], "Number of segments should match"
    print(optimized_df)


def build_comparison_document():
    comparison = pd.DataFrame({
        'Metric': [
            'Columns Selected',
            'Intermediate Rows',
            'Filters Applied Before Join',
            'Nesting Depth',
            'Readability Score',
        ],
        'Original': [
            'All columns (SELECT *)',
            'Joined full tables',
            'No',
            'Multiple nested subqueries',
            'Hard to follow',
        ],
        'Optimized': [
            'Explicit required columns',
            'Filtered smaller dataset before join',
            'Yes',
            'Single layer CTEs',
            'Clear and testable',
        ],
    })
    print(comparison.to_string(index=False))

    with open(BASE_DIR / 'sql_optimization_comparison.md', 'w', encoding='utf-8') as f:
        f.write('# SQL Optimization Comparison\n\n')
        f.write(comparison.to_markdown(index=False))


def main():
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/mydb')
    engine = create_engine(database_url)
    compare_query_1(engine)
    compare_query_2(engine)
    compare_query_3(engine)
    build_comparison_document()

if __name__ == '__main__':
    main()
