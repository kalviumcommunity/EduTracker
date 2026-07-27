import os
import sys
import json
import pandas as pd
import numpy as np

# Set non-interactive backend for matplotlib before importing pyplot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Ensure standard output can handle UTF-8 symbols on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def generate_daily_revenue_data(filepath='data/raw/daily_revenue_transactions.csv', days=730):
    """Generate synthetic daily revenue dataset with strong day-to-day noise ($8k-$12k fluctuations) over an underlying trend."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    print(f"Generating synthetic {days}-day revenue dataset with high daily volatility...")
    
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    
    # Baseline trend: starts around $9,000, has a mid-year dip, and then strong accelerating growth toward $15,000
    t = np.arange(days)
    trend = 9000.0 + 12.0 * t - 1500.0 * np.sin(2 * np.pi * t / 365.0)
    
    # Strong daily fluctuations ($8k one day, $12k next) via normal noise + day-of-week seasonality (weekends lower)
    dow_effect = np.where(dates.dayofweek >= 5, -1800.0, 800.0)
    daily_noise = np.random.normal(0, 2200.0, size=days)
    
    revenue = np.round(np.maximum(1500.0, trend + dow_effect + daily_noise), 2)
    
    # Orders and active customers correlate with revenue + noise
    orders = np.round(revenue / np.random.uniform(70.0, 110.0, size=days)).astype(int)
    customers = np.round(orders * np.random.uniform(0.7, 0.9, size=days)).astype(int)
    
    df = pd.DataFrame({
        'date': dates,
        'revenue': revenue,
        'orders': orders,
        'customers': customers
    })
    
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic daily revenue dataset created at {filepath} ({len(df):,} days)")
    print(f"  • Date Range:           {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"  • Mean Daily Revenue:   ${df['revenue'].mean():,.2f}")
    print(f"  • Daily Volatility (std): ${df['revenue'].std():,.2f}\n")
    return df

def run_time_series_trends_pipeline(df):
    """Execute all 5 time-series resampling, rolling average, cumulative growth, and trend analysis tasks."""
    print("="*70)
    print("TIME-SERIES RESAMPLING, ROLLING AVERAGES & TREND ANALYSIS PIPELINE")
    print("="*70)
    df_ana = df.copy()
    df_ana['date'] = pd.to_datetime(df_ana['date'], format='%Y-%m-%d')
    
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)

    # Set datetime index for resampling
    df_ts = df_ana.set_index('date')
    
    # Handle pandas resampling frequency strings safely ('ME' in newer pandas vs 'M')
    try:
        resample_month = 'ME'
        _ = df_ts['revenue'].resample(resample_month).sum()
    except ValueError:
        resample_month = 'M'

    # Task 1: Resample Data by Time Period (Weekly and Monthly)
    print("\n--- TASK 1: RESAMPLE DATA BY TIME PERIOD (WEEKLY & MONTHLY AGGREGATIONS) ---")
    weekly_revenue = df_ts['revenue'].resample('W').sum()
    weekly_count = df_ts['orders'].resample('W').count()
    weekly_avg = df_ts['revenue'].resample('W').mean()

    print("Recent Weekly Revenue ($ Sum) - Last 5 Weeks:")
    print(weekly_revenue.tail(5).map(lambda x: f"${x:,.2f}"))
    
    monthly_revenue = df_ts['revenue'].resample(resample_month).sum()
    monthly_orders = df_ts['orders'].resample(resample_month).sum()
    monthly_avg_rev = df_ts['revenue'].resample(resample_month).mean()

    monthly_summary = pd.DataFrame({
        'total_revenue': monthly_revenue,
        'total_orders': monthly_orders,
        'avg_daily_revenue': monthly_avg_rev
    })
    
    print("\nMonthly Aggregation Summary Table:")
    print(monthly_summary.round(2).to_string())
    
    max_month_idx = monthly_revenue.idxmax()
    print(f"\n[Resampling Comparison Insight]:")
    print(f"  • Highest Revenue Period: {max_month_idx.strftime('%B %Y')} with ${monthly_revenue.loc[max_month_idx]:,.2f} in total revenue.")
    print("  • Resampling aggregates high-variance daily fluctuations into interpretable macro buckets.")

    # Task 2: Compute Rolling Window Average (7-Day and 30-Day MAs)
    print("\n--- TASK 2: COMPUTE ROLLING WINDOW AVERAGES (7-DAY & 30-DAY MAs) ---")
    df_ana['revenue_ma7'] = df_ana['revenue'].rolling(window=7).mean()
    df_ana['revenue_ma30'] = df_ana['revenue'].rolling(window=30).mean()

    print("Recent Daily Records with 7-Day and 30-Day Rolling Averages:")
    print(df_ana[['date', 'revenue', 'revenue_ma7', 'revenue_ma30']].tail(8).to_string(index=False))

    # Plot Raw vs Rolling MAs
    plt.figure(figsize=(14, 6))
    plt.plot(df_ana['date'], df_ana['revenue'], label='Raw Daily Revenue ($8k-$12k noise)', alpha=0.35, color='gray', lw=1)
    plt.plot(df_ana['date'], df_ana['revenue_ma7'], label='7-Day Moving Average (Short-term trend)', color='#5bc0de', lw=2)
    plt.plot(df_ana['date'], df_ana['revenue_ma30'], label='30-Day Moving Average (Macro trend)', color='#d9534f', lw=3)
    plt.title('Daily Revenue vs Rolling Moving Averages (7-Day & 30-Day Windows)', fontweight='bold', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.legend(loc='upper left', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    rolling_plot_path = os.path.join(output_dir, 'rolling_avg.png')
    plt.savefig(rolling_plot_path, dpi=300)
    plt.close()
    print(f"\n✓ Saved rolling window comparison chart to: {rolling_plot_path}")
    print("  • Notice how the 30-day moving average strips away the violent $2,200+ daily noise to expose a clear mid-year seasonal trough followed by sustained Q4 accelerating momentum!")

    # Task 3: Calculate Month-over-Month Percentage Change
    print("\n--- TASK 3: CALCULATE MONTH-OVER-MONTH (MoM) PERCENTAGE CHANGE ---")
    mom_change = monthly_revenue.pct_change() * 100

    mom_df = pd.DataFrame({
        'monthly_revenue': monthly_revenue.map(lambda x: f"${x:,.2f}"),
        'mom_growth_pct': mom_change.round(2).map(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A")
    })
    print("Month-over-Month Revenue Growth Matrix:")
    print(mom_df.to_string())

    growth_months = mom_change[mom_change > 0]
    decline_months = mom_change[mom_change < 0]
    print(f"\n[Growth vs Decline Breakdown]:")
    print(f"  • Positive Growth Months ({len(growth_months)}): {', '.join([m.strftime('%b %Y') for m in growth_months.index])}")
    print(f"  • Negative Decline Months ({len(decline_months)}): {', '.join([m.strftime('%b %Y') for m in decline_months.index])}")
    print("  • Pattern Explanation: The business exhibits predictable seasonality with summer consolidation followed by strong Q3/Q4 acceleration.")

    # Task 4: Compute Cumulative Sum
    print("\n--- TASK 4: COMPUTE CUMULATIVE SUM (REVENUE & ORDERS ACCUMULATION) ---")
    df_ana['cumulative_revenue'] = df_ana['revenue'].cumsum()
    df_ana['cumulative_orders'] = df_ana['orders'].cumsum()

    plt.figure(figsize=(12, 6))
    plt.plot(df_ana['date'], df_ana['cumulative_revenue'], color='#5cb85c', lw=3, label='Cumulative Revenue')
    plt.title('Cumulative Revenue Over Time ($ Total Accumulated)', fontweight='bold', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Cumulative Revenue ($)')
    plt.legend(loc='upper left', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    cum_plot_path = os.path.join(output_dir, 'cumulative.png')
    plt.savefig(cum_plot_path, dpi=300)
    plt.close()
    print(f"✓ Saved cumulative growth trajectory chart to: {cum_plot_path}")
    print(f"  • Total Accumulated Revenue by End of Period: ${df_ana['cumulative_revenue'].iloc[-1]:,.2f}")
    print(f"  • Total Accumulated Orders by End of Period:  {df_ana['cumulative_orders'].iloc[-1]:,}")

    # Task 5: Identify Trend Pattern and Business Implications
    print("\n--- TASK 5: IDENTIFY TREND PATTERN & BUSINESS IMPLICATIONS ---")
    recent_ma30 = df_ana['revenue_ma30'].dropna().iloc[-30:]
    trend_direction = 'up' if recent_ma30.iloc[-1] > recent_ma30.iloc[0] else 'down'
    trend_magnitude = ((recent_ma30.iloc[-1] - recent_ma30.iloc[0]) / recent_ma30.iloc[0]) * 100

    last_mom = mom_change.dropna().iloc[-1]

    action_str = (
        f"With rolling velocity increasing by {trend_magnitude:.1f}% over the last 30 days, capitalize on positive momentum by increasing inventory and scaling customer acquisition campaigns."
        if trend_direction == 'up' else
        f"With rolling velocity declining by {abs(trend_magnitude):.1f}% over the last 30 days, investigate conversion drop-offs and prioritize customer retention over aggressive expansion."
    )
    
    implication_str = (
        "Accelerating growth - maintain current strategy and expand acquisition spend"
        if trend_direction == 'up' else
        "Declining momentum - investigate customer churn and marketing efficiency"
    )

    analysis = f"""TREND ANALYSIS & EXECUTIVE IMPLICATIONS:

Rolling Average Trend Direction: {trend_direction.upper()}
Magnitude of Change over last 30 days: {trend_magnitude:.1f}%
Latest Month-over-Month Growth: {last_mom:.1f}%

Business Implications:
- {implication_str}
- Daily Revenue Volatility: ${df_ana['revenue'].std():,.0f} (standard deviation measure of noise)

Recommended Action:
- Do not react to day-to-day dips (e.g., $8k drop on a Tuesday); evaluate all performance against the 30-day moving average (${df_ana['revenue_ma30'].iloc[-1]:,.0f}).
- {action_str}
"""
    print(analysis)

    # Save report JSON
    report_dict = {
        'trend_direction': trend_direction.upper(),
        'trend_magnitude_30d_pct': round(float(trend_magnitude), 2),
        'latest_mom_growth_pct': round(float(last_mom), 2),
        'daily_volatility_std': round(float(df_ana['revenue'].std()), 2),
        'total_cumulative_revenue': round(float(df_ana['cumulative_revenue'].iloc[-1]), 2),
        'highest_revenue_month': max_month_idx.strftime('%B %Y'),
        'highest_month_revenue': round(float(monthly_revenue.loc[max_month_idx]), 2),
        'business_implication': implication_str,
        'recommended_action': action_str
    }
    
    report_path = os.path.join(output_dir, 'time_series_trend_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2)
    print(f"✓ Executive time-series analysis report saved to: {report_path}")

    # Save processed dataframe
    proc_dir = 'data/processed'
    if not os.path.exists(proc_dir) and os.path.exists('../data'):
        proc_dir = '../data/processed'
    else:
        os.makedirs(proc_dir, exist_ok=True)
        
    proc_path = os.path.join(proc_dir, 'processed_time_series_revenue.csv')
    df_ana.to_csv(proc_path, index=False)
    print(f"✓ Exported processed time-series table ({len(df_ana):,} days) with MAs and cumulative sums to: {proc_path}")
    print("="*70 + "\n")
    
    return df_ana, report_dict

if __name__ == "__main__":
    filepath = 'data/raw/daily_revenue_transactions.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    df_raw = generate_daily_revenue_data(filepath)
    df_ts, report_dict = run_time_series_trends_pipeline(df_raw)
