import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np

# Ensure standard output can handle UTF-8 symbols on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def detect_exact_duplicates(df):
    """
    Find rows where all values are identical.
    
    Returns: Tuple of (count, duplicate_rows_dataframe)
    """
    # Count exact duplicates
    exact_dups = int(df.duplicated().sum())
    
    # Get actual duplicate rows including the original
    dup_rows = df[df.duplicated(keep=False)].sort_values(by=df.columns.tolist())
    
    print("\nEXACT DUPLICATE DETECTION")
    print("="*60)
    print(f"Exact duplicates found: {exact_dups}")
    print(f"Total duplicate rows (including originals): {len(dup_rows)}")
    
    if len(dup_rows) > 0:
        print(f"\nSample duplicate rows:")
        print(dup_rows.head(10).to_string())
    
    return exact_dups, dup_rows

def detect_near_duplicates(df, key_columns):
    """
    Find rows with same key values but different other fields.
    
    Args:
        df: Input DataFrame
        key_columns: Columns defining uniqueness (e.g., ['customer_id', 'date'])
    
    Returns:
        DataFrame showing near-duplicates grouped by key
    """
    valid_keys = [col for col in key_columns if col in df.columns]
    if not valid_keys:
        print(f"Warning: None of the key columns {key_columns} found in DataFrame")
        return pd.DataFrame()
        
    # Find records with duplicate key values
    duplicate_keys = df[df.duplicated(subset=valid_keys, keep=False)]
    
    print("\nNEAR-DUPLICATE DETECTION")
    print("="*60)
    print(f"Records with duplicate keys: {len(duplicate_keys)}")
    print(f"Unique key combinations with duplicates: {len(duplicate_keys.groupby(valid_keys)) if len(duplicate_keys) > 0 else 0}")
    
    # Show sample groups
    if len(duplicate_keys) > 0:
        print(f"\nSample groups with duplicate keys:")
        for keys, group in list(duplicate_keys.groupby(valid_keys))[:3]:
            print(f"\n  Key: {keys}")
            print(f"  Records in group: {len(group)}")
            print(group.to_string())
    
    return duplicate_keys

def remove_exact_duplicates(df, keep='first'):
    """
    Remove exact duplicates, choosing which record to keep.
    
    Args:
        df: Input DataFrame
        keep: 'first' (keep oldest), 'last' (keep newest), or False (remove all)
    
    Returns:
        Deduplicated DataFrame with row counts documented
    """
    rows_before = len(df)
    
    df_dedup = df.drop_duplicates(keep=keep).copy()
    
    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = (rows_removed / rows_before) * 100 if rows_before > 0 else 0.0
    
    print("\nEXACT DUPLICATE REMOVAL")
    print("="*60)
    print(f"Keep strategy: {keep}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(f"Rows removed: {rows_removed:,} ({removal_pct:.2f}%)")
    
    return df_dedup

def remove_near_duplicates(df, key_columns, keep_strategy='most_complete'):
    """
    Remove near-duplicates by choosing best record.
    
    Args:
        df: Input DataFrame
        key_columns: Columns defining uniqueness
        keep_strategy: 'most_complete' (fewest nulls), 'first', 'last'
    
    Returns:
        Deduplicated DataFrame
    """
    valid_keys = [col for col in key_columns if col in df.columns]
    rows_before = len(df)
    
    if not valid_keys:
        print(f"Warning: Key columns {key_columns} not found")
        return df.copy()
        
    if keep_strategy == 'most_complete':
        # Keep row with fewest nulls per group, preserving original index for audit logging
        df_sorted = df.assign(null_count=df.isnull().sum(axis=1)).sort_values(by='null_count', ascending=True)
        df_dedup = df_sorted.drop_duplicates(subset=valid_keys, keep='first').drop(columns=['null_count']).sort_index()
    
    elif keep_strategy == 'last':
        # Keep most recent record (last by index)
        df_dedup = df.drop_duplicates(subset=valid_keys, keep='last').copy()
    
    else:
        # Keep first record
        df_dedup = df.drop_duplicates(subset=valid_keys, keep='first').copy()
    
    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = (rows_removed / rows_before) * 100 if rows_before > 0 else 0.0
    
    print("\nNEAR-DUPLICATE REMOVAL")
    print("="*60)
    print(f"Keep strategy: {keep_strategy}")
    print(f"Key columns: {valid_keys}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(f"Rows removed: {rows_removed:,} ({removal_pct:.2f}%)")
    
    return df_dedup

def log_removed_duplicates(df_original, df_dedup):
    """
    Save all removed duplicate rows to audit file for compliance.
    
    Returns: Audit summary
    """
    # Find rows in original but not in deduplicated
    removed_mask = ~df_original.index.isin(df_dedup.index)
    removed_records = df_original[removed_mask]
    
    print("\nAUDIT LOGGING")
    print("="*60)
    print(f"Total records removed: {len(removed_records)}")
    
    # Determine output path robustly
    output_dir = 'output'
    if not os.path.exists('output') and os.path.exists('../output'):
        output_dir = '../output'
    else:
        os.makedirs(output_dir, exist_ok=True)
        
    audit_csv_path = os.path.join(output_dir, 'removed_duplicates_audit.csv')
    audit_json_path = os.path.join(output_dir, 'dedup_audit_summary.json')
    
    # Save removed records for audit trail
    removed_records.to_csv(audit_csv_path, index=False)
    print(f"✓ Removed records saved to audit file")
    
    # Create summary
    audit_summary = {
        'removal_timestamp': datetime.now().isoformat(),
        'total_removed': int(len(removed_records)),
        'reason': 'Duplicate detection and deduplication',
        'audit_file': 'output/removed_duplicates_audit.csv',
        'audit_note': 'All removed records logged for compliance and recovery if needed'
    }
    
    with open(audit_json_path, 'w') as f:
        json.dump(audit_summary, f, indent=2, default=str)
    
    print(f"✓ Audit summary saved")
    print("="*60)
    
    return removed_records, audit_summary

def compare_before_after(df_original, df_dedup):
    """
    Log before/after metrics confirming deduplication worked.
    
    Returns: Comparison dictionary
    """
    comparison = {
        'rows_before': int(len(df_original)),
        'rows_after': int(len(df_dedup)),
        'rows_removed': int(len(df_original) - len(df_dedup)),
        'removal_percentage': round(((len(df_original) - len(df_dedup)) / len(df_original)) * 100, 2) if len(df_original) > 0 else 0.0,
        'columns': int(len(df_original.columns)),
        'nulls_before': int(df_original.isnull().sum().sum()),
        'nulls_after': int(df_dedup.isnull().sum().sum()),
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n" + "="*70)
    print("DEDUPLICATION FINAL SUMMARY")
    print("="*70)
    print(f"Rows before: {comparison['rows_before']:,}")
    print(f"Rows after:  {comparison['rows_after']:,}")
    print(f"Removed:     {comparison['rows_removed']:,} ({comparison['removal_percentage']}%)")
    print(f"\nNulls before: {comparison['nulls_before']:,}")
    print(f"Nulls after:  {comparison['nulls_after']:,}")
    print(f"Null change:  {comparison['nulls_before'] - comparison['nulls_after']:,}")
    print("="*70)
    
    output_path = 'output/dedup_summary.json'
    if not os.path.exists('output') and os.path.exists('../output'):
        output_path = '../output/dedup_summary.json'
    else:
        os.makedirs('output', exist_ok=True)
        
    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    return comparison

if __name__ == "__main__":
    # Determine filepath robustly
    filepath = 'data/raw/data_with_dupes.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    # Load data
    df = pd.read_csv(filepath)
    df_original = df.copy()
    
    print("\n" + "="*70)
    print("STARTING DEDUPLICATION WORKFLOW")
    print("="*70)
    print(f"Initial record count: {len(df):,}")
    
    # Step 1: Detect exact duplicates
    print("\n[Step 1/4] Detecting exact duplicates...")
    exact_count, exact_rows = detect_exact_duplicates(df)
    
    # Step 2: Detect near-duplicates
    print("\n[Step 2/4] Detecting near-duplicates by key...")
    near_dups = detect_near_duplicates(df, key_columns=['customer_id', 'transaction_date'])
    
    # Step 3: Remove exact duplicates
    print("\n[Step 3/4] Removing exact duplicates (keeping first)...")
    df = remove_exact_duplicates(df, keep='first')
    
    # Step 4: Remove near-duplicates
    print("\n[Step 4/4] Removing near-duplicates (keeping most complete)...")
    df = remove_near_duplicates(
        df,
        key_columns=['customer_id', 'transaction_date'],
        keep_strategy='most_complete'
    )
    
    # Log removals
    print("\n[Audit] Logging removed records for compliance...")
    log_removed_duplicates(df_original, df)
    
    # Compare metrics
    compare_before_after(df_original, df)
    
    # Determine output path robustly
    output_path = 'data/processed/deduplicated_data.csv'
    if not os.path.exists('data') and os.path.exists('../data'):
        output_path = '../data/processed/deduplicated_data.csv'
    else:
        os.makedirs('data/processed', exist_ok=True)
        
    # Save deduplicated data
    df.to_csv(output_path, index=False)
    print(f"\n✓ Deduplicated data saved to {output_path}")
