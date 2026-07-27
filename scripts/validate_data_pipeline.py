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

def generate_unvalidated_dataset(filepath='data/raw/unvalidated_campaign_data.csv'):
    """Generate sample customer campaign dataset containing various validation anomalies."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    np.random.seed(42)
    n_clean = 500
    
    # Clean records
    customer_ids = [f"CUST-{i}" for i in range(10001, 10001 + n_clean)]
    ages = np.random.randint(18, 75, size=n_clean)
    prices = np.round(np.random.uniform(10.0, 500.0, size=n_clean), 2)
    
    # Birth dates corresponding roughly to ages
    current_year = 2025
    birth_years = current_year - ages
    birth_dates = [f"{year}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 28):02d}" for year in birth_years]
    
    emails = [f"user_{i}@example.com" for i in range(1, n_clean + 1)]
    phones = [f"{np.random.randint(6, 10)}{np.random.randint(100000000, 999999999)}" for _ in range(n_clean)]
    
    start_dates = [f"2025-0{np.random.randint(1, 6)}-01" for _ in range(n_clean)]
    end_dates = [f"2025-0{np.random.randint(6, 10)}-01" for _ in range(n_clean)]
    
    df_clean = pd.DataFrame({
        'customer_id': customer_ids,
        'age': ages,
        'birth_date': birth_dates,
        'price': prices,
        'email': emails,
        'phone': phones,
        'start_date': start_dates,
        'end_date': end_dates
    })
    
    # Dirty / Anomaly records
    dirty_records = [
        # 1. Birth date in year 2050 (Future birth date)
        {'customer_id': 'CUST-20001', 'age': 25, 'birth_date': '2050-05-15', 'price': 99.99, 'email': 'futurist@example.com', 'phone': '9876543210', 'start_date': '2025-01-01', 'end_date': '2025-02-01'},
        {'customer_id': 'CUST-20002', 'age': 30, 'birth_date': '2065-11-20', 'price': 149.50, 'email': 'time_travel@test.org', 'phone': '8765432109', 'start_date': '2025-02-01', 'end_date': '2025-03-01'},
        # 2. Impossible ages (Negative and >150)
        {'customer_id': 'CUST-20003', 'age': -5, 'birth_date': '2030-01-01', 'price': 50.00, 'email': 'negative_age@test.com', 'phone': '7654321098', 'start_date': '2025-01-15', 'end_date': '2025-02-15'},
        {'customer_id': 'CUST-20004', 'age': 185, 'birth_date': '1840-06-10', 'price': 75.00, 'email': 'vampire@old.org', 'phone': '6543210987', 'start_date': '2025-03-01', 'end_date': '2025-04-01'},
        # 3. Negative prices
        {'customer_id': 'CUST-20005', 'age': 40, 'birth_date': '1985-04-12', 'price': -49.99, 'email': 'refund_bug@store.com', 'phone': '9123456780', 'start_date': '2025-01-01', 'end_date': '2025-05-01'},
        {'customer_id': 'CUST-20006', 'age': 55, 'birth_date': '1970-08-22', 'price': -150.00, 'email': 'glitch@shop.net', 'phone': '8123456789', 'start_date': '2025-02-01', 'end_date': '2025-06-01'},
        # 4. Missing customer_id when required
        {'customer_id': None, 'age': 29, 'birth_date': '1996-03-14', 'price': 120.00, 'email': 'anonymous1@test.com', 'phone': '9012345678', 'start_date': '2025-01-10', 'end_date': '2025-03-10'},
        {'customer_id': np.nan, 'age': 34, 'birth_date': '1991-07-19', 'price': 210.00, 'email': 'anonymous2@test.com', 'phone': '8012345678', 'start_date': '2025-02-15', 'end_date': '2025-04-15'},
        # 5. Missing email or phone
        {'customer_id': 'CUST-20009', 'age': 42, 'birth_date': '1983-09-09', 'price': 88.50, 'email': None, 'phone': '7012345678', 'start_date': '2025-01-01', 'end_date': '2025-02-01'},
        {'customer_id': 'CUST-20010', 'age': 50, 'birth_date': '1975-12-12', 'price': 300.00, 'email': 'no_phone@test.com', 'phone': None, 'start_date': '2025-03-01', 'end_date': '2025-05-01'},
        # 6. Format Pattern validation failures (No @ in email, phone not 10 digits)
        {'customer_id': 'CUST-20011', 'age': 22, 'birth_date': '2003-02-14', 'price': 45.00, 'email': 'invalid_email_domain.com', 'phone': '9876543210', 'start_date': '2025-01-01', 'end_date': '2025-02-01'},
        {'customer_id': 'CUST-20012', 'age': 27, 'birth_date': '1998-11-11', 'price': 65.00, 'email': 'bad_user@test', 'phone': '12345', 'start_date': '2025-02-01', 'end_date': '2025-03-01'},
        {'customer_id': 'CUST-20013', 'age': 31, 'birth_date': '1994-05-05', 'price': 110.00, 'email': 'valid@test.com', 'phone': '9876543210987654', 'start_date': '2025-01-01', 'end_date': '2025-04-01'},
        # 7. Business Rule validation: end_date before start_date
        {'customer_id': 'CUST-20014', 'age': 38, 'birth_date': '1987-10-10', 'price': 190.00, 'email': 'chrono_error1@test.com', 'phone': '9112233445', 'start_date': '2025-06-01', 'end_date': '2025-05-01'},
        {'customer_id': 'CUST-20015', 'age': 45, 'birth_date': '1980-01-20', 'price': 250.00, 'email': 'chrono_error2@test.com', 'phone': '9223344556', 'start_date': '2025-09-15', 'end_date': '2025-01-15'}
    ]
    
    df_dirty = pd.DataFrame(dirty_records)
    df = pd.concat([df_clean, df_dirty], ignore_index=True)
    
    df.to_csv(filepath, index=False)
    print(f"✓ Synthetic unvalidated dataset created at {filepath} ({len(df)} records)")
    print("  Injected anomaly types: Future birth dates (2050), negative prices, missing customer IDs, invalid emails/phones, reversed date ranges.\n")
    return df

def run_validation_pipeline(df):
    """Execute all 5 validation tasks and generate reports."""
    print("="*70)
    print("DATA VALIDATION PIPELINE EXECUTION (5+ VALIDATION RULES)")
    print("="*70)
    df_val = df.copy()
    
    # Task 1: Range Checks
    print("\n--- TASK 1: RANGE CHECKS ---")
    df_val['valid_age'] = (df_val['age'] >= 0) & (df_val['age'] <= 150)
    df_val['valid_price'] = df_val['price'] >= 0
    
    # Parse birth_date safely for comparison
    birth_dt = pd.to_datetime(df_val['birth_date'], errors='coerce')
    df_val['valid_date'] = (birth_dt >= '1920-01-01') & (birth_dt <= pd.Timestamp.now())
    
    print(f"Invalid ages (not between 0 and 150):        {(~df_val['valid_age']).sum()}")
    print(f"Invalid prices (negative amounts):           {(~df_val['valid_price']).sum()}")
    print(f"Invalid birth dates (future or < 1920):      {(~df_val['valid_date']).sum()}")
    
    # Task 2: Null Constraints
    print("\n--- TASK 2: NULL CONSTRAINTS ---")
    df_val['valid_customer_id'] = df_val['customer_id'].notna() & (df_val['customer_id'].astype(str).str.strip() != '')
    df_val['valid_email'] = df_val['email'].notna() & (df_val['email'].astype(str).str.strip() != '')
    
    print(f"Missing customer IDs:                        {(~df_val['valid_customer_id']).sum()}")
    print(f"Missing emails:                              {(~df_val['valid_email']).sum()}")
    
    # Task 3: Format Pattern Validation
    print("\n--- TASK 3: FORMAT PATTERN VALIDATION ---")
    df_val['valid_email_format'] = df_val['email'].astype(str).str.contains('@', na=False) & df_val['email'].astype(str).str.contains('.', regex=False, na=False)
    df_val['valid_phone'] = df_val['phone'].astype(str).str.match(r'^\d{10}$', na=False)
    
    print(f"Invalid emails (malformed regex pattern):    {(~df_val['valid_email_format']).sum()}")
    print(f"Invalid phone numbers (not 10 digits):       {(~df_val['valid_phone']).sum()}")
    
    # Task 4: Business Rule Validation
    print("\n--- TASK 4: BUSINESS RULE VALIDATION ---")
    start_dt = pd.to_datetime(df_val['start_date'], errors='coerce')
    end_dt = pd.to_datetime(df_val['end_date'], errors='coerce')
    df_val['valid_date_order'] = end_dt >= start_dt
    
    print(f"Invalid date ranges (end before start):      {(~df_val['valid_date_order']).sum()}")
    
    # Task 5: Validation Report & Failure Isolation
    print("\n--- TASK 5: VALIDATION REPORT & FAILURE ISOLATION ---")
    validation_cols = [
        'valid_age', 'valid_price', 'valid_date', 
        'valid_customer_id', 'valid_email', 'valid_email_format', 
        'valid_phone', 'valid_date_order'
    ]
    
    df_val['passes_all_checks'] = df_val[validation_cols].all(axis=1)
    
    # Isolate failures
    failures = df_val[~df_val['passes_all_checks']]
    
    output_dir = 'output'
    if not os.path.exists(output_dir) and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    fail_path = os.path.join(output_dir, 'validation_failures.csv')
    failures.to_csv(fail_path, index=False)
    print(f"✓ Isolated {len(failures)} validation failure records and written to {fail_path}")
    
    # Print sample failure breakdown
    if len(failures) > 0:
        print("\nSample Isolated Failure Records & Violated Rules:")
        sample_cols = ['customer_id', 'age', 'birth_date', 'price', 'email', 'phone', 'start_date', 'end_date']
        print(failures[sample_cols].head(6).to_string(index=False))
        
    # Summary Report
    print("\n[EXECUTIVE VALIDATION SUMMARY REPORT]")
    print(f"Total Records Evaluated: {len(df_val)}")
    print(f"Passed All Checks:       {df_val['passes_all_checks'].sum()} ({df_val['passes_all_checks'].sum()/len(df_val)*100:.1f}%)")
    print(f"Failed One/More Checks:  {(~df_val['passes_all_checks']).sum()} ({(~df_val['passes_all_checks']).sum()/len(df_val)*100:.1f}%)")
    
    # Detailed rule failure breakdown
    summary_data = []
    for col in validation_cols:
        fail_cnt = int((~df_val[col]).sum())
        fail_pct = round((fail_cnt / len(df_val)) * 100, 2)
        summary_data.append({
            'validation_rule': col,
            'failed_records': fail_cnt,
            'failure_percentage': fail_pct,
            'status': 'PASSED' if fail_cnt == 0 else 'VIOLATION DETECTED'
        })
        
    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = os.path.join(output_dir, 'validation_report_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"\nRule-by-Rule Failure Breakdown (Saved to {summary_csv_path}):")
    print(summary_df.to_string(index=False))
    
    # Export clean validated data
    df_clean = df_val[df_val['passes_all_checks']]
    proc_dir = 'data/processed'
    if not os.path.exists(proc_dir) and os.path.exists('../data'):
        proc_dir = '../data/processed'
    else:
        os.makedirs(proc_dir, exist_ok=True)
        
    clean_path = os.path.join(proc_dir, 'validated_clean_data.csv')
    df_clean.to_csv(clean_path, index=False)
    print(f"\n✓ Exported {len(df_clean)} 100%-clean validated records to {clean_path}")
    
    # Generate Visual Failure Chart
    plt.figure(figsize=(12, 6))
    rule_names = [col.replace('valid_', '').replace('_', ' ').title() for col in summary_df['validation_rule']]
    bars = plt.barh(rule_names, summary_df['failed_records'], color='#d9534f', edgecolor='black')
    plt.title('Validation Rule Violations by Check Type', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Failed Records', fontsize=12)
    plt.ylabel('Validation Rule', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add value annotations on bars
    for bar in bars:
        width = bar.get_width()
        if width > 0:
            plt.text(width + 0.2, bar.get_y() + bar.get_height()/2, f"{int(width)}", 
                     va='center', ha='left', fontweight='bold', color='#a94442')
            
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'validation_failure_chart.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"✓ Visual validation failure chart saved to {chart_path}")
    print("="*70 + "\n")
    
    return df_clean, failures, summary_df

if __name__ == "__main__":
    filepath = 'data/raw/unvalidated_campaign_data.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    # Generate unvalidated dataset
    df_raw = generate_unvalidated_dataset(filepath)
    
    # Run pipeline
    df_clean, failures, summary_df = run_validation_pipeline(df_raw)
