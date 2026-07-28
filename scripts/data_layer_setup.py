import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_SQL_DIR = BASE_DIR / 'database'


def execute_sql(engine, sql: str):
    with engine.begin() as conn:
        conn.execute(text(sql))


def create_views(engine):
    view_files = [
        DATABASE_SQL_DIR / 'views' / 'vw_active_customers.sql',
        DATABASE_SQL_DIR / 'views' / 'vw_revenue_by_region.sql',
    ]
    for file_path in view_files:
        sql = file_path.read_text(encoding='utf-8')
        execute_sql(engine, sql)
        print(f"Created/updated view: {file_path.name}")


def create_aggregated_table(engine):
    agg_sql = DATABASE_SQL_DIR / 'aggregations' / 'agg_daily_metrics.sql'
    sql = agg_sql.read_text(encoding='utf-8')
    execute_sql(engine, sql)
    print("Created aggregated table: agg_daily_metrics")


def query_clean_data_layer(engine):
    active_customers = pd.read_sql("SELECT * FROM vw_active_customers LIMIT 10", engine)
    revenue_by_region = pd.read_sql("SELECT * FROM vw_revenue_by_region LIMIT 10", engine)
    agg_data = pd.read_sql(
        "SELECT aggregation_date, metric_name, metric_value, updated_at FROM agg_daily_metrics ORDER BY aggregation_date DESC LIMIT 10",
        engine,
    )

    print("View 1 columns:", active_customers.columns.tolist())
    print("View 2 columns:", revenue_by_region.columns.tolist())
    print(f"Aggregated rows: {len(agg_data)}")
    print(agg_data.head())

    top_active = pd.read_sql(
        """
SELECT
    customer_id,
    customer_name,
    revenue_30d,
    days_since_order
FROM vw_active_customers
WHERE days_since_order <= 30
ORDER BY revenue_30d DESC
LIMIT 20
""",
        engine,
    )
    print("\nTop 20 Active Customers (last 30 days):")
    print(top_active)

    custom_metric = pd.read_sql("SELECT * FROM vw_revenue_by_region LIMIT 20", engine)
    print("\nCustom Metric Results:")
    print(custom_metric)

    agg_result = pd.read_sql(
        """
SELECT
    aggregation_date,
    metric_name,
    metric_value
FROM agg_daily_metrics
WHERE aggregation_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY aggregation_date DESC
""",
        engine,
    )
    print("\nDaily Aggregated Metrics (last 30 days):")
    print(agg_result)

    active_by_segment = pd.read_sql(
        """
SELECT
    segment,
    COUNT(*) AS customer_count,
    SUM(revenue_30d) AS total_segment_revenue,
    AVG(revenue_30d) AS avg_customer_revenue
FROM vw_active_customers
GROUP BY segment
ORDER BY total_segment_revenue DESC
""",
        engine,
    )
    print("\nRevenue by Segment:")
    print(active_by_segment)


def main():
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/mydb')
    engine = create_engine(database_url)
    create_views(engine)
    create_aggregated_table(engine)
    query_clean_data_layer(engine)

if __name__ == '__main__':
    main()
