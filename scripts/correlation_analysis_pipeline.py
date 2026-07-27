import os
import sys
import json
import pandas as pd
import numpy as np
import seaborn as sns

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

def generate_churn_dataset(filepath='data/raw/customer_churn_features.csv', n_customers=2500):
    """Generate synthetic customer churn dataset with known confounding variables and collinearity."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    print(f"Generating synthetic {n_customers:,}-row customer churn dataset with confounding variables...")
    
    # 1. Latent / Confounding variable: Customer Pain Index (0 to 100)
    # This represents underlying product bugs, usability hurdles, and service degradation
    customer_pain = np.random.uniform(0, 100, size=n_customers)
    
    # 2. Support Tickets: Heavily driven by customer_pain (r ~ 0.8 with churn)
    support_tickets = np.round(customer_pain * 0.15 + np.random.normal(0, 0.4, size=n_customers)).astype(int)
    support_tickets = np.clip(support_tickets, 0, 25)
    
    # 3. Churn: Driven by customer pain (thus tickets and churn correlate heavily via pain)
    churn_prob = 1.0 / (1.0 + np.exp(-(customer_pain - 50.0) / 6.0))
    churn = (np.random.uniform(0, 1, size=n_customers) < churn_prob).astype(int)
    
    # 4. Transactions per month: Inversely driven by pain + baseline engagement
    transactions_per_month = np.round(np.maximum(0.5, 20.0 - customer_pain * 0.15 + np.random.normal(0, 2.0, size=n_customers)), 2)
    
    # 5. Engagement Score: Highly collinear with transactions_per_month (r ~ 0.92)
    engagement = np.round(transactions_per_month * 4.8 + np.random.normal(0, 10.5, size=n_customers), 2)
    
    # 6. Tenure Days and Revenue (orthogonal/slightly correlated features)
    tenure_days = np.random.randint(30, 1500, size=n_customers)
    revenue = np.round(transactions_per_month * np.random.uniform(30.0, 120.0, size=n_customers), 2)
    
    df = pd.DataFrame({
        'customer_id': range(10001, 10001 + n_customers),
        'customer_pain_index': np.round(customer_pain, 1), # Latent confounder
        'support_tickets': support_tickets,
        'churn': churn,
        'transactions_per_month': transactions_per_month,
        'engagement': engagement,
        'tenure_days': tenure_days,
        'revenue': revenue
    })
    
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic churn dataset created at {filepath} ({len(df):,} records)")
    print(f"  • Overall Churn Rate:           {df['churn'].mean()*100:.1f}%")
    print(f"  • Support Tickets Range:        {df['support_tickets'].min()} to {df['support_tickets'].max()}")
    print(f"  • Target Collinear Pair Corr:   r = {df['transactions_per_month'].corr(df['engagement']):.2f}\n")
    return df

def run_correlation_analysis_pipeline(df):
    """Execute all 5 correlation vs causation tasks, heatmap visualization, and feature selection."""
    print("="*70)
    print("CORRELATION VS CAUSATION & MULTICOLLINEARITY FEATURE SELECTION")
    print("="*70)
    df_ana = df.copy()
    
    # Drop ID and latent confounder for the predictive modeling feature matrix
    # We analyze observables as a data scientist would in production
    df_model = df_ana.drop(columns=['customer_id', 'customer_pain_index'])
    
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)

    # Task 1: Compute Pearson and Spearman Correlation
    print("\n--- TASK 1: COMPUTE PEARSON AND SPEARMAN CORRELATION WITH CHURN ---")
    pearson_corr = df_model.corr(method='pearson')
    spearman_corr = df_model.corr(method='spearman')

    comparison = pd.DataFrame({
        'pearson': pearson_corr['churn'].round(3),
        'spearman': spearman_corr['churn'].round(3),
        'abs_diff': (pearson_corr['churn'] - spearman_corr['churn']).abs().round(3)
    }).sort_values(by='pearson', ascending=False)
    
    print("Correlation Comparison Table (Target: churn):")
    print(comparison.to_string())
    print("\n[Methodology Insights]:")
    print("  • Pearson evaluates linear relationships ($y = mx + c$), sensitive to extreme outliers and non-linear scaling.")
    print("  • Spearman evaluates monotonic rank relationships based on order, providing robustness against non-linear distributions.")

    # Task 2: Visualize Correlation Heatmap
    print("\n--- TASK 2: VISUALIZE FEATURE CORRELATION HEATMAP ---")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pearson_corr, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, center=0, 
                cbar_kws={'label': 'Pearson Correlation Coefficient (r)'}, ax=ax, linewidths=0.5)
    ax.set_title('Feature Correlation Matrix (Pearson)', fontweight='bold', fontsize=14, pad=15)
    plt.tight_layout()
    
    heatmap_path = os.path.join(output_dir, 'correlation_heatmap.png')
    plt.savefig(heatmap_path, dpi=300)
    plt.close()
    print(f"✓ Feature correlation heatmap saved to: {heatmap_path}")

    # Task 3: Identify Strongly Correlated Pairs
    print("\n--- TASK 3: IDENTIFY STRONGLY CORRELATED FEATURE PAIRS (|r| > 0.7) ---")
    corr_flat = pearson_corr.unstack()
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False)

    # Exclude self-correlation (r=1.0) and deduplicate mirror pairs
    strong_pairs = strong[strong < 0.999]
    
    # Filter to unique pairs
    seen = set()
    unique_strong = []
    for (f1, f2), val in strong_pairs.items():
        pair = tuple(sorted([f1, f2]))
        if pair not in seen:
            seen.add(pair)
            unique_strong.append(((f1, f2), round(val, 3)))
            
    print("Top Strongly Correlated Pairs (Excluding Self-Correlation r=1.0):")
    for (f1, f2), val in unique_strong[:10]:
        print(f"  • {f1:<22} <-> {f2:<22} : r = {val:>5.2f}")

    # Task 4: Business Interpretation (Correlation vs Causation Confounder Analysis)
    print("\n--- TASK 4: BUSINESS INTERPRETATION (CAUSATION VS CONFOUNDING SIGNALS) ---")
    # Verify support tickets correlation with churn
    tix_churn_r = round(float(pearson_corr.loc['support_tickets', 'churn']), 2)
    
    analysis = {
        'support_tickets <-> churn': {
            'correlation': tix_churn_r,
            'possible_directions': [
                'support_tickets → churn (customer gives up after contacting support)',
                'churn → support_tickets (unhappy customers contact support before leaving)',
                'customer_pain → both (underlying issue causes both)'
            ],
            'data_indicates': 'Likely customer_pain is the confounder; tickets are symptom not cause',
            'action': 'Focus on reducing pain, not blocking tickets'
        },
        'engagement <-> transactions_per_month': {
            'correlation': round(float(pearson_corr.loc['engagement', 'transactions_per_month']), 2),
            'possible_directions': [
                'transactions → engagement (higher order frequency drives platform activity metrics)',
                'engagement → transactions (active browsing drives purchase conversion)',
                'product_value → both (core product utility drives both metrics)'
            ],
            'data_indicates': 'Severe multicollinearity / redundancy between behavioral metrics',
            'action': 'Drop redundant feature to prevent model instability and variance inflation'
        }
    }

    print(json.dumps(analysis, indent=2))
    
    causation_path = os.path.join(output_dir, 'correlation_causation_analysis.json')
    with open(causation_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"✓ Executive correlation vs causation report saved to: {causation_path}")

    # Task 5: Feature Selection Based on Correlation
    print("\n--- TASK 5: MULTICOLLINEARITY FEATURE SELECTION ---")
    # High correlation means redundancy - keep more interpretable feature
    df_features = df_model[['engagement', 'transactions_per_month', 'support_tickets', 'churn']]

    print("Initial 4-Feature Sub-Matrix Correlation:")
    print(df_features.corr().round(2))

    # transactions_per_month and engagement are r=0.92 (collinear)
    # Drop redundant, keep interpretable
    print("\n[Feature Selection Action]: Dropping 'engagement' (collinear with 'transactions_per_month', r~0.92)...")
    df_features = df_features.drop('engagement', axis=1)

    print("\nFinal Clean Feature Matrix Correlation (Post-Deduplication):")
    final_corr = df_features.corr().round(2)
    print(final_corr)
    
    print("\n[Why Remove Collinear Features?]:")
    print("  • Multicollinearity inflates standard errors of regression coefficients, making model weights unstable and uninterpretable.")
    print("  • Keeping 'transactions_per_month' over 'engagement' preserves clear, actionable business domain meaning (orders per 30 days vs an arbitrary composite score).")

    # Export clean feature dataset
    proc_dir = 'data/processed'
    if not os.path.exists(proc_dir) and os.path.exists('../data'):
        proc_dir = '../data/processed'
    else:
        os.makedirs(proc_dir, exist_ok=True)
        
    proc_path = os.path.join(proc_dir, 'selected_churn_features.csv')
    df_features.to_csv(proc_path, index=False)
    print(f"\n✓ Exported clean 3-feature predictive dataset ({len(df_features):,} records) to: {proc_path}")
    print("="*70 + "\n")
    
    return df_features, analysis

if __name__ == "__main__":
    filepath = 'data/raw/customer_churn_features.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    df_raw = generate_churn_dataset(filepath)
    df_clean, analysis = run_correlation_analysis_pipeline(df_raw)
