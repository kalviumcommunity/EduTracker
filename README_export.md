# Export Process Guide

## What is exported
- `cleaned_data.csv`: Cleaned analysis dataset for stakeholder review.
- `summary_report.pdf`: Executive-friendly summary report.
- `interactive_report.html`: Browser-based report with embedded charts.
- `README.md`: Metadata file describing the export.

## Where exports are saved
Exports go to `output/{timestamp}_analysis`, where `timestamp` is the export run time.

## How to run on demand
From the repository root:

```bash
python scripts/export_analysis.py
```

## Streamlit one-click export
Open `dashboard/app.py` and click the `Export Full Analysis` button in the sidebar.

## Scheduled export options
### Python schedule
Use `schedule` in a small script to run daily:

```python
import schedule
import time
from scripts.export_analysis import export_analysis, verify_exports

schedule.every().day.at('17:00').do(lambda: export_analysis(...))

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Windows Task Scheduler
- Create a task to run `python scripts/export_analysis.py`
- Trigger: daily at 5:00 PM
- Start in: `C:\Users\k.vijay simha reddy\OneDrive\Desktop\Edutracker\EduTracker`

### Cron (Linux/Mac)
Use a cron entry:

```cron
0 17 * * * /usr/bin/python3 /path/to/EduTracker/scripts/export_analysis.py
```

## Validation
After export, verify files exist and are readable in the generated report folder.
