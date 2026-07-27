import pandas as pd  # type: ignore # pyrefly: ignore [missing-import]
import numpy as np  # type: ignore # pyrefly: ignore [missing-import]

def calculate_mau(df: pd.DataFrame, days: int = 30) -> int:
    """
    Monthly Active Users (MAU): distinct customers with at least one transaction in last N days.
    """
    if 'transaction_date' not in df.columns or 'customer_id' not in df.columns:
        raise ValueError("DataFrame must contain 'transaction_date' and 'customer_id' columns.")
    
    # Ensure datetime format
    dates = pd.to_datetime(df['transaction_date'])
    max_date = dates.max() if not dates.empty else pd.Timestamp.now()
    cutoff = max_date - pd.Timedelta(days=days)
    
    active_df = df[pd.to_datetime(df['transaction_date']) >= cutoff]
    return int(active_df['customer_id'].nunique())

def calculate_revenue_per_customer(df: pd.DataFrame) -> float:
    """
    Average revenue per unique active customer.
    """
    if 'amount' not in df.columns or 'customer_id' not in df.columns:
        raise ValueError("DataFrame must contain 'amount' and 'customer_id' columns.")
    
    # Filter completed transactions if payment_status column exists
    filtered_df = df[df['payment_status'] == 'SUCCESS'] if 'payment_status' in df.columns else df
    unique_customers = filtered_df['customer_id'].nunique()
    if unique_customers == 0:
        return 0.0
    
    total_rev = filtered_df['amount'].sum()
    return float(total_rev / unique_customers)

def calculate_churn_rate(df: pd.DataFrame, period_days: int = 30) -> float:
    """
    Customers who had activity in Period 1 but no transactions in Period 2.
    """
    if 'transaction_date' not in df.columns or 'customer_id' not in df.columns:
        raise ValueError("DataFrame must contain 'transaction_date' and 'customer_id' columns.")
    
    dates = pd.to_datetime(df['transaction_date'])
    max_date = dates.max() if not dates.empty else pd.Timestamp.now()
    
    period_2_end = max_date
    period_2_start = max_date - pd.Timedelta(days=period_days)
    period_1_end = period_2_start
    period_1_start = period_1_end - pd.Timedelta(days=period_days)
    
    df_with_dates = df.copy()
    df_with_dates['dt'] = pd.to_datetime(df_with_dates['transaction_date'])
    
    active_p1 = df_with_dates[(df_with_dates['dt'] >= period_1_start) & (df_with_dates['dt'] < period_1_end)]['customer_id'].unique()
    active_p2 = df_with_dates[(df_with_dates['dt'] >= period_2_start) & (df_with_dates['dt'] <= period_2_end)]['customer_id'].unique()
    
    if len(active_p1) == 0:
        return 0.0
    
    churned_count = len([c for c in active_p1 if c not in set(active_p2)])
    return float(churned_count / len(active_p1))

def calculate_payment_success_rate(df: pd.DataFrame) -> float:
    """
    Proportion of payment attempts that were completed successfully.
    """
    if 'payment_status' not in df.columns:
        # Default to 1.0 if not present
        return 1.0
    
    total_attempts = len(df)
    if total_attempts == 0:
        return 0.0
    
    successful_attempts = len(df[df['payment_status'] == 'SUCCESS'])
    return float(successful_attempts / total_attempts)

def calculate_customer_acquisition_cost(total_marketing_spend: float, new_customers_acquired: int) -> float:
    """
    Customer Acquisition Cost (CAC) = Total Marketing Spend / New Customers Acquired.
    """
    if new_customers_acquired <= 0:
        return 0.0
    return float(total_marketing_spend / new_customers_acquired)

def calculate_total_revenue(df: pd.DataFrame) -> float:
    """
    Total revenue accumulated across successful transactions.
    """
    if 'amount' not in df.columns:
        return 0.0
    filtered_df = df[df['payment_status'] == 'SUCCESS'] if 'payment_status' in df.columns else df
    return float(filtered_df['amount'].sum())

def format_kpi_value(kpi_name: str, value: float) -> str:
    """
    Formats a numeric KPI value into human-readable string based on its nature.
    """
    kpi_lower = kpi_name.lower()
    if 'rate' in kpi_lower or 'churn' in kpi_lower or 'percentage' in kpi_lower:
        return f"{value:.1%}"
    elif 'revenue' in kpi_lower or 'rpc' in kpi_lower or 'cost' in kpi_lower or 'cac' in kpi_lower or 'amount' in kpi_lower:
        return f"${value:,.2f}"
    elif 'mau' in kpi_lower or 'count' in kpi_lower or 'users' in kpi_lower:
        return f"{int(value):,} users"
    else:
        return f"{value:,.2f}"
