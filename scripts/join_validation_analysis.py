import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_DIR = BASE_DIR / 'queries'


def load_query(query_name: str) -> str:
    query_path = QUERIES_DIR / f"{query_name}.sql"
    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {query_path}")
    return query_path.read_text(encoding='utf-8')


def execute_query(engine, query_name: str) -> pd.DataFrame:
    sql = load_query(query_name)
    return pd.read_sql(sql, engine)


def validate_join_counts(engine):
    customers_count = pd.read_sql('SELECT COUNT(*) AS ct FROM customers', engine).iloc[0, 0]
    orders_count = pd.read_sql('SELECT COUNT(*) AS ct FROM orders', engine).iloc[0, 0]

    left_join_df = execute_query(engine, 'join_validation_examples')
    print(f"Customers before join: {customers_count}")
    print(f"Rows after LEFT JOIN aggregation query: {len(left_join_df)}")

    if len(left_join_df) >= customers_count:
        print("✓ LEFT JOIN result set is larger or equal, as expected when customers have multiple orders")
    else:
        raise AssertionError("LEFT JOIN result set should not be smaller than customer count")

    no_orders_df = pd.read_sql(
        "SELECT c.customer_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL",
        engine,
    )
    orphaned_df = pd.read_sql(
        "SELECT o.order_id FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL",
        engine,
    )

    print(f"Customers without orders: {len(no_orders_df)} ({(len(no_orders_df) / customers_count) * 100:.1f}%)")
    print(f"Orphaned orders: {len(orphaned_df)}")
    if len(orphaned_df) > 0:
        print("⚠️ Orphaned orders found - investigate customer_id mismatches")

    inner_count = pd.read_sql('SELECT COUNT(*) AS ct FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id', engine).iloc[0, 0]
    left_count = pd.read_sql('SELECT COUNT(*) AS ct FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id', engine).iloc[0, 0]
    full_count = pd.read_sql('SELECT COUNT(*) AS ct FROM customers c FULL OUTER JOIN orders o ON c.customer_id = o.customer_id', engine).iloc[0, 0]

    print(f"INNER JOIN rows: {inner_count}")
    print(f"LEFT JOIN rows: {left_count}")
    print(f"FULL OUTER JOIN rows: {full_count}")

    assert left_count >= inner_count, "LEFT join should be >= INNER join"
    assert full_count >= max(left_count, customers_count), "FULL OUTER join should be >= LEFT join and include all customers"

    # Multi-table validation
    multi_df = pd.read_sql(
        "SELECT c.customer_id, c.customer_type, o.order_id, o.order_date, oi.product_id, p.product_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS line_total "
        "FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id "
        "LEFT JOIN order_items oi ON o.order_id = oi.order_id "
        "LEFT JOIN products p ON oi.product_id = p.product_id "
        "WHERE c.customer_type = 'Enterprise'",
        engine,
    )

    expected_total = pd.read_sql("SELECT SUM(quantity * unit_price) AS total FROM order_items", engine).iloc[0, 0]
    line_total_sum = multi_df['line_total'].sum()

    print(f"Order items expected total: {expected_total}")
    print(f"Joined line_total sum: {line_total_sum}")
    assert abs(line_total_sum - expected_total) < 0.01, "Duplication detected in multi-table join aggregation"
    print("✓ Multi-table join validated - no unexpected duplication")

    join_documentation = '''
JOIN STRATEGY DOCUMENTATION

Table: customers (1000 rows, PK: customer_id)
Table: orders (5000 rows, FK: customer_id)
Table: order_items (8000 rows, FK: order_id)
Table: products (500 rows, PK: product_id)

Decision 1: customers LEFT JOIN orders
- Purpose: Get all customers with their order history
- Row count change: 1000 → 5000+ (customers repeated for multiple orders)
- Unmatched: customers with no orders are retained and show NULL order fields
- Business use: Customer lifetime value, segmentation, retention analysis

Decision 2: orders LEFT JOIN order_items
- Purpose: Get detailed order line-item data for each order
- Row count change: 5000 → 8000 (orders with multiple items repeat order rows)
- Unmatched: should be minimal or none if every order has at least one item
- Business use: product-level revenue, margin, inventory analysis

Decision 3: Full 3-table join
- Purpose: Build complete contextual view: customer → order → item → product
- Row count: 5000 → 8000 (base orders multiplied by order items)
- Risk: aggregate at order/item level to avoid double-counting totals
- Solution: use order-level aggregation or DISTINCT product/order identifiers when summarizing

Validation: row counts were checked before and after joins, orphaned records were identified, and multi-table aggregation was verified for duplication.
'''
    print(join_documentation)
    return True


if __name__ == '__main__':
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/mydb')
    engine = create_engine(database_url)
    validate_join_counts(engine)
