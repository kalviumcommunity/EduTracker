import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title='Business Performance Dashboard', layout='wide')
st.title('Business Performance Dashboard')
st.markdown('A single page summary for Marketing, Sales, and Executive review.')

PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'neutral': '#6c757d',
}

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / 'data' / 'processed'

REVENUE_CSV = DATA_DIR / 'processed_time_series_revenue.csv'
ORDERS_CSV = DATA_DIR / 'merged_customer_orders.csv'
FEATURES_CSV = DATA_DIR / 'engineered_customer_features.csv'


def safe_load_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        st.error(f'Missing expected data file: {path.name}')
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


def format_delta(current: float, previous: float) -> str:
    if previous == 0 or previous is None:
        return '—'
    return f'{(current - previous) / previous:+.1%}'


def calculate_churn_rate(orders_df: pd.DataFrame, end_date: pd.Timestamp, window_days: int = 30) -> float:
    window_end = end_date
    window_start = end_date - pd.Timedelta(days=window_days)
    comparison_start = window_start - pd.Timedelta(days=window_days)

    active_previous = set(
        orders_df[(orders_df['order_date'] >= comparison_start) & (orders_df['order_date'] < window_start)]['customer_id'].unique()
    )
    active_current = set(
        orders_df[(orders_df['order_date'] >= window_start) & (orders_df['order_date'] <= window_end)]['customer_id'].unique()
    )

    if not active_previous:
        return 0.0
    churned = len(active_previous - active_current)
    return churned / len(active_previous)


def calculate_payment_success_rate(orders_df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
    window_df = orders_df[(orders_df['order_date'] >= start_date) & (orders_df['order_date'] <= end_date)]
    if window_df.empty:
        return 0.0
    successful = window_df['payment_status'].isin(['Paid', 'SUCCESS']).sum()
    return successful / len(window_df)


def get_last_window(df: pd.DataFrame, date_col: str, value_col: str, end_date: pd.Timestamp, window_days: int) -> float:
    mask = (df[date_col] > end_date - pd.Timedelta(days=window_days)) & (df[date_col] <= end_date)
    return float(df.loc[mask, value_col].sum())


revenue_df = safe_load_csv(REVENUE_CSV, parse_dates=['date'])
orders_df = safe_load_csv(ORDERS_CSV, parse_dates=['order_date'])
features_df = safe_load_csv(FEATURES_CSV)

if not revenue_df.empty and not orders_df.empty:
    revenue_df = revenue_df.sort_values('date')
    latest_date = revenue_df['date'].max()
    previous_date = revenue_df['date'].iloc[-2] if len(revenue_df) > 1 else latest_date

    revenue_current = get_last_window(revenue_df, 'date', 'revenue', latest_date, window_days=7)
    revenue_previous = get_last_window(revenue_df, 'date', 'revenue', latest_date - pd.Timedelta(days=7), window_days=7)

    orders_current = get_last_window(revenue_df, 'date', 'orders', latest_date, window_days=7)
    orders_previous = get_last_window(revenue_df, 'date', 'orders', latest_date - pd.Timedelta(days=7), window_days=7)

    active_customers_current = int(revenue_df.loc[revenue_df['date'] == latest_date, 'customers'].iat[0])
    active_customers_previous = int(revenue_df.loc[revenue_df['date'] == previous_date, 'customers'].iat[0])

    avg_order_value_current = revenue_current / orders_current if orders_current else 0.0
    avg_order_value_previous = revenue_previous / orders_previous if orders_previous else 0.0

    churn_rate_current = calculate_churn_rate(orders_df, latest_date, window_days=30)
    churn_rate_previous = calculate_churn_rate(orders_df, latest_date - pd.Timedelta(days=30), window_days=30)

    payment_success_current = calculate_payment_success_rate(orders_df, latest_date - pd.Timedelta(days=30), latest_date)
    payment_success_previous = calculate_payment_success_rate(orders_df, latest_date - pd.Timedelta(days=60), latest_date - pd.Timedelta(days=31))

    revenue_delta = format_delta(revenue_current, revenue_previous)
    active_customers_delta = format_delta(active_customers_current, active_customers_previous)
    aov_delta = format_delta(avg_order_value_current, avg_order_value_previous)
    churn_delta = format_delta(churn_rate_current, churn_rate_previous)
    payment_success_delta = format_delta(payment_success_current, payment_success_previous)

    churn_label = f'{churn_rate_current:.1%}'
    payment_success_label = f'{payment_success_current:.1%}'

else:
    latest_date = pd.Timestamp.now()
    revenue_current = revenue_previous = 0.0
    orders_current = orders_previous = 0
    active_customers_current = active_customers_previous = 0
    avg_order_value_current = avg_order_value_previous = 0.0
    churn_rate_current = churn_rate_previous = 0.0
    payment_success_current = payment_success_previous = 0.0
    revenue_delta = active_customers_delta = aov_delta = churn_delta = payment_success_delta = '—'
    churn_label = payment_success_label = '—'

# Level 1: KPI Summary Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        label='Revenue (7d)',
        value=f'${revenue_current:,.0f}',
        delta=revenue_delta,
    )
with col2:
    st.metric(
        label='Active Customers',
        value=f'{active_customers_current:,}',
        delta=active_customers_delta,
    )
with col3:
    st.metric(
        label='Avg Order Value',
        value=f'${avg_order_value_current:,.2f}',
        delta=aov_delta,
    )
with col4:
    st.metric(
        label='Churn Rate',
        value=churn_label,
        delta=churn_delta,
        delta_color='inverse',
    )
with col5:
    st.metric(
        label='Payment Success Rate',
        value=payment_success_label,
        delta=payment_success_delta,
    )

st.divider()

# Level 2: Trend Section
st.header('Trends and Momentum')

revenue_plot = revenue_df.copy()
revenue_plot = revenue_plot.set_index('date').last('90D')
months = revenue_plot.index

customer_trend = revenue_plot['customers']

monthly_churn = []
monthly_idx = revenue_df.set_index('date').resample('M').last().index
for month_end in monthly_idx:
    churn_counts = calculate_churn_rate(orders_df, month_end, window_days=30) * len(
        orders_df[(orders_df['order_date'] >= month_end - pd.Timedelta(days=60)) & (orders_df['order_date'] < month_end - pd.Timedelta(days=30))]['customer_id'].unique()
    )
    monthly_churn.append(churn_counts)

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(months, revenue_plot['revenue'] / 1_000_000, marker='o', linewidth=2, color=PALETTE['primary'], label='Revenue')
ax1.axhline(y=5.0, color=PALETTE['success'], linestyle='--', linewidth=1.5, label='Target: $5M')
ax1.set_title('Revenue Trend (Last 90 Days)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Date', fontsize=11)
ax1.set_ylabel('Revenue ($M)', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.legend()
fig1.autofmt_xdate()

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(months, customer_trend, marker='o', linewidth=2, color=PALETTE['primary'], label='Active Customers')
if len(monthly_idx) >= len(monthly_churn):
    churn_months = monthly_idx[-len(monthly_churn):]
    ax2.plot(churn_months, monthly_churn, marker='s', linewidth=2, color=PALETTE['danger'], label='Churned Customers')
ax2.set_title('Customer Growth vs Churn', fontsize=14, fontweight='bold')
ax2.set_xlabel('Date', fontsize=11)
ax2.set_ylabel('Customer Count', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.legend()
fig2.autofmt_xdate()

campaign_engagement = revenue_plot['customers'].rolling(7).mean().fillna(method='bfill') / revenue_plot['customers'].max() * 100
fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(months, campaign_engagement, marker='o', linewidth=2, color=PALETTE['secondary'], label='Relative Engagement')
ax3.axhline(y=50, color=PALETTE['success'], linestyle='--', linewidth=1.5, label='Healthy Range')
ax3.set_title('Relative Engagement Trend', fontsize=14, fontweight='bold')
ax3.set_xlabel('Date', fontsize=11)
ax3.set_ylabel('Engagement Index', fontsize=11)
ax3.grid(True, alpha=0.3)
ax3.legend()
fig3.autofmt_xdate()

col1, col2 = st.columns(2)
with col1:
    st.pyplot(fig1)
with col2:
    st.pyplot(fig2)
st.pyplot(fig3)

st.divider()

# Level 3: Segment Section
st.header('Segment Performance')
segment_revenue = orders_df.groupby('segment')['order_amount'].sum().sort_values(ascending=False).head(4)
region_revenue = features_df.groupby('customer_region')['total_spent'].sum().sort_values(ascending=False).head(4)

fig4, ax4 = plt.subplots(figsize=(10, 4))
bars = ax4.barh(segment_revenue.index, segment_revenue.values, color=[PALETTE['primary'], PALETTE['secondary'], PALETTE['success'], PALETTE['danger']][: len(segment_revenue)])
ax4.set_xlabel('Revenue ($)', fontsize=11)
ax4.set_title('Revenue by Customer Segment', fontsize=14, fontweight='bold')
for bar, val in zip(bars, segment_revenue.values):
    ax4.text(bar.get_width() + 0.01 * max(segment_revenue.values), bar.get_y() + bar.get_height() / 2, f'${val:,.0f}', va='center', fontsize=10)

fig5, ax5 = plt.subplots(figsize=(10, 4))
bars2 = ax5.bar(region_revenue.index, region_revenue.values, color=[PALETTE['primary'], PALETTE['secondary'], PALETTE['success'], PALETTE['danger']][: len(region_revenue)])
ax5.set_ylabel('Total Spent ($)', fontsize=11)
ax5.set_title('Total Customer Spend by Region', fontsize=14, fontweight='bold')
for bar, val in zip(bars2, region_revenue.values):
    ax5.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01 * max(region_revenue.values), f'${val:,.0f}', ha='center', fontsize=10)

col1, col2 = st.columns(2)
with col1:
    st.pyplot(fig4)
with col2:
    st.pyplot(fig5)

st.divider()

# Level 4: Detailed Data Explorer
st.header('Detailed Data Explorer')
st.sidebar.header('Filters')
segment_options = ['All'] + sorted(orders_df['segment'].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox('Customer Segment', segment_options)
start_date = revenue_df['date'].min().date()
end_date = revenue_df['date'].max().date()
selected_range = st.sidebar.date_input('Date Range', value=(start_date, end_date))

filtered_orders = orders_df.copy()
if selected_segment != 'All':
    filtered_orders = filtered_orders[filtered_orders['segment'] == selected_segment]
if isinstance(selected_range, tuple) and len(selected_range) == 2:
    start_range, end_range = selected_range
    filtered_orders = filtered_orders[
        (filtered_orders['order_date'].dt.date >= start_range) &
        (filtered_orders['order_date'].dt.date <= end_range)
    ]

st.write(f'Showing {len(filtered_orders):,} records from orders data')
st.dataframe(filtered_orders[['customer_id', 'segment', 'order_date', 'order_amount', 'payment_status']].sort_values('order_date', ascending=False).reset_index(drop=True))

csv = filtered_orders.to_csv(index=False).encode('utf-8')
st.download_button(
    label='Download CSV',
    data=csv,
    file_name='filtered_orders.csv',
    mime='text/csv',
)
