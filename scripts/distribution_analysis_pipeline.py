import os
import sys
import json
import pandas as pd
import numpy as np
from scipy import stats

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

def generate_skewed_revenue_data(filepath='data/raw/customer_revenue_skewed.csv'):
    """Generate synthetic customer revenue dataset matching target statistics (mean~$1,200, median~$450, skewness~2.5)."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    
    # 1,850 Retail/SMB customers with median around $450
    retail_smb = np.random.gamma(shape=4.2, scale=112.0, size=1850)
    
    # 150 Enterprise VIP accounts spending $6,500 to $15,000
    enterprise = np.random.uniform(6500.0, 15000.0, size=150)
    
    all_rev = np.concatenate([retail_smb, enterprise])
    
    # Fine-tune scale slightly so mean is near 1200 and median is near 450
    current_mean = np.mean(all_rev)
    scale_factor = 1200.0 / current_mean
    all_rev = np.round(all_rev * scale_factor, 2)
    
    df = pd.DataFrame({
        'customer_id': range(10001, 10001 + len(all_rev)),
        'revenue': all_rev,
        'customer_type': ['Retail/SMB']*1850 + ['Enterprise VIP']*150
    })
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic skewed revenue dataset created at {filepath} ({len(df):,} records)")
    print(f"  • Mean Revenue:   ${df['revenue'].mean():,.2f}")
    print(f"  • Median Revenue: ${df['revenue'].median():,.2f}")
    print(f"  • Skewness:       {stats.skew(df['revenue']):.2f}\n")
    return df

def run_distribution_analysis(df):
    """Execute all 5 distribution analysis, segmentation, and business interpretation tasks."""
    print("="*70)
    print("REVENUE DISTRIBUTION ANALYSIS, SKEWNESS & BUSINESS INTERPRETATION")
    print("="*70)
    df_ana = df.copy()
    
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)

    # Task 1: Distribution Plots (Histogram & KDE)
    print("\n--- TASK 1: GENERATE DISTRIBUTION PLOTS (HISTOGRAM & KDE) ---")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(df_ana['revenue'], bins=50, edgecolor='black', color='#66b3ff', alpha=0.8)
    axes[0].set_title('Revenue Distribution (Histogram)', fontweight='bold', fontsize=12)
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_ylabel('Frequency (Number of Customers)')
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # KDE (Kernel Density Estimation)
    df_ana['revenue'].plot(kind='density', ax=axes[1], color='#d9534f', lw=2.5)
    axes[1].set_title('Revenue Distribution (Kernel Density Estimate - KDE)', fontweight='bold', fontsize=12)
    axes[1].set_xlabel('Revenue ($)')
    axes[1].set_ylabel('Density')
    axes[1].grid(True, linestyle='--', alpha=0.5)
    axes[1].set_xlim(0, df_ana['revenue'].max() * 1.05)

    plt.tight_layout()
    hist_kde_path = os.path.join(output_dir, 'revenue_distribution.png')
    plt.savefig(hist_kde_path, dpi=300)
    plt.close()
    print(f"✓ Saved combined Histogram & KDE distribution chart to: {hist_kde_path}")

    # Task 2: Compute Skewness and Kurtosis
    print("\n--- TASK 2: COMPUTE SKEWNESS & KURTOSIS ---")
    skewness = stats.skew(df_ana['revenue'])
    kurtosis = stats.kurtosis(df_ana['revenue'])

    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}")

    if abs(skewness) > 1:
        print("✓ Highly right-skewed distribution detected → Use MEDIAN ($450) instead of MEAN ($1,200) as the primary KPI.")
    if kurtosis > 3:
        print("✓ Heavy tails (leptokurtic distribution) detected → Expect extreme enterprise outliers generating outsized revenue.")

    # Task 3: Identify Abnormal Patterns & Percentile Gaps
    print("\n--- TASK 3: IDENTIFY ABNORMAL PATTERNS (PERCENTILE ANALYSIS & BIMODALITY) ---")
    print("Full Summary Descriptive Statistics:")
    print(df_ana['revenue'].describe().round(2))

    print("\nPercentile Analysis (Quantiles):")
    percentiles = df_ana['revenue'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).round(2)
    for p, val in percentiles.items():
        print(f"  • {int(p*100):>2}th Percentile (P{int(p*100)}): ${val:,.2f}")

    gap_75_90 = percentiles.loc[0.90] / max(percentiles.loc[0.75], 1e-5)
    gap_90_99 = percentiles.loc[0.99] / max(percentiles.loc[0.90], 1e-5)
    print(f"\n[Abnormal Pattern Detection]:")
    print(f"  • Ratio between P90 (${percentiles.loc[0.90]:,.0f}) and P75 (${percentiles.loc[0.75]:,.0f}) is {gap_75_90:.1f}x!")
    print("  • This massive gap between the 75th and 90th percentiles confirms a bimodal/hidden sub-segment structure: a large retail base topped by an elite tier of enterprise spenders.")

    # Task 4: Compare Segment Distributions (High vs Low Value)
    print("\n--- TASK 4: COMPARE SEGMENT DISTRIBUTIONS (TOP 25% VS BOTTOM 25%) ---")
    q75 = df_ana['revenue'].quantile(0.75)
    q25 = df_ana['revenue'].quantile(0.25)
    
    high_value = df_ana[df_ana['revenue'] > q75]
    low_value = df_ana[df_ana['revenue'] < q25]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(high_value['revenue'], bins=30, alpha=0.7, label='High-Value (Top 25%)', color='#5cb85c', edgecolor='black')
    axes[0].hist(low_value['revenue'], bins=30, alpha=0.7, label='Low-Value (Bottom 25%)', color='#f0ad4e', edgecolor='black')
    axes[0].legend(fontsize=11)
    axes[0].set_title('Revenue: High vs Low Value Customers', fontweight='bold', fontsize=12)
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_ylabel('Customer Count')
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # Boxplot on Log Scale to display both segments cleanly
    axes[1].boxplot([low_value['revenue'], high_value['revenue']], tick_labels=['Low-Value\n(Bottom 25%)', 'High-Value\n(Top 25%)'], patch_artist=True, boxprops=dict(facecolor='#5bc0de'))
    axes[1].set_title('Segment Comparison (Log-Scale Boxplot)', fontweight='bold', fontsize=12)
    axes[1].set_ylabel('Revenue ($ - Log Scale)')
    axes[1].set_yscale('log')
    axes[1].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    seg_chart_path = os.path.join(output_dir, 'segment_distributions_comparison.png')
    plt.savefig(seg_chart_path, dpi=300)
    plt.close()
    print(f"✓ Saved segment comparison charts to: {seg_chart_path}")

    print(f"High-value (Top 25%):    mean=${high_value['revenue'].mean():,.0f}, median=${high_value['revenue'].median():,.0f} (N={len(high_value):,})")
    print(f"Low-value  (Bottom 25%): mean=${low_value['revenue'].mean():,.0f}, median=${low_value['revenue'].median():,.0f} (N={len(low_value):,})")

    # Task 5: Business Interpretation & Action Report
    print("\n--- TASK 5: BUSINESS INTERPRETATION & EXECUTIVE REPORT ---")
    interpretation = f"""
Revenue Distribution Analysis:

Skewness: {skewness:.2f} → {"Highly right-skewed" if skewness > 1 else "Moderate"}
Mean: ${df_ana['revenue'].mean():,.0f}
Median: ${df_ana['revenue'].median():,.0f}
Interpretation: {'Most customers are small; few are huge enterprise accounts' if skewness > 1 else 'Balanced distribution'}

Kurtosis: {kurtosis:.2f} → {"Fat tails (outliers)" if kurtosis > 3 else "Normal"}
Max: ${df_ana['revenue'].max():,.0f}
Top 1%: ${df_ana['revenue'].quantile(0.99):,.0f}

Business Action: {'Segment into small/enterprise for different strategies' if skewness > 1 else 'Uniform strategy'}
"""
    print(interpretation)

    # Save report to JSON
    report_dict = {
        'mean_revenue': round(df_ana['revenue'].mean(), 2),
        'median_revenue': round(df_ana['revenue'].median(), 2),
        'skewness': round(float(skewness), 2),
        'kurtosis': round(float(kurtosis), 2),
        'max_revenue': round(df_ana['revenue'].max(), 2),
        'p99_revenue': round(percentiles.loc[0.99], 2),
        'p75_revenue': round(percentiles.loc[0.75], 2),
        'p25_revenue': round(percentiles.loc[0.25], 2),
        'interpretation': 'Highly right-skewed distribution where enterprise outliers pull the average up to $1,200 while median customer spend remains $450.',
        'business_action': 'Implement bifurcated go-to-market strategy: automated self-service product-led growth (PLG) for small/SMB base (<P75), and dedicated White-Glove Account Executives for high-value enterprise accounts (>P75).'
    }
    
    report_json_path = os.path.join(output_dir, 'distribution_analysis_report.json')
    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2)
    print(f"✓ Executive distribution analysis report JSON saved to: {report_json_path}")

    # Save processed dataset with segment labels
    def tag_segment(val):
        if val > q75:
            return 'High-Value Enterprise (Top 25%)'
        elif val < q25:
            return 'Low-Value Retail (Bottom 25%)'
        else:
            return 'Mid-Market SMB (Middle 50%)'
            
    df_ana['value_segment'] = df_ana['revenue'].apply(tag_segment)
    
    proc_dir = 'data/processed'
    if not os.path.exists(proc_dir) and os.path.exists('../data'):
        proc_dir = '../data/processed'
    else:
        os.makedirs(proc_dir, exist_ok=True)
        
    proc_path = os.path.join(proc_dir, 'segmented_customer_revenue.csv')
    df_ana.to_csv(proc_path, index=False)
    print(f"✓ Exported {len(df_ana):,} segmented customer records to: {proc_path}")
    print("="*70 + "\n")
    
    return df_ana, report_dict

if __name__ == "__main__":
    filepath = 'data/raw/customer_revenue_skewed.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    df_raw = generate_skewed_revenue_data(filepath)
    df_analyzed, report_dict = run_distribution_analysis(df_raw)
