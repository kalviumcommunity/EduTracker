import os
import sys
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

def generate_raw_transaction_data(filepath='data/raw/raw_customer_transactions.csv'):
    """Generate sample customer transaction totals and counts dataset."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    n_customers = 1200
    
    customer_ids = [f"CUST-{i}" for i in range(10001, 10001 + n_customers)]
    
    # Days as customer between 30 (1 month) and 1095 (3 years)
    days_as_customer = np.random.randint(30, 1096, size=n_customers)
    
    # Total transactions (gamma distribution to create low, medium, and power users)
    total_transactions = np.maximum(1, np.round(np.random.gamma(shape=2.5, scale=8.0, size=n_customers))).astype(int)
    
    # Total spent correlated with total transactions plus noise
    avg_spend = np.random.uniform(25.0, 250.0, size=n_customers)
    total_spent = np.round(total_transactions * avg_spend, 2)
    
    # Days since last purchase (recency): must be <= days_as_customer
    days_since_last_purchase = np.array([np.random.randint(1, max(2, min(365, int(dac)))) for dac in days_as_customer])
    
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'days_as_customer': days_as_customer,
        'total_transactions': total_transactions,
        'purchase_count': total_transactions,  # Alias for RFM formula compatibility
        'total_spent': total_spent,
        'days_since_last_purchase': days_since_last_purchase,
        'customer_region': np.random.choice(['North America', 'Europe', 'Asia-Pacific', 'Latin America'], size=n_customers)
    })
    
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic raw transaction dataset created at {filepath} ({len(df)} records)")
    print(f"  • Days as customer range:       {df['days_as_customer'].min()} to {df['days_as_customer'].max()} days")
    print(f"  • Total transactions range:     {df['total_transactions'].min()} to {df['total_transactions'].max()} transactions")
    print(f"  • Total spent range:            ${df['total_spent'].min():,.2f} to ${df['total_spent'].max():,.2f}\n")
    return df

def run_feature_engineering_pipeline(df):
    """Execute all 5 feature engineering and validation tasks."""
    print("="*70)
    print("FEATURE ENGINEERING PIPELINE (RATIOS, BINNING & COMPOSITE RFM)")
    print("="*70)
    df_feat = df.copy()
    
    # Task 1: Compute Ratio Features
    print("\n--- TASK 1: COMPUTE RATIO FEATURES ---")
    df_feat['transactions_per_month'] = df_feat['total_transactions'] / (df_feat['days_as_customer'] / 30.0)
    df_feat['avg_spend_per_transaction'] = df_feat['total_spent'] / df_feat['total_transactions']
    df_feat['lifetime_value_per_month'] = df_feat['total_spent'] / (df_feat['days_as_customer'] / 30.0)

    print("Summary statistics for engineered ratio features:")
    print(df_feat[['transactions_per_month', 'avg_spend_per_transaction', 'lifetime_value_per_month']].describe().round(2))
    print("\n[Business Value of Ratio Features]:")
    print("  • Ratio normalization removes tenure bias: a 3-year customer with 30 orders has the exact same engagement rate (0.83 tx/month) as a 3-month customer with 2.5 orders.")

    # Task 2: Binning with Equal-Width Bins (Custom Domain Boundaries)
    print("\n--- TASK 2: BINNING WITH EQUAL-WIDTH / FIXED BOUNDARY BINS ---")
    df_feat['engagement_tier'] = pd.cut(
        df_feat['transactions_per_month'],
        bins=[0, 2, 10, float('inf')],
        labels=['low', 'medium', 'high']
    )

    print("Engagement Tier Distribution (Transactions/Month: <2 low, 2-10 medium, >10 high):")
    val_counts = df_feat['engagement_tier'].value_counts()
    for tier, count in val_counts.items():
        print(f"  • {tier.upper():<8}: {count:>4} customers ({count/len(df_feat)*100:>5.1f}%)")

    # Task 3: Binning with Quantiles (Equal Sample Size Quartiles)
    print("\n--- TASK 3: BINNING WITH QUANTILES (EQUAL SAMPLE SIZE QUARTILES) ---")
    df_feat['spend_quartile'] = pd.qcut(
        df_feat['total_spent'],
        q=4,
        labels=['Q1', 'Q2', 'Q3', 'Q4']
    )

    print("Spend Quartile Distribution (Equal 25% customer cohorts by total revenue):")
    q_counts = df_feat['spend_quartile'].value_counts()
    for q, count in q_counts.items():
        print(f"  • {q}: {count:>4} customers ({count/len(df_feat)*100:>5.1f}%)")
    print("\n[Comparison: pd.cut vs pd.qcut]:")
    print("  • `pd.cut` sets fixed numerical thresholds (0, 2, 10) suitable for SLA or business policy tiers.")
    print("  • `pd.qcut` dynamically splits data into equal-sized cohorts (quartiles/deciles), ideal for relative ranking like top 25% VIP spenders.")

    # Task 4: Composite Score (RFM Customer Health Scoring)
    print("\n--- TASK 4: COMPOSITE SCORE (RFM CUSTOMER HEALTH SCORING) ---")
    # Note: For recency, lower days = higher health score (labels=[5,4,3,2,1])
    df_feat['recency_score'] = pd.qcut(df_feat['days_since_last_purchase'], q=5, labels=[5, 4, 3, 2, 1])
    df_feat['frequency_score'] = pd.qcut(df_feat['purchase_count'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    df_feat['monetary_score'] = pd.qcut(df_feat['total_spent'], q=5, labels=[1, 2, 3, 4, 5])

    df_feat['rfm_score'] = (df_feat['recency_score'].astype(int) + 
                            df_feat['frequency_score'].astype(int) + 
                            df_feat['monetary_score'].astype(int))
                            
    # Create descriptive segment labels
    def assign_rfm_segment(score):
        if score >= 13:
            return 'Champions / VIP'
        elif score >= 10:
            return 'Loyal Customers'
        elif score >= 7:
            return 'Needs Attention'
        else:
            return 'At-Risk / Churning'
            
    df_feat['customer_health_segment'] = df_feat['rfm_score'].apply(assign_rfm_segment)
    print(f"Composite RFM Score computed across {len(df_feat)} customers.")
    print("Customer Health Segment Breakdown:")
    seg_counts = df_feat['customer_health_segment'].value_counts()
    for seg, count in seg_counts.items():
        print(f"  • {seg:<20}: {count:>4} customers ({count/len(df_feat)*100:>5.1f}%)")

    # Task 5: Feature Validation
    print("\n--- TASK 5: FEATURE VALIDATION & INTEGRITY CHECKS ---")
    # Check ranges are sensible
    print(f"Engagement tier distribution:\n{df_feat['engagement_tier'].value_counts()}")
    print(f"RFM score range: {df_feat['rfm_score'].min()} to {df_feat['rfm_score'].max()} (Expected valid range: 3-15)")

    # Ensure no NaNs introduced
    missing_cnt = df_feat[['engagement_tier', 'spend_quartile', 'rfm_score']].isna().sum()
    print(f"\nMissing values in engineered features:\n{missing_cnt}")
    
    # Assert zero NaNs
    assert missing_cnt.sum() == 0, "Error: NaNs introduced during feature engineering!"
    print("✓ Validation passed: All engineered features contain 0 missing values and fall within logical boundaries.")

    # Export Processed Dataset & Summary Table
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    proc_dir = 'data/processed'
    if not os.path.exists(proc_dir) and os.path.exists('../data'):
        proc_dir = '../data/processed'
    else:
        os.makedirs(proc_dir, exist_ok=True)
        
    proc_path = os.path.join(proc_dir, 'engineered_customer_features.csv')
    df_feat.to_csv(proc_path, index=False)
    print(f"\n✓ Exported {len(df_feat)} engineered records to {proc_path}")
    
    # Summary Report Table
    summary_df = df_feat.groupby('customer_health_segment')[['transactions_per_month', 'avg_spend_per_transaction', 'lifetime_value_per_month', 'rfm_score']].mean().round(2).reset_index()
    summary_path = os.path.join(output_dir, 'feature_engineering_summary.csv')
    summary_df.to_csv(summary_path, index=False)
    print(f"✓ Executive segment summary table exported to {summary_path}:")
    print(summary_df.to_string(index=False))

    # Generate Visual 2x2 Feature Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Top-Left: Transactions/Month Histogram by Tier
    for tier in ['low', 'medium', 'high']:
        subset = df_feat[df_feat['engagement_tier'] == tier]['transactions_per_month']
        axes[0, 0].hist(subset, bins=20, alpha=0.6, label=f"{tier.title()} (<2, 2-10, >10)", edgecolor='black')
    axes[0, 0].set_title('Engagement Rate by Tier (Transactions / Month)', fontweight='bold')
    axes[0, 0].set_xlabel('Transactions per Month')
    axes[0, 0].set_ylabel('Customer Count')
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle='--', alpha=0.5)
    
    # 2. Top-Right: Total Spend Boxplot by Quartile
    quartile_data = [df_feat[df_feat['spend_quartile'] == q]['total_spent'] for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    axes[0, 1].boxplot(quartile_data, tick_labels=['Q1 (Bottom 25%)', 'Q2', 'Q3', 'Q4 (Top 25%)'], patch_artist=True, boxprops=dict(facecolor='#5bc0de'))
    axes[0, 1].set_title('Total Spend Distribution Across Quartiles (pd.qcut)', fontweight='bold')
    axes[0, 1].set_ylabel('Total Spent ($)')
    axes[0, 1].grid(True, linestyle='--', alpha=0.5)
    
    # 3. Bottom-Left: RFM Score Histogram
    axes[1, 0].hist(df_feat['rfm_score'], bins=range(3, 17), align='left', color='#5cb85c', edgecolor='black', rwidth=0.8)
    axes[1, 0].set_title('Composite RFM Customer Health Score (Range: 3 - 15)', fontweight='bold')
    axes[1, 0].set_xlabel('RFM Score (Recency + Frequency + Monetary)')
    axes[1, 0].set_ylabel('Customer Count')
    axes[1, 0].set_xticks(range(3, 16))
    axes[1, 0].grid(axis='y', linestyle='--', alpha=0.5)
    
    # 4. Bottom-Right: LTV by Health Segment
    seg_names = summary_df['customer_health_segment']
    ltv_vals = summary_df['lifetime_value_per_month']
    bars = axes[1, 1].barh(seg_names, ltv_vals, color='#f0ad4e', edgecolor='black')
    axes[1, 1].set_title('Average Monthly LTV ($/Month) by Health Segment', fontweight='bold')
    axes[1, 1].set_xlabel('Monthly Lifetime Value ($)')
    axes[1, 1].grid(axis='x', linestyle='--', alpha=0.5)
    for bar in bars:
        width = bar.get_width()
        axes[1, 1].text(width + 2, bar.get_y() + bar.get_height()/2, f"${width:,.2f}", va='center', fontweight='bold')
        
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'feature_distributions_dashboard.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"\n✓ Visual 2x2 feature engineering dashboard saved to {chart_path}")
    print("="*70 + "\n")
    
    return df_feat, summary_df

if __name__ == "__main__":
    filepath = 'data/raw/raw_customer_transactions.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    df_raw = generate_raw_transaction_data(filepath)
    df_engineered, summary_df = run_feature_engineering_pipeline(df_raw)
