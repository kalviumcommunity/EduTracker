import os
import json
import chardet
import pandas as pd
from datetime import datetime

def validate_file_exists(filepath):
    """Check if file exists and is non-empty."""
    if not os.path.exists(filepath):
        return False, f"File does not exist: {filepath}"
    
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"
    
    return True, "File exists and has content"

def validate_file_format(filepath, allowed_formats=['csv', 'json', 'xlsx']):
    """Check if file extension is supported."""
    extension = filepath.split('.')[-1].lower()
    
    if extension not in allowed_formats:
        return False, f"Unsupported format: {extension}. Allowed: {allowed_formats}"
    
    return True, f"Format valid: {extension}"

def validate_schema(df, expected_columns):
    """Validate that DataFrame has all expected columns."""
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)
    
    issues = []
    if missing:
        issues.append(f"Missing columns: {missing}")
    if extra:
        issues.append(f"Unexpected columns: {extra}")
    
    if not issues:
        return True, f"Schema valid: {len(df.columns)} columns present"
    return False, " | ".join(issues)

def detect_encoding(filepath):
    """Detect file encoding with confidence."""
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read(10000))
    
    encoding = result.get('encoding', 'utf-8') if result.get('encoding') else 'utf-8'
    if encoding and encoding.lower() == 'ascii':
        encoding = 'utf-8'
    confidence = result.get('confidence', 0) if result.get('confidence') is not None else 0
    
    return encoding.lower(), f"Detected: {encoding.lower()} (confidence: {confidence:.1%})"

def capture_dataset_stats(filepath, df):
    """Log row count and file size."""
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    row_count = len(df)
    col_count = len(df.columns)
    
    return {
        'rows': row_count,
        'columns': col_count,
        'file_size_mb': round(file_size_mb, 5),
        'bytes': os.path.getsize(filepath)
    }

def generate_intake_report(filepath, expected_columns):
    """Generate complete intake validation report."""
    report = {
        'timestamp': datetime.now().isoformat()[:19],
        'filepath': filepath,
        'validations': {}
    }
    
    # Check existence
    file_exists, msg = validate_file_exists(filepath)
    report['validations']['file_exists'] = msg
    if not file_exists:
        return report
    
    # Check format
    format_valid, msg = validate_file_format(filepath)
    report['validations']['format'] = msg
    
    # Load data for remaining checks
    df = pd.read_csv(filepath)
    
    # Check schema
    schema_valid, msg = validate_schema(df, expected_columns)
    report['validations']['schema'] = msg
    
    # Check encoding
    encoding, msg = detect_encoding(filepath)
    report['validations']['encoding'] = msg
    
    # Capture statistics
    stats = capture_dataset_stats(filepath, df)
    report['statistics'] = stats
    
    # Determine output path robustly
    output_path = 'output/intake_report.json'
    if not os.path.exists('output') and os.path.exists('../output'):
        output_path = '../output/intake_report.json'
    else:
        os.makedirs('output', exist_ok=True)
        
    # Save report to file
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    return report

if __name__ == "__main__":
    filepath = "data/raw/sample.csv"
    if not os.path.exists(filepath) and os.path.exists(os.path.join("..", filepath)):
        filepath = os.path.join("..", filepath)
        
    expected_columns = ['customer_id', 'customer_name', 'transaction_amount', 'transaction_date']
    report = generate_intake_report(filepath, expected_columns)
    print("Validation report generated:")
    print(json.dumps(report, indent=2))
