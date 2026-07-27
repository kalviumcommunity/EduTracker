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

def generate_segmentation_dataset(filepath='data/raw/customer_segmentation_data.csv', n_customers=2000):
    """Generate synthetic customer dataset matching explicit segment distributions and churn/revenue disparities."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    print(f"Generating synthetic {n_customers:,}-row customer dataset with segment disparities...")
    
    # Segment counts: Enterprise (5% = 100), SMB (40% = 800), Startup (55% = 1100)
    n_ent = 100
    n_smb = 800
    n_str = 1100
    
    # 1. Enterprise: 1% churn (1 churner), ~$70,000 average revenue (~$7M total = 70%), ~1.2 support tickets
    ent_churn = np.array([1]*1 + [0]*(n_ent - 1))
    np.random.shuffle(ent_churn)
    ent_rev = np.round(np.random.normal(70000.0, 5000.0, size=n_ent), 2)
    ent_tix = np.random.poisson(1.2, size=n_ent)
    ent_prod = np.random.choice(['Cloud Platform', 'Analytics Suite', 'Developer API'], size=n_ent, p=[0.60, 0.30, 0.10])
    
    # 2. SMB: 12% churn (96 churners), ~$1,875 average revenue (~$1.5M total = 15%), ~5.8 support tickets
    smb_churn = np.array([1]*96 + [0]*(n_smb - 96))
    np.random.shuffle(smb_churn)
    smb_rev = np.round(np.random.normal(1875.0, 300.0, size=n_smb), 2)
    smb_tix = np.random.poisson(5.8, size=n_smb)
    smb_prod = np.random.choice(['Cloud Platform', 'Analytics Suite', 'Developer API'], size=n_smb, p=[0.40, 0.40, 0.20])
    
    # 3. Startup: 8% churn (88 churners), ~$1,364 average revenue (~$1.5M total = 15%), ~3.4 support tickets
    str_churn = np.array([1]*88 + [0]*(n_str - 88))
    np.random.shuffle(str_churn)
    str_rev = np.round(np.random.normal(1363.64, 250.0, size=n_str), 2)
    str_tix = np.random.poisson(3.4, size=n_str)
    str_prod = np.random.choice(['Cloud Platform', 'Analytics Suite', 'Developer API'], size=n_str, p=[0.25, 0.35, 0.40])
    
    df = pd.DataFrame({
        'customer_id': range(10001, 10001 + n_customers),
        'customer_type': ['Enterprise']*n_ent + ['SMB']*n_smb + ['Startup']*n_str,
        'product': np.concatenate([ent_prod, smb_prod, str_prod]),
        'revenue': np.concatenate([ent_rev, smb_rev, str_rev]),
        'churn': np.concatenate([ent_churn, smb_churn, str_churn]),
        'support_tickets': np.concatenate([ent_tix, smb_tix, str_tix])
    })
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic segmentation dataset created at {filepath} ({len(df):,} records)")
    print(f"  • Total Revenue:               ${df['revenue'].sum():,.2f}")
    print(f"  • Overall Dataset Churn Rate:  {df['churn'].mean()*100:.2f}%\n")
    return df

def run_segmentation_groupby_pipeline(df):
    """Execute all 5 groupby, multi-level aggregation, pivot table, and actionable insight tasks."""
    print("="*70)
    print("GROUPBY AGGREGATION, SEGMENTATION & ACTIONABLE INSIGHTS PIPELINE")
    print("="*70)
    
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)

    # Task 1: Single-Level GroupBy with Multiple Aggregations
    print("\n--- TASK 1: SINGLE-LEVEL GROUPBY WITH MULTIPLE AGGREGATIONS ---")
    segment_metrics = df.groupby('customer_type').agg({
        'churn': 'mean',
        'revenue': 'sum',
        'customer_id': 'count',
        'support_tickets': 'mean'
    })

    segment_metrics.columns = ['churn_rate', 'total_revenue', 'customer_count', 'avg_support_tickets']

    print("Raw Segment Aggregations (Customer Type):")
    print(segment_metrics.round(4))
    print("\n[Why One Dataset-Wide Statistic Hides the Real Story]:")
    print(f"  • While overall churn is {df['churn'].mean()*100:.1f}%, grouping surfaces severe divergence:")
    print("  • Enterprise generates ~70% of total revenue with near-zero churn (1.0%), whereas SMB suffers critical 12.0% churn.")

    # Task 2: Multi-Level GroupBy (Two dimensions simultaneously)
    print("\n--- TASK 2: MULTI-LEVEL GROUPBY (CUSTOMER TYPE X PRODUCT) ---")
    product_segment = df.groupby(['customer_type', 'product']).agg({
        'revenue': 'sum',
        'customer_id': 'count'
    })

    product_segment.columns = ['total_revenue', 'customer_count']

    # Unstack for cleaner view
    product_segment_pivot = product_segment.unstack()
    print("Multi-Level Aggregation Unstacked (Total Revenue & Customer Count by Product):")
    print(product_segment_pivot.round(2))

    # Task 3: Pivot Table
    print("\n--- TASK 3: PIVOT TABLE (CUSTOMER TYPE ROWS X PRODUCT COLUMNS) ---")
    pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_type',
        columns='product',
        aggfunc='sum'
    )

    print("Revenue Pivot Table ($ Sum by Customer Type and Product):")
    print(pivot.round(2).map(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00"))

    # Task 4: Rank and Identify Top/Bottom Performers
    print("\n--- TASK 4: RANK AND IDENTIFY TOP / BOTTOM PERFORMING SEGMENTS ---")
    # Rank segments by churn (rank 1 = lowest churn / best performer)
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()

    # Sort to see worst first
    worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
    print("Segments Ranked by Churn Rate (Worst First):")
    print(worst_first[['churn_rate', 'churn_rank', 'avg_support_tickets']].round(4))

    # Profit/revenue ranking
    segment_metrics['revenue_contribution'] = (segment_metrics['total_revenue'] / segment_metrics['total_revenue'].sum() * 100)
    print("\nRevenue Contribution (%) vs Churn Rate (%):")
    print(segment_metrics[['revenue_contribution', 'churn_rate']].round(4))

    # Task 5: Surface Actionable Segment Insights
    print("\n--- TASK 5: SURFACE ACTIONABLE SEGMENT INSIGHTS ---")
    insights = []

    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        
        insight = {
            'segment': segment,
            'customer_count': int(row['customer_count']),
            'churn_rate': f"{row['churn_rate']:.1%}",
            'total_revenue': f"${row['total_revenue']:,.0f}",
            'revenue_contribution': f"{row['revenue_contribution']:.1f}%",
            'action': ''
        }
        
        # Action based on metrics
        if row['churn_rate'] > 0.10:
            insight['action'] = 'HIGH PRIORITY: Churn above 10%. Investigate pain points.'
        elif row['churn_rate'] < 0.02:
            insight['action'] = 'Healthy. Maintain current service level.'
        else:
            insight['action'] = 'Monitor. No immediate action needed.'
        
        insights.append(insight)

    insights_df = pd.DataFrame(insights)
    print("Executive Segment Insights Summary Table:")
    print(insights_df.to_string(index=False))
    
    insights_path = os.path.join(output_dir, 'segment_insights.csv')
    insights_df.to_csv(insights_path, index=False)
    print(f"\n✓ Exported actionable segment insights table to: {insights_path}")

    # Generate Visual 2x2 Segmentation Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Top-Left: Revenue Contribution Bar Chart
    segs = segment_metrics.index
    rev_contribs = segment_metrics['revenue_contribution']
    axes[0, 0].bar(segs, rev_contribs, color=['#5cb85c', '#f0ad4e', '#5bc0de'], edgecolor='black', width=0.5)
    axes[0, 0].set_title('Revenue Contribution (%) by Segment', fontweight='bold', fontsize=12)
    axes[0, 0].set_ylabel('Percentage of Total Revenue (%)')
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(rev_contribs):
        axes[0, 0].text(i, v + 1.5, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=11)
    axes[0, 0].set_ylim(0, 85)

    # 2. Top-Right: Churn Rate by Segment with Threshold Line
    churn_rates_pct = segment_metrics['churn_rate'] * 100
    axes[0, 1].bar(segs, churn_rates_pct, color=['#5cb85c', '#d9534f', '#f0ad4e'], edgecolor='black', width=0.5)
    axes[0, 1].axhline(10.0, color='red', linestyle='--', linewidth=2, label='10% High Priority Threshold')
    axes[0, 1].set_title('Churn Rate (%) by Segment', fontweight='bold', fontsize=12)
    axes[0, 1].set_ylabel('Churn Rate (%)')
    axes[0, 1].legend(loc='upper right')
    axes[0, 1].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(churn_rates_pct):
        axes[0, 1].text(i, v + 0.5, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=11)
    axes[0, 1].set_ylim(0, 15)

    # 3. Bottom-Left: Stacked Revenue by Product
    pivot.plot(kind='bar', stacked=True, ax=axes[1, 0], colormap='viridis', edgecolor='black', rot=0)
    axes[1, 0].set_title('Total Revenue ($ Sum) by Segment and Product', fontweight='bold', fontsize=12)
    axes[1, 0].set_ylabel('Total Revenue ($)')
    axes[1, 0].legend(title='Product Line', fontsize=10)
    axes[1, 0].grid(axis='y', linestyle='--', alpha=0.5)

    # 4. Bottom-Right: Average Support Tickets by Segment
    avg_tix = segment_metrics['avg_support_tickets']
    axes[1, 1].barh(segs, avg_tix, color='#d9534f', edgecolor='black', height=0.5)
    axes[1, 1].set_title('Average Support Tickets per Customer', fontweight='bold', fontsize=12)
    axes[1, 1].set_xlabel('Average Support Tickets')
    axes[1, 1].grid(axis='x', linestyle='--', alpha=0.5)
    for i, v in enumerate(avg_tix):
        axes[1, 1].text(v + 0.1, i, f"{v:.1f} tix", va='center', fontweight='bold', fontsize=11)
    axes[1, 1].set_xlim(0, 7)

    plt.tight_layout()
    dashboard_path = os.path.join(output_dir, 'segmentation_analysis_dashboard.png')
    plt.savefig(dashboard_path, dpi=300)
    plt.close()
    print(f"✓ Saved visual 2x2 segmentation analysis dashboard to: {dashboard_path}")
    print("="*70 + "\n")
    
    return segment_metrics, insights_df

if __name__ == "__main__":
    filepath = 'data/raw/customer_segmentation_data.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    df_raw = generate_segmentation_dataset(filepath)
    metrics_df, insights_df = run_segmentation_groupby_pipeline(df_raw)
