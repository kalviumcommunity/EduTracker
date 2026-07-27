import os
import sys
import pandas as pd

# Ensure standard output can handle UTF-8 symbols like checkmarks on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def ingest_data(filepath):
    """
    Load data from a file and return a Pandas DataFrame.
    
    Input: Path string (filepath) pointing to a CSV or JSON file.
    Output: Pandas DataFrame containing the ingested raw dataset.
    Assumptions: The file exists and is formatted as valid CSV or JSON.
    """
    # Adjust path if running from within the scripts/ subdirectory
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    if filepath.endswith('.json'):
        df = pd.read_json(filepath)
    else:
        df = pd.read_csv(filepath)
    return df

def process_data(df):
    """
    Transform raw data into analysis-ready format.
    
    Input: Pandas DataFrame with raw data.
    Output: Pandas DataFrame with nulls filled and duplicates removed.
    Assumptions: DataFrame may contain duplicate rows or missing numerical values that should be imputed with the median.
    """
    # Remove exact duplicates (rows where all values are identical)
    df = df.drop_duplicates()
    
    # Fill missing values in numerical columns with median
    for col in df.select_dtypes(include=['number']).columns:
        df[col] = df[col].fillna(df[col].median())
    
    return df

def output_results(df, output_path):
    """
    Save processed data and print confirmation.
    
    Input: Processed Pandas DataFrame and target output file path string.
    Output: None (writes a CSV file to disk and prints execution statistics to standard output).
    Assumptions: Output directory exists or can be accessed.
    """
    # Adjust path if running from within the scripts/ subdirectory
    if not os.path.exists(os.path.dirname(output_path)) and os.path.exists(os.path.join("..", os.path.dirname(output_path))):
        output_path = os.path.join("..", output_path)
        
    df.to_csv(output_path, index=False)
    print(f"✓ Data successfully processed")
    print(f"✓ Rows processed: {len(df)}")
    print(f"✓ Output saved to {output_path}")

if __name__ == "__main__":
    data = ingest_data("data/raw/sample.csv")
    processed = process_data(data)
    output_results(processed, "output/processed.csv")
