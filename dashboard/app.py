import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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

# Level 1: KPI Summary Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label='Revenue', value='$5.2M', delta='+12.5%')
with col2:
    st.metric(label='Active Customers', value='2,500', delta='+5.2%')
with col3:
    st.metric(label='Avg Order Value', value='$145', delta='+3.1%')
with col4:
    st.metric(label='Churn Rate', value='4.8%', delta='-1.2%', delta_color='inverse')
with col5:
    st.metric(label='Marketing ROI', value='4.8x', delta='+18%')

st.divider()

# Level 2: Trend Section
st.header('Trends and Momentum')

months = pd.date_range('2024-01-01', periods=12, freq='M')
revenue = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]
active_customers = [2200, 2250, 2280, 2270, 2310, 2350, 2380, 2360, 2400, 2430, 2470, 2500]
churned_customers = [110, 108, 112, 115, 110, 105, 108, 112, 109, 104, 101, 98]
campaign_engagement = [42, 45, 48, 46, 53, 51, 49, 47, 55, 58, 60, 62]

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(months, revenue, marker='o', linewidth=2, color=PALETTE['primary'], label='Revenue')
ax1.axhline(y=5.0, color=PALETTE['success'], linestyle='--', linewidth=1.5, label='Target: $5M')
ax1.set_title('Monthly Revenue Trend (2024)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Month', fontsize=11)
ax1.set_ylabel('Revenue ($M)', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.legend()
fig1.autofmt_xdate()

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(months, active_customers, marker='o', linewidth=2, color=PALETTE['primary'], label='Active Customers')
ax2.plot(months, churned_customers, marker='s', linewidth=2, color=PALETTE['danger'], label='Churned Customers')
ax2.set_title('Customer Growth vs Churn', fontsize=14, fontweight='bold')
ax2.set_xlabel('Month', fontsize=11)
ax2.set_ylabel('Customer Count', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.legend()
fig2.autofmt_xdate()

fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(months, campaign_engagement, marker='o', linewidth=2, color=PALETTE['secondary'], label='Campaign Engagement')
ax3.axhline(y=50, color=PALETTE['success'], linestyle='--', linewidth=1.5', label='Engagement Target')
ax3.set_title('Marketing Campaign Engagement Trend', fontsize=14, fontweight='bold')
ax3.set_xlabel('Month', fontsize=11)
ax3.set_ylabel('Engagement Score', fontsize=11)
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
segments = ['Enterprise', 'Mid-Market', 'SMB', 'Starter']
segment_revenue = [2.1, 1.5, 1.0, 0.6]
region_revenue = [1.8, 1.4, 1.0, 0.4]
segment_colors = [PALETTE['primary'], PALETTE['secondary'], PALETTE['success'], PALETTE['danger']]

fig4, ax4 = plt.subplots(figsize=(10, 4))
bars = ax4.barh(segments, segment_revenue, color=segment_colors)
ax4.set_xlabel('Revenue ($M)', fontsize=11)
ax4.set_title('Revenue by Customer Segment', fontsize=14, fontweight='bold')
for bar, val in zip(bars, segment_revenue):
    ax4.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2, f'${val}M', va='center', fontsize=10)

fig5, ax5 = plt.subplots(figsize=(10, 4))
regions = ['North', 'South', 'East', 'West']
bars2 = ax5.bar(regions, region_revenue, color=[PALETTE['primary'], PALETTE['secondary'], PALETTE['success'], PALETTE['danger']])
ax5.set_ylabel('Revenue ($M)', fontsize=11)
ax5.set_title('Revenue by Region', fontsize=14, fontweight='bold')
for bar, val in zip(bars2, region_revenue):
    ax5.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03, f'${val}M', ha='center', fontsize=10)

col1, col2 = st.columns(2)
with col1:
    st.pyplot(fig4)
with col2:
    st.pyplot(fig5)

st.divider()

# Level 4: Detailed Data Explorer
st.header('Detailed Data Explorer')
st.sidebar.header('Filters')
segment_options = ['All', 'Enterprise', 'Mid-Market', 'SMB', 'Starter']
selected_segment = st.sidebar.selectbox('Customer Segment', segment_options)

start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
selected_range = st.sidebar.date_input('Date Range', value=(start_date, end_date))

records = [
    {'customer_id': f'C{100+i}', 'segment': segment, 'revenue': round(2000 + i * 15, 2), 'last_activity': '2024-12-01', 'churn_risk': 'Low'}
    for i, segment in enumerate(['Enterprise', 'Mid-Market', 'SMB', 'Starter'] * 10)
]
df = pd.DataFrame(records)

if selected_segment != 'All':
    filtered_df = df[df['segment'] == selected_segment]
else:
    filtered_df = df

st.write(f'Showing {len(filtered_df):,} records')
st.dataframe(filtered_df[['customer_id', 'segment', 'revenue', 'last_activity', 'churn_risk']])

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label='Download CSV',
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)
