import os
import sys
import json
import pandas as pd

# Ensure standard output can handle UTF-8 symbols like checkmarks on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def ingest_csv(filepath, delimiter=',', encoding='utf-8', dtype_dict=None):
    """
    Load CSV file with explicit parameters documented.
    
    Args:
        filepath: Path to CSV file
        delimiter: Field delimiter (comma by default, but could be semicolon or tab)
        encoding: File encoding (UTF-8 standard, but may be latin-1 or cp1252)
        dtype_dict: Dictionary mapping column names to data types
    
    Returns:
        Pandas DataFrame with shape and column names confirmed
    """
    # Adjust path if running from within the scripts/ subdirectory
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    try:
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding,
            dtype=dtype_dict
        )
        print(f"✓ CSV loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise
    except UnicodeDecodeError as e:
        print(f"Encoding error: Could not decode with {encoding}")
        print("Try: latin-1, iso-8859-1, or cp1252")
        raise

def ingest_json(filepath, is_nested=False):
    """
    Load JSON file, handling nested structures by flattening them.
    
    Args:
        filepath: Path to JSON file
        is_nested: If True, flatten nested JSON structures into columns
    
    Returns:
        Pandas DataFrame with nested structures expanded
    """
    # Adjust path if running from within the scripts/ subdirectory
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    try:
        if is_nested:
            # Flatten nested JSON: {'customer': {'name': 'Alice'}} → 'customer.name': 'Alice'
            with open(filepath, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
            df = pd.json_normalize(data_json)
            print("✓ Nested JSON flattened to tabular format")
        else:
            df = pd.read_json(filepath)
            
        print(f"✓ JSON loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise

def ingest_csv_with_fallback(filepath, delimiters=[','], fallback_encodings=None):
    """
    Load CSV with fallback encodings if initial attempt fails.
    
    Tries multiple encodings and delimiters in sequence.
    """
    # Adjust path if running from within the scripts/ subdirectory
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for delimiter in delimiters:
        for encoding in fallback_encodings:
            try:
                df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
                print(f"✓ Successfully loaded with delimiter='{delimiter}', encoding='{encoding}'")
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    
    raise ValueError(f"Could not load {filepath} with any encoding/delimiter combination")

def document_ingestion(df, source_file):
    """
    Print detailed ingestion report for audit trail.
    """
    print(f"\n{'='*60}")
    print(f"INGESTION REPORT: {source_file}")
    print(f"{'='*60}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"\nColumn Names & Data Types:")
    print(df.dtypes)
    print(f"\nNull Values Per Column:")
    print(df.isnull().sum())
    print(f"\nFirst 3 Rows:")
    print(df.head(3).to_string())
    print(f"{'='*60}\n")
    return df

if __name__ == "__main__":
    print("Starting multi-format ingestion...\n")
    
    # Load CSV with explicit parameters
    csv_df = ingest_csv(
        "data/raw/customers.csv",
        delimiter=',',
        encoding='utf-8'
    )
    document_ingestion(csv_df, "customers.csv")
    
    # Load JSON with flattening
    json_df = ingest_json(
        "data/raw/transactions.json",
        is_nested=True
    )
    document_ingestion(json_df, "transactions.json")
    
    # Ensure processed directory exists
    processed_dir = "data/processed"
    if not os.path.exists("data") and os.path.exists("../data"):
        processed_dir = "../data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    # Save ingested data
    csv_out = os.path.join(processed_dir, "customers_ingested.csv")
    json_out = os.path.join(processed_dir, "transactions_ingested.csv")
    csv_df.to_csv(csv_out, index=False)
    json_df.to_csv(json_out, index=False)
    
    print("\n✓ All data ingested and saved to processed/")
