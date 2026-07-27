# Team Workflow Documentation

## Branching Strategy
- **Main branch**: Holds releasable code only.
- **Feature branches**: Follow the `feature/[description]` naming pattern (e.g., `feature/data-ingestion`).
- **Deletion**: Branches are deleted after merge.

## Commit Message Convention
- **Types used**: `feat`, `fix`, `docs`, `refactor`, `chore`.
- **Format**: `[type]: [description]`
- **Why**: Enables automated changelog generation and clear history.

## PR Review Process
- PRs require at least one approval before merge.
- Code review focuses on: correctness, clarity, data integrity, and test coverage.
- Commit messages are reviewed as part of code review.

## GitHub Issue Tracking
- Every feature or fix starts with an issue.
- Issues have labels, assignees, and descriptions.
- Issues are closed when the corresponding PR is merged.

## Data Workflow Script
The modular data processing pipeline is implemented in `scripts/data_workflow.py`.

### Execution
Run the workflow from the repository root directory:
```bash
python scripts/data_workflow.py
```
Or from within the `scripts/` directory:
```bash
cd scripts
python data_workflow.py
```

### Modular Functions
The script is architected around three separated concerns:
1. `ingest_data(filepath)`: Reads raw data from CSV or JSON files into a Pandas DataFrame. Handled seamlessly with path resolution whether executed from project root or scripts directory.
2. `process_data(df)`: Transforms the dataset by removing exact duplicate rows and imputing missing numerical values using column medians.
3. `output_results(df, output_path)`: Saves the cleaned, analysis-ready DataFrame to CSV and prints execution confirmation statistics (`✓ Rows processed: ...`).

### Modifying for New Datasets
To adapt the workflow for new datasets:
1. **New Ingestion Sources**: In `ingest_data()`, add support for additional file extensions (e.g., `.xlsx`, `.parquet`) by calling the appropriate Pandas reader (`pd.read_excel`, `pd.read_parquet`).
2. **Custom Transformations**: Extend `process_data()` to add domain-specific cleaning rules, such as categorical encoding, date parsing, or outlier filtering.
3. **Alternative Output Formats**: Update `output_results()` to export to databases (via SQLAlchemy) or specialized serialization formats.