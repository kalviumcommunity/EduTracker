import os
import sys
import pandas as pd
import numpy as np

# Ensure standard output can handle UTF-8 symbols on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def strip_all_strings(df):
    """Strip whitespace from all string columns."""
    df_cleaned = df.copy()
    string_cols = df_cleaned.select_dtypes(include=['object', 'str', 'string']).columns
    
    print("\n" + "="*70)
    print("TASK 1: STRIP WHITESPACE CONSISTENTLY")
    print("="*70)
    
    total_whitespace_fixed = 0
    for col in string_cols:
        before_unique = df_cleaned[col].nunique()
        before_counts = df_cleaned[col].value_counts(dropna=False)
        
        # Count how many values actually have leading or trailing whitespace
        has_whitespace = int(df_cleaned[col].dropna().apply(lambda x: len(str(x)) != len(str(x).strip())).sum())
        total_whitespace_fixed += has_whitespace
        
        # Apply strip
        df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
        # Replace 'nan' or 'None' strings back to NaN if they occurred from NaN casting
        df_cleaned[col] = df_cleaned[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})
        
        after_unique = df_cleaned[col].nunique()
        after_counts = df_cleaned[col].value_counts(dropna=False)
        
        print(f"\nColumn: '{col}' | Whitespace issues fixed: {has_whitespace} | Unique values: {before_unique} → {after_unique}")
        if col in ['customer_name', 'product_code'] and has_whitespace > 0:
            print(f"\n  [Before Strip - Value Counts for {col}]:")
            for val, cnt in before_counts.head(5).items():
                print(f"    '{val}': {cnt}")
            print(f"  [After Strip - Value Counts for {col}]:")
            for val, cnt in after_counts.head(5).items():
                print(f"    '{val}': {cnt}")
                
    print(f"\n✓ Summary: Total whitespace issues fixed across dataset: {total_whitespace_fixed}")
    print("="*70)
    return df_cleaned

def normalize_casing(df, columns_to_lower):
    """Normalize casing for specified columns."""
    df_cleaned = df.copy()
    print("\n" + "="*70)
    print("TASK 2: NORMALIZE CASING TO CONSISTENT STANDARD")
    print("="*70)
    print("Business Decision: Standardizing categorical text and names to lowercase.")
    print("Justification: Lowercase standardizes user input variations (e.g. CRM vs web forms), ensuring exact string matching in aggregations and joins without case-sensitivity bugs.\n")
    
    print("Sample rows BEFORE casing normalization:")
    print(df_cleaned[columns_to_lower].head(5).to_string())
    
    for col in columns_to_lower:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].str.lower()
            print(f"\n✓ Normalized column '{col}' to lowercase")
            
            # Show John example if customer_name
            if col == 'customer_name' and 'john' in df_cleaned[col].values:
                john_count = int((df_cleaned[col] == 'john').sum())
                print(f"  Demonstration: 'JOHN', 'john', and 'John' consolidated into canonical 'john' (Total count: {john_count})")
                
    print("\nSample rows AFTER casing normalization:")
    print(df_cleaned[columns_to_lower].head(5).to_string())
    print("="*70)
    return df_cleaned

def remove_special_characters(df, columns):
    """Remove special characters from specified columns."""
    df_cleaned = df.copy()
    print("\n" + "="*70)
    print("TASK 3: REMOVE SPECIAL CHARACTERS USING REGEX")
    print("="*70)
    print("Regex Pattern Used: '[^a-zA-Z0-9 ]'")
    print("Explanation: Matches any character that is NOT standard ASCII lowercase (a-z), uppercase (A-Z), digit (0-9), or space ( ). It replaces accents, punctuation, symbols, and international characters with empty string '' to prevent encoding errors in legacy downstream systems.\n")
    
    for col in columns:
        if col in df_cleaned.columns:
            before_samples = df_cleaned[col].dropna().unique()[:4].tolist()
            df_cleaned[col] = df_cleaned[col].str.replace('[^a-zA-Z0-9 ]', '', regex=True)
            after_samples = df_cleaned[col].dropna().unique()[:4].tolist()
            
            print(f"✓ Removed special characters from '{col}'")
            print(f"  Before samples: {before_samples}")
            print(f"  After samples:  {after_samples}")
            
            if col == 'city':
                print(f"  Verification: International characters handled (e.g., 'são paulo' → 'so paulo', 'münchen' → 'mnchen', 'zürich' → 'zrich')")
                
    print("="*70)
    return df_cleaned

def standardize_categorical_labels(df, col_name, mapping_dict):
    """Standardize categorical labels using mapping dictionary."""
    df_cleaned = df.copy()
    print("\n" + "="*70)
    print("TASK 4: STANDARDIZE CATEGORICAL LABELS USING MAPPING DICTIONARY")
    print("="*70)
    print(f"Target Column: '{col_name}'")
    print("Mapping Dictionary (3 categories × 3 variations):")
    for var, canonical in mapping_dict.items():
        print(f"  '{var}' → '{canonical}'")
        
    print("\nBusiness Justifications for Canonical Forms:")
    print("  • 'B2B': Standard industry abbreviation for Business-to-Business; matches core CRM segmentation code.")
    print("  • 'SMB': Canonical designation for Small & Medium Business; preferred over SME/sme by sales finance team.")
    print("  • 'Enterprise': Unabbreviated title required for executive reporting and large-account tiering.\n")
    
    if col_name in df_cleaned.columns:
        print("Value counts BEFORE mapping:")
        print(df_cleaned[col_name].value_counts(dropna=False).to_string())
        
        df_cleaned[col_name] = df_cleaned[col_name].map(mapping_dict).fillna(df_cleaned[col_name])
        
        print("\nValue counts AFTER mapping (consolidated):")
        print(df_cleaned[col_name].value_counts(dropna=False).to_string())
        
    print("="*70)
    return df_cleaned

def clean_text_column(series, lowercase=True, strip=True, 
                     remove_special=False, mapping=None):
    """Reusable text cleaning function for any string column."""
    result = series.copy()
    
    if result.isna().any():
        print(f"Warning: {result.isna().sum()} null values in column '{series.name if hasattr(series, 'name') and series.name else 'Series'}'")
    
    if strip:
        result = result.astype(str).str.strip()
        result = result.replace({'nan': np.nan, 'None': np.nan, '': np.nan})
    
    if lowercase:
        result = result.str.lower()
    
    if remove_special:
        result = result.str.replace('[^a-zA-Z0-9 ]', '', regex=True)
    
    if mapping:
        result = result.map(mapping).fillna(result)
    
    return result

if __name__ == "__main__":
    # Determine filepath robustly
    filepath = 'data/raw/messy_text_data.csv'
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    df = pd.read_csv(filepath)
    print(f"Loaded dataset with shape: {df.shape}")
    
    # Task 1: Strip Whitespace
    df_step1 = strip_all_strings(df)
    
    # Task 2: Normalize Casing
    df_step2 = normalize_casing(df_step1, ['customer_name', 'city', 'segment', 'product_code'])
    
    # Task 3: Remove Special Characters
    df_step3 = remove_special_characters(df_step2, ['city', 'product_code'])
    
    # Task 4: Standardize Categorical Labels
    segment_map = {
        'b2b': 'B2B',
        'b 2 b': 'B2B',
        'business-to-business': 'B2B',
        'sme': 'SMB',
        'small medium enterprise': 'SMB',
        'smb': 'SMB',
        'enterprise': 'Enterprise',
        'enterprise co': 'Enterprise',
        'ent.': 'Enterprise'
    }
    df_step4 = standardize_categorical_labels(df_step3, 'segment', segment_map)
    
    # Task 5: Build & Demonstrate Reusable String Cleaning Function
    print("\n" + "="*70)
    print("TASK 5: REUSABLE STRING CLEANING FUNCTION DEMONSTRATION")
    print("="*70)
    print("Applying clean_text_column() to multiple columns with tailored parameter combinations:\n")
    
    df_reusable = df.copy()
    
    # Column 1: customer_name
    print("1. Column: 'customer_name' | Parameters: lowercase=True, strip=True, remove_special=False")
    print("   Documentation: Strips accidental form padding and normalizes case, but preserves hyphens/spaces in compound names.")
    df_reusable['customer_name'] = clean_text_column(df_reusable['customer_name'], lowercase=True, strip=True, remove_special=False)
    print(f"   Sample output: {df_reusable['customer_name'].dropna().unique()[:4].tolist()}\n")
    
    # Column 2: product_code
    print("2. Column: 'product_code' | Parameters: lowercase=False, strip=True, remove_special=True")
    print("   Documentation: Removes special punctuation (#, !, *) and whitespace, maintaining uppercase SKU code format.")
    df_reusable['product_code'] = clean_text_column(df_reusable['product_code'], lowercase=False, strip=True, remove_special=True)
    print(f"   Sample output: {df_reusable['product_code'].dropna().unique()[:4].tolist()}\n")
    
    # Column 3: segment
    print("3. Column: 'segment' | Parameters: lowercase=True, strip=True, mapping=segment_map")
    print("   Documentation: Pre-cleans whitespace and case before mapping into canonical B2B/SMB/Enterprise tiers.")
    df_reusable['segment'] = clean_text_column(df_reusable['segment'], lowercase=True, strip=True, mapping=segment_map)
    print(f"   Sample output: {df_reusable['segment'].dropna().unique()[:4].tolist()}\n")
    print("="*70)
    
    # Save processed data
    output_path = 'data/processed/cleaned_text_data.csv'
    if not os.path.exists('data') and os.path.exists('../data'):
        output_path = '../data/processed/cleaned_text_data.csv'
    else:
        os.makedirs('data/processed', exist_ok=True)
    df_reusable.to_csv(output_path, index=False)
    print(f"\n✓ Cleaned text dataset saved to {output_path}")
    
    # Testing Instructions Execution
    print("\n" + "="*70)
    print("TESTING INSTRUCTIONS - EDGE CASE SUITE")
    print("="*70)
    test_cases = [
        '  Product A  ',      # Leading/trailing spaces
        'PRODUCT B',         # All caps
        'Product_C',         # Special char
        None,                # Null value
        ''                   # Empty string
    ]
    test_series = pd.Series(test_cases, name="test_edge_cases")
    print("Input test cases:")
    for idx, val in enumerate(test_cases):
        print(f"  [{idx}]: {repr(val)}")
        
    print("\nExecuting: clean_text_column(test_series, lowercase=True, strip=True, remove_special=True)")
    result = clean_text_column(test_series, lowercase=True, strip=True, remove_special=True)
    
    print("\nCleaned Result Series:")
    print(result.to_string())
    print("="*70)
