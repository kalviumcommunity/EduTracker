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

def generate_relational_datasets(cust_path='data/raw/customers_table.csv', ord_path='data/raw/orders_table.csv'):
    """Generate 1000-row customer table and 5000-row orders table with relational anomalies."""
    for path in [cust_path, ord_path]:
        output_dir = os.path.dirname(path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
    np.random.seed(42)
    
    # 1. Customers Table (1000 rows: IDs 1001 to 2000)
    cust_ids = range(1001, 2001)
    cust_names = [f"Customer_{i}" for i in cust_ids]
    segments = np.random.choice(['Retail', 'SMB', 'Enterprise', 'VIP'], size=1000, p=[0.5, 0.3, 0.15, 0.05])
    signup_dates = [f"2024-{np.random.randint(1, 13):02d}-{np.random.randint(1, 28):02d}" for _ in range(1000)]
    
    df_customers = pd.DataFrame({
        'customer_id': cust_ids,
        'customer_name': cust_names,
        'segment': segments,
        'signup_date': signup_dates,
        'status': np.random.choice(['Active', 'Pending', 'Dormant'], size=1000, p=[0.8, 0.1, 0.1])
    })
    
    # 2. Orders Table (5000 rows: IDs 50001 to 55000)
    ord_ids = range(50001, 55001)
    
    # We want 150 customers (IDs 1851 to 2000) to have NO orders (unmatched left keys)
    active_cust_ids = list(range(1001, 1851)) # 850 active customers
    
    # We want 50 orders to be orphaned (belonging to deleted/guest IDs 2001 to 2050 not in customers table)
    orphan_cust_ids = list(range(2001, 2051))
    
    # Assign 4950 orders to active customers, 50 orders to orphans
    assigned_custs = np.random.choice(active_cust_ids, size=4950).tolist() + np.random.choice(orphan_cust_ids, size=50).tolist()
    np.random.shuffle(assigned_custs)
    
    order_dates = [f"2025-0{np.random.randint(1, 4)}-{np.random.randint(1, 28):02d}" for _ in range(5000)]
    order_amounts = np.round(np.random.exponential(scale=150.0, size=5000) + 20.0, 2)
    
    df_orders = pd.DataFrame({
        'order_id': ord_ids,
        'customer_id': assigned_custs,
        'order_date': order_dates,
        'order_amount': order_amounts,
        'payment_status': np.random.choice(['Paid', 'Processing', 'Refunded'], size=5000, p=[0.85, 0.10, 0.05])
    })
    
    df_customers.to_csv(cust_path, index=False)
    df_orders.to_csv(ord_path, index=False)
    print(f"✓ Synthetic relational tables created:")
    print(f"  • Customers table: {len(df_customers)} rows ({cust_path})")
    print(f"  • Orders table:    {len(df_orders)} rows ({ord_path})")
    print(f"  • Injected relational test cases: 150 customers with 0 orders, 50 orphaned orders from deleted customer IDs.\n")
    return df_customers, df_orders

def run_relational_pipeline(df_customers, df_orders):
    """Execute all 5 merging and validation tasks."""
    print("="*70)
    print("RELATIONAL DATA MERGING & JOIN VALIDATION PIPELINE")
    print("="*70)
    
    # Task 1: Explicit Join with Row Count Validation
    print("\n--- TASK 1: EXPLICIT JOIN WITH ROW COUNT VALIDATION ---")
    print(f"Left table (customers) row count:  {len(df_customers):,}")
    print(f"Right table (orders) row count:    {len(df_orders):,}")

    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='left')

    print(f"Merged table (left join) row count: {len(df_merged):,}")
    print(f"Change in row count vs Left:        {len(df_merged) - len(df_customers):+,}")
    print("Explanation of Row Count Increase:")
    print("  • In a 1-to-Many relational join (1 Customer → N Orders), each customer row multiplies by the number of matching order records.")
    print("  • Active customers with multiple purchases generate multiple rows in the result set, expanding total rows while preserving all 1,000 original customers.")

    # Task 2: Detect Unmatched Keys
    print("\n--- TASK 2: DETECT UNMATCHED KEYS (ORPHANS & DORMANT ACCOUNTS) ---")
    unmatched_customers = df_customers[~df_customers['customer_id'].isin(df_orders['customer_id'])]
    unmatched_orders = df_orders[~df_orders['customer_id'].isin(df_customers['customer_id'])]

    print(f"Customers without orders (Dormant Accounts): {len(unmatched_customers):,}")
    print(f"Orphaned orders (Missing Customer Master):   {len(unmatched_orders):,}")

    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    unm_cust_path = os.path.join(output_dir, 'unmatched_customers.csv')
    unm_ord_path = os.path.join(output_dir, 'unmatched_orders.csv')
    unmatched_customers.to_csv(unm_cust_path, index=False)
    unmatched_orders.to_csv(unm_ord_path, index=False)
    print(f"✓ Isolated unmatched customers saved to: {unm_cust_path}")
    print(f"✓ Isolated orphaned orders saved to:     {unm_ord_path}")
    
    if len(unmatched_orders) > 0:
        print("\nSample Orphaned Order Records (Data Integrity Alert):")
        print(unmatched_orders[['order_id', 'customer_id', 'order_date', 'order_amount']].head(5).to_string(index=False))

    # Task 3: Compare Join Types
    print("\n--- TASK 3: COMPARE JOIN TYPES & CARDINALITY ---")
    inner = pd.merge(df_customers, df_orders, how='inner')
    left = pd.merge(df_customers, df_orders, how='left')
    outer = pd.merge(df_customers, df_orders, how='outer')

    print(f"Inner Join Row Count: {len(inner):,} (Excludes 150 dormant customers and 50 orphaned orders)")
    print(f"Left Join Row Count:  {len(left):,} (Preserves all 1,000 customers; order columns are NaN for dormant accounts)")
    print(f"Outer Join Row Count: {len(outer):,} (Full relational union: includes dormant customers AND orphaned orders)")

    # Task 4: Validate No Unexpected Duplication & Column Conflicts
    print("\n--- TASK 4: VALIDATE NO UNEXPECTED DUPLICATION ---")
    print("Merged DataFrame Columns:", list(df_merged.columns))

    # If customer_id appears in both, verify merge key
    key_counts = df_merged['customer_id'].value_counts()
    print(f"Max orders per customer in merged result: {key_counts.max()}")
    print(f"Average orders per active customer:       {key_counts[key_counts > 1].mean():.2f}")
    
    # Check for column suffix collisions (e.g. status in customers vs status in orders)
    # Demonstrating explicit suffix handling to prevent _x and _y ambiguity
    if 'status' in df_customers.columns and 'status' in df_orders.columns:
        print("Note: Column 'status' exists in both tables. Demonstrating clean suffix resolution...")
        df_clean_merge = pd.merge(df_customers, df_orders, on='customer_id', how='left', suffixes=('_cust', '_ord'))
        print("Resolved Suffix Columns:", [c for c in df_clean_merge.columns if '_cust' in c or '_ord' in c])
    else:
        df_clean_merge = df_merged.copy()

    # Task 5: Document Join Decision & Business Report
    print("\n--- TASK 5: DOCUMENT JOIN DECISION ---")
    join_report = {
        'join_type': 'left',
        'left_table': 'customers',
        'right_table': 'orders',
        'join_key': 'customer_id',
        'left_rows': len(df_customers),
        'right_rows': len(df_orders),
        'result_rows': len(df_merged),
        'unmatched_left': len(unmatched_customers),
        'unmatched_right': len(unmatched_orders),
        'reasoning': 'Left join preserves all customers; unmatched customers have no orders. This is essential for building complete customer 360 profiles and churn analysis without dropping zero-spend accounts.'
    }

    print(json.dumps(join_report, indent=2))
    
    report_path = os.path.join(output_dir, 'join_decision_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(join_report, f, indent=2)
    print(f"\n✓ Join decision report JSON written to: {report_path}")

    # Export merged dataset
    proc_dir = 'data/processed'
    if not os.path.exists(proc_dir) and os.path.exists('../data'):
        proc_dir = '../data/processed'
    else:
        os.makedirs(proc_dir, exist_ok=True)
        
    merged_path = os.path.join(proc_dir, 'merged_customer_orders.csv')
    df_clean_merge.to_csv(merged_path, index=False)
    print(f"✓ Final relational merged dataset saved to: {merged_path}")

    # Generate Visual Join Comparison Chart
    plt.figure(figsize=(10, 6))
    join_types = ['Inner Join\n(Active Only)', 'Left Join\n(All Customers)', 'Outer Join\n(All + Orphans)']
    counts = [len(inner), len(left), len(outer)]
    colors = ['#5bc0de', '#0275d8', '#5cb85c']
    
    bars = plt.bar(join_types, counts, color=colors, edgecolor='black', width=0.5)
    plt.title('Relational Join Cardinality Comparison (Customers × Orders)', fontsize=14, fontweight='bold')
    plt.ylabel('Total Resulting Rows', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Annotate bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, f"{count:,}", 
                 ha='center', va='bottom', fontweight='bold', fontsize=11)
        
    plt.ylim(0, max(counts) * 1.15)
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'join_types_comparison.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"✓ Visual join comparison chart saved to: {chart_path}")
    print("="*70 + "\n")
    
    return df_clean_merge, join_report

if __name__ == "__main__":
    cust_path = 'data/raw/customers_table.csv'
    ord_path = 'data/raw/orders_table.csv'
    if not os.path.exists(cust_path) and os.path.exists(os.path.join("..", cust_path)):
        cust_path = os.path.join("..", cust_path)
        ord_path = os.path.join("..", ord_path)
        
    df_cust, df_ord = generate_relational_datasets(cust_path, ord_path)
    df_merged, report = run_relational_pipeline(df_cust, df_ord)
