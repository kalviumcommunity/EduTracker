import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = Path(__file__).resolve().parent.parent


def get_date_ranges(reference_date: date):
    """Return start/end dates for current and previous calendar months."""
    first_day_this_month = reference_date.replace(day=1)
    last_day_previous_month = first_day_this_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    return (
        first_day_previous_month,
        last_day_previous_month,
        first_day_this_month,
        reference_date,
    )


def calculate_churn_py(orders_df: pd.DataFrame, reference_date: date) -> int:
    """Calculate monthly churn in Python using explicit month boundaries."""
    orders_df = orders_df.copy()
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date']).dt.date

    prev_month_start, prev_month_end, curr_month_start, _ = get_date_ranges(reference_date)

    prev_month_customers = orders_df[
        (orders_df['order_date'] >= prev_month_start)
        & (orders_df['order_date'] <= prev_month_end)
        & (orders_df['order_amount'] > 0)
    ]['customer_id'].dropna().unique()

    current_month_customers = orders_df[
        (orders_df['order_date'] >= curr_month_start)
        & (orders_df['order_date'] <= reference_date)
    ]['customer_id'].dropna().unique()

    churned_customers = set(prev_month_customers) - set(current_month_customers)
    return len(churned_customers)


def load_dataframes(engine):
    logins_df = pd.read_sql('SELECT * FROM logins', engine)
    orders_df = pd.read_sql('SELECT * FROM orders', engine)
    return logins_df, orders_df


def compare_metrics(engine):
    current_date = date.today()
    first_day_previous_month, last_day_previous_month, first_day_current_month, _ = get_date_ranges(current_date)

    sql_query_1 = """
SELECT COUNT(DISTINCT user_id) AS active_users
FROM logins
WHERE login_date >= CURRENT_DATE - INTERVAL '30 days';
"""

    sql_query_2 = """
SELECT AVG(order_amount) AS aov
FROM orders;
"""

    sql_query_3 = """
SELECT COUNT(DISTINCT c1.customer_id) AS churned_customers
FROM (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE MONTH(order_date) = MONTH(CURRENT_DATE) - 1
      AND order_amount > 0
) c1
LEFT JOIN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE MONTH(order_date) = MONTH(CURRENT_DATE)
) c2 ON c1.customer_id = c2.customer_id
WHERE c2.customer_id IS NULL;
"""

    logins_df, orders_df = load_dataframes(engine)
    logins_df['login_date'] = pd.to_datetime(logins_df['login_date']).dt.date
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date']).dt.date

    sql_metric1 = pd.read_sql(sql_query_1, engine).iloc[0, 0]
    sql_metric2 = pd.read_sql(sql_query_2, engine).iloc[0, 0]
    sql_metric3 = pd.read_sql(sql_query_3, engine).iloc[0, 0]

    py_metric1 = logins_df[logins_df['login_date'] >= current_date - timedelta(days=30)]['user_id'].nunique()
    py_metric2 = orders_df['order_amount'].mean()
    py_metric3 = calculate_churn_py(orders_df, current_date)

    comparison = pd.DataFrame({
        'Metric': ['Active Users', 'AOV', 'Churn'],
        'SQL': [sql_metric1, sql_metric2, sql_metric3],
        'Python': [py_metric1, py_metric2, py_metric3],
    })
    comparison['Difference'] = (comparison['SQL'] - comparison['Python']).abs()
    comparison['Percent_Difference'] = (
        comparison['Difference'] / comparison['SQL'].abs() * 100
    ).round(2)

    print('Metrics Comparison:')
    print(comparison.to_string(index=False))

    print('\nDiscrepancies found:')
    for _, row in comparison.iterrows():
        if row['Percent_Difference'] > 0.1:
            print(f"  ⚠️ {row['Metric']}: {row['Percent_Difference']}% difference")
        else:
            print(f"  ✓ {row['Metric']}: Match within tolerance")

    return comparison


def validate_metrics(engine, tolerance_pct: float = 0.1) -> pd.DataFrame:
    """Validate SQL and Python metric alignment and report pass/fail status."""
    current_date = date.today()
    logins_df, orders_df = load_dataframes(engine)
    logins_df['login_date'] = pd.to_datetime(logins_df['login_date']).dt.date
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date']).dt.date

    metrics = {
        'active_users': {
            'sql': """
SELECT COUNT(DISTINCT user_id) AS value
FROM logins
WHERE login_date >= CURRENT_DATE - INTERVAL '30 days';
""",
            'python': lambda: logins_df[logins_df['login_date'] >= current_date - timedelta(days=30)]['user_id'].nunique(),
            'tolerance': 0,
        },
        'aov': {
            'sql': """
SELECT AVG(order_amount) AS value
FROM orders;
""",
            'python': lambda: orders_df['order_amount'].mean(),
            'tolerance': 0.1,
        },
        'churn': {
            'sql': """
SELECT COUNT(DISTINCT c1.customer_id) AS value
FROM (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE MONTH(order_date) = MONTH(CURRENT_DATE) - 1
      AND order_amount > 0
) c1
LEFT JOIN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE MONTH(order_date) = MONTH(CURRENT_DATE)
) c2 ON c1.customer_id = c2.customer_id
WHERE c2.customer_id IS NULL;
""",
            'python': lambda: calculate_churn_py(orders_df, current_date),
            'tolerance': 0,
        },
    }

    validation_report = []
    for metric_name, metric_def in metrics.items():
        sql_result = pd.read_sql(metric_def['sql'], engine).iloc[0, 0]
        py_result = metric_def['python']()
        difference = abs(sql_result - py_result)
        pct_diff = (difference / abs(sql_result) * 100) if sql_result != 0 else 0
        match = pct_diff <= metric_def['tolerance']
        validation_report.append({
            'Metric': metric_name,
            'SQL': sql_result,
            'Python': py_result,
            'Difference': difference,
            'Pct_Difference': round(pct_diff, 3),
            'Tolerance': metric_def['tolerance'],
            'Status': 'PASS' if match else 'FAIL',
            'Timestamp': datetime.now(),
        })

    report_df = pd.DataFrame(validation_report)
    report_df.to_csv(BASE_DIR / 'validation_report.csv', index=False)
    print('\nValidation report saved to validation_report.csv')
    return report_df


def main():
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/mydb')
    engine = create_engine(database_url)
    try:
        compare_metrics(engine)
        report = validate_metrics(engine)
        print('\nValidation Report:')
        print(report.to_string(index=False))
    except SQLAlchemyError as exc:
        print('Database error:', exc)


if __name__ == '__main__':
    main()
