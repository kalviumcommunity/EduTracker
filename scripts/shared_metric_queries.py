import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_DIR = BASE_DIR / 'queries'


def load_query(query_name: str) -> str:
    """Load SQL query text from a file in the shared queries directory."""
    query_path = QUERIES_DIR / f"{query_name}.sql"
    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {query_path}")
    return query_path.read_text(encoding='utf-8')


def execute_query(engine, query_name: str) -> pd.DataFrame:
    """Execute a shared SQL query and return the results in a DataFrame."""
    sql = load_query(query_name)
    return pd.read_sql(sql, engine)


def validate_metrics(mau_df: pd.DataFrame, revenue_df: pd.DataFrame, funnel_df: pd.DataFrame) -> bool:
    """Validate metric computation and sanity-check result frames."""
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue has nulls"
    assert funnel_df.isnull().sum().sum() == 0, "Funnel has nulls"

    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue <= 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion out of range"

    # Check consistency
    assert (revenue_df['order_count'] > 0).all(), "Zero orders"
    assert (revenue_df['monthly_revenue'] > 0).all(), "Zero revenue"

    print("✓ All metrics validated")
    return True


if __name__ == '__main__':
    # Example usage. Replace the database URL with your environment-specific connection string.
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/mydb')
    engine = create_engine(database_url)

    mau = execute_query(engine, 'monthly_active_users')
    revenue = execute_query(engine, 'revenue_by_segment')
    funnel = execute_query(engine, 'conversion_funnel')

    print('Monthly Active Users:')
    print(mau)
    print('\nRevenue by Segment:')
    print(revenue)
    print('\nConversion Funnel:')
    print(funnel)

    validate_metrics(mau, revenue, funnel)
