import os
import sys
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

def generate_synthetic_outlier_data(filepath='data/raw/customer_revenue_outliers.csv'):
    """Generate sample customer revenue and age dataset containing extreme outliers."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    n_normal = 495
    
    # Normal customer records
    customer_ids = range(10001, 10001 + n_normal + 5)
    # Revenue normally/exponentially distributed around $450
    normal_rev = np.round(np.random.gamma(shape=3.0, scale=150.0, size=n_normal), 2)
    # Age uniformly distributed between 18 and 75
    normal_age = np.random.randint(18, 76, size=n_normal)
    
    # Extreme Outliers
    outlier_rev = np.array([500000.00, 250000.00, 180000.00, 450.50, 620.00])
    outlier_age = np.array([35, 42, 29, 165, 195]) # 165 and 195 are impossible human ages
    
    all_rev = np.concatenate([normal_rev, outlier_rev])
    all_age = np.concatenate([normal_age, outlier_age])
    
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'revenue': all_rev,
        'age': all_age,
        'customer_segment': np.random.choice(['Retail', 'SMB', 'Enterprise'], size=len(all_rev))
    })
    
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic outlier dataset generated at {filepath} ({len(df)} records)")
    print(f"  Extreme revenue values included: ${df['revenue'].max():,.2f}")
    print(f"  Impossible age values included:  {df['age'].max()} years old\n")
    return df

def task_1_zscore_detection(df):
    """Task 1: Z-Score Outlier Detection."""
    print("="*70)
    print("TASK 1: Z-SCORE OUTLIER DETECTION (±3 STANDARD DEVIATIONS)")
    print("="*70)
    df_z = df.copy()
    
    # Revenue Z-Score
    df_z['revenue_zscore'] = np.abs(stats.zscore(df_z['revenue']))
    z_outliers_rev = df_z[df_z['revenue_zscore'] > 3]
    
    print(f"Revenue Mean: ${df_z['revenue'].mean():,.2f} | Std Dev: ${df_z['revenue'].std():,.2f}")
    print(f"Z-score revenue outliers identified: {len(z_outliers_rev)}")
    if len(z_outliers_rev) > 0:
        print("Sample extreme revenue outliers (> 3 SD):")
        print(z_outliers_rev[['customer_id', 'revenue', 'revenue_zscore']].to_string(index=False))
        
    # Age Z-Score
    df_z['age_zscore'] = np.abs(stats.zscore(df_z['age']))
    z_outliers_age = df_z[df_z['age_zscore'] > 3]
    print(f"\nAge Mean: {df_z['age'].mean():.1f} | Std Dev: {df_z['age'].std():.1f}")
    print(f"Z-score age outliers identified: {len(z_outliers_age)}")
    if len(z_outliers_age) > 0:
        print("Sample impossible age outliers (> 3 SD):")
        print(z_outliers_age[['customer_id', 'age', 'age_zscore']].to_string(index=False))
        
    print("="*70 + "\n")
    return df_z

def task_2_iqr_detection(df):
    """Task 2: IQR Outlier Detection (1.5 × IQR from quartiles)."""
    print("="*70)
    print("TASK 2: IQR OUTLIER DETECTION (1.5 × IQR FROM QUARTILES)")
    print("="*70)
    df_iqr = df.copy()
    
    # Revenue IQR
    Q1_rev = df_iqr['revenue'].quantile(0.25)
    Q3_rev = df_iqr['revenue'].quantile(0.75)
    IQR_rev = Q3_rev - Q1_rev
    lower_rev = Q1_rev - 1.5 * IQR_rev
    upper_rev = Q3_rev + 1.5 * IQR_rev
    
    df_iqr['is_outlier_iqr_rev'] = (df_iqr['revenue'] < lower_rev) | (df_iqr['revenue'] > upper_rev)
    print(f"[Revenue IQR Analysis]")
    print(f"  Q1 (25th percentile): ${Q1_rev:,.2f} | Q3 (75th percentile): ${Q3_rev:,.2f} | IQR: ${IQR_rev:,.2f}")
    print(f"  Lower Threshold: ${lower_rev:,.2f} | Upper Threshold: ${upper_rev:,.2f}")
    print(f"  IQR revenue outliers identified: {df_iqr['is_outlier_iqr_rev'].sum()}")
    
    # Age IQR
    Q1_age = df_iqr['age'].quantile(0.25)
    Q3_age = df_iqr['age'].quantile(0.75)
    IQR_age = Q3_age - Q1_age
    lower_age = Q1_age - 1.5 * IQR_age
    upper_age = Q3_age + 1.5 * IQR_age
    
    df_iqr['is_outlier_iqr_age'] = (df_iqr['age'] < lower_age) | (df_iqr['age'] > upper_age)
    print(f"\n[Age IQR Analysis]")
    print(f"  Q1 (25th percentile): {Q1_age:.1f} | Q3 (75th percentile): {Q3_age:.1f} | IQR: {IQR_age:.1f}")
    print(f"  Lower Threshold: {lower_age:.1f} | Upper Threshold: {upper_age:.1f}")
    print(f"  IQR age outliers identified: {df_iqr['is_outlier_iqr_age'].sum()}")
    
    print("="*70 + "\n")
    return df_iqr, (lower_rev, upper_rev), (lower_age, upper_age)

def task_3_cap_outliers(df, rev_bounds, age_bounds):
    """Task 3: Cap Outliers at Boundaries (Winsorizing/Clipping)."""
    print("="*70)
    print("TASK 3: CAP OUTLIERS AT BOUNDARIES (WINSORIZATION STRATEGY)")
    print("="*70)
    df_capped = df.copy()
    lower_rev, upper_rev = rev_bounds
    lower_age, upper_age = age_bounds
    
    # For revenue, clip at lower (or 0) and upper IQR threshold
    clip_lower_rev = max(0.0, lower_rev) # Revenue cannot be negative in this domain
    df_capped['revenue_capped'] = df_capped['revenue'].clip(lower=clip_lower_rev, upper=upper_rev)
    
    # For age, clip at lower (e.g. 18) and upper IQR threshold (or realistic human cap ~100)
    clip_lower_age = max(18, lower_age)
    clip_upper_age = min(100, upper_age)
    df_capped['age_capped'] = df_capped['age'].clip(lower=clip_lower_age, upper=clip_upper_age)
    
    print("[Revenue Capping Verification]")
    print(f"Before: min=${df_capped['revenue'].min():,.2f}, max=${df_capped['revenue'].max():,.2f}")
    print(f"After:  min=${df_capped['revenue_capped'].min():,.2f}, max=${df_capped['revenue_capped'].max():,.2f}")
    
    print(f"\n[Age Capping Verification]")
    print(f"Before: min={df_capped['age'].min()} years, max={df_capped['age'].max()} years")
    print(f"After:  min={df_capped['age_capped'].min():.1f} years, max={df_capped['age_capped'].max():.1f} years")
    
    print("="*70 + "\n")
    return df_capped

def task_4_flag_outliers(df):
    """Task 4: Flag Outliers with Binary Column (Anomaly Flagging)."""
    print("="*70)
    print("TASK 4: FLAG OUTLIERS WITH BINARY COLUMN (NON-DESTRUCTIVE MARKING)")
    print("="*70)
    df_flagged = df.copy()
    
    # Use both methods and combine
    df_flagged['is_outlier'] = (df_flagged['is_outlier_iqr_rev']) | \
                               (df_flagged['revenue_zscore'] > 3) | \
                               (df_flagged['is_outlier_iqr_age']) | \
                               (df_flagged['age_zscore'] > 3)
                               
    # Downstream analysis can filter or weight separately
    normal = df_flagged[~df_flagged['is_outlier']]
    anomalies = df_flagged[df_flagged['is_outlier']]

    print(f"Total records evaluated: {len(df_flagged)}")
    print(f"Normal records:          {len(normal)} ({len(normal)/len(df_flagged)*100:.1f}%)")
    print(f"Anomalies identified:    {len(anomalies)} ({len(anomalies)/len(df_flagged)*100:.1f}%)")
    
    if len(anomalies) > 0:
        print("\nSummary of Flagged Anomalies:")
        print(anomalies[['customer_id', 'revenue', 'age', 'revenue_zscore', 'age_zscore']].to_string(index=False))
        
    print("\n[Business Justification: Why Flag and Cap vs. Remove Data?]")
    print("  • Non-Destructive Audit Trail: Deleting rows permanently destroys customer transaction history and reduces sample size.")
    print("  • Fraud & VIP Detection: Flagging allows specialized machine learning models (e.g. isolation forests) to study extreme spenders ($500k VIPs) or data entry bugs (150+ age) without contaminating standard linear regression models.")
    print("  • Parametric Protection: Capped columns (`revenue_capped`, `age_capped`) protect standard averages and linear assumptions from distortion while keeping all rows in the dataset.")
    print("="*70 + "\n")
    return df_flagged

def task_5_create_cleaning_log(df, rev_bounds, age_bounds):
    """Task 5: Create Cleaning Log and Document Transformations."""
    print("="*70)
    print("TASK 5: CREATE CLEANING LOG FOR AUDIT COMPLIANCE")
    print("="*70)
    
    lower_rev, upper_rev = rev_bounds
    lower_age, upper_age = age_bounds
    
    rev_affected = int(((df['revenue'] < max(0.0, lower_rev)) | (df['revenue'] > upper_rev)).sum())
    age_affected = int(((df['age'] < max(18, lower_age)) | (df['age'] > min(100, upper_age))).sum())
    
    cleaning_log = [
        {
            'column': 'revenue',
            'method': 'IQR + Z-Score',
            'action': 'cap (Winsorize at 1.5×IQR upper threshold)',
            'threshold_lower': max(0.0, lower_rev),
            'threshold_upper': upper_rev,
            'affected_rows': rev_affected,
            'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'column': 'age',
            'method': 'IQR + Domain Rule (Max realistic age 100)',
            'action': 'cap (Winsorize at realistic physiological boundary)',
            'threshold_lower': max(18, lower_age),
            'threshold_upper': min(100, upper_age),
            'affected_rows': age_affected,
            'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    log_df = pd.DataFrame(cleaning_log)
    
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    log_path = os.path.join(output_dir, 'cleaning_log.csv')
    log_df.to_csv(log_path, index=False)
    
    print(f"✓ Cleaning log successfully written to {log_path}\n")
    print("Cleaning Log Contents:")
    print(log_df.to_string(index=False))
    print("="*70 + "\n")
    return log_df

def generate_outlier_plots(df):
    """Generate visual before/after distributions for report."""
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Revenue Before
    axes[0, 0].boxplot(df['revenue'], orientation='horizontal', patch_artist=True, boxprops=dict(facecolor='#ff9999'))
    axes[0, 0].set_title('Revenue Before Capping (Notice $500k Outlier)', fontweight='bold')
    axes[0, 0].set_xlabel('Revenue ($)')
    axes[0, 0].grid(True, linestyle='--', alpha=0.5)
    
    # 2. Revenue After
    axes[0, 1].hist(df['revenue_capped'], bins=30, color='#66b3ff', edgecolor='black')
    axes[0, 1].set_title('Revenue After Capping (Winsorized Distribution)', fontweight='bold')
    axes[0, 1].set_xlabel('Capped Revenue ($)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(True, linestyle='--', alpha=0.5)
    
    # 3. Age Before
    axes[1, 0].boxplot(df['age'], orientation='horizontal', patch_artist=True, boxprops=dict(facecolor='#ffcc99'))
    axes[1, 0].set_title('Age Before Capping (Notice 150+ Impossible Ages)', fontweight='bold')
    axes[1, 0].set_xlabel('Age (Years)')
    axes[1, 0].grid(True, linestyle='--', alpha=0.5)
    
    # 4. Age After
    axes[1, 1].hist(df['age_capped'], bins=20, color='#99ff99', edgecolor='black')
    axes[1, 1].set_title('Age After Capping (Standard Human Age Range)', fontweight='bold')
    axes[1, 1].set_xlabel('Capped Age (Years)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'outlier_analysis_plots.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"✓ Visual before/after outlier analysis plots saved to {plot_path}")

if __name__ == "__main__":
    filepath = 'data/raw/customer_revenue_outliers.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    # Generate dataset
    df_raw = generate_synthetic_outlier_data(filepath)
    
    # Task 1: Z-Score Detection
    df_step1 = task_1_zscore_detection(df_raw)
    
    # Task 2: IQR Detection
    df_step2, rev_bounds, age_bounds = task_2_iqr_detection(df_step1)
    
    # Task 3: Cap Outliers
    df_step3 = task_3_cap_outliers(df_step2, rev_bounds, age_bounds)
    
    # Task 4: Flag Outliers
    df_step4 = task_4_flag_outliers(df_step3)
    
    # Task 5: Cleaning Log
    task_5_create_cleaning_log(df_step4, rev_bounds, age_bounds)
    
    # Generate visual plots
    generate_outlier_plots(df_step4)
    
    # Save cleaned dataset
    output_dir = 'data/processed'
    if not os.path.exists(output_dir) and os.path.exists('../data'):
        output_dir = '../data/processed'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    proc_path = os.path.join(output_dir, 'outlier_cleaned_data.csv')
    df_step4.to_csv(proc_path, index=False)
    print(f"\n✓ Cleaned customer dataset with outlier flags & capped values saved to {proc_path}")
