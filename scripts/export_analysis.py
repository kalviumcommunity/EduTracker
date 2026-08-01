import html
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

try:
    from plotly.graph_objs import Figure
except ImportError:  # pragma: no cover
    Figure = object  # type: ignore


def markdown_to_html(markdown_text: str) -> str:
    lines = []
    list_open = False
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            if list_open:
                lines.append('</ul>')
                list_open = False
            lines.append('<p></p>')
            continue

        if line.startswith('# '):
            if list_open:
                lines.append('</ul>')
                list_open = False
            lines.append(f'<h1>{html.escape(line[2:])}</h1>')
        elif line.startswith('## '):
            if list_open:
                lines.append('</ul>')
                list_open = False
            lines.append(f'<h2>{html.escape(line[3:])}</h2>')
        elif line.startswith('### '):
            if list_open:
                lines.append('</ul>')
                list_open = False
            lines.append(f'<h3>{html.escape(line[4:])}</h3>')
        elif line.startswith('- '):
            if not list_open:
                lines.append('<ul>')
                list_open = True
            lines.append(f'<li>{html.escape(line[2:])}</li>')
        else:
            text = html.escape(line)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            lines.append(f'<p>{text}</p>')

    if list_open:
        lines.append('</ul>')

    return '\n'.join(lines)


def render_pdf_summary(markdown_text: str, pdf_path: Path) -> None:
    safe_text = markdown_text.replace('#', '').strip()
    safe_text = re.sub(r'\*\*(.*?)\*\*', r'\1', safe_text)
    paragraph_text = '\n\n'.join(
        ' '.join(textwrap.wrap(line, width=90))
        for line in safe_text.splitlines()
        if line.strip()
    )

    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        plt.axis('off')
        fig.text(0.05, 0.95, paragraph_text, va='top', ha='left', fontsize=10, family='sans-serif')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)


def safe_div_id(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)


def export_analysis(
    df: pd.DataFrame,
    summary_text: str,
    charts_dict: Dict[str, Figure],
    output_dir: str,
    metadata_filename: str = 'README.md',
) -> str:
    output_path = Path(output_dir)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    report_dir = output_path / f'{timestamp}_analysis'
    report_dir.mkdir(parents=True, exist_ok=True)

    csv_path = report_dir / 'cleaned_data.csv'
    df.to_csv(csv_path, index=False)
    print(f'✓ CSV exported: {csv_path}')

    pdf_path = report_dir / 'summary_report.pdf'
    try:
        render_pdf_summary(summary_text, pdf_path)
        print(f'✓ PDF exported: {pdf_path}')
    except Exception as exc:  # pragma: no cover
        print(f'✗ PDF export failed: {exc}')

    html_path = report_dir / 'interactive_report.html'
    summary_html = markdown_to_html(summary_text)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Analysis Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }}
            h1, h2, h3 {{ color: #333; }}
            .chart-container {{ margin: 24px 0; }}
            .summary p {{ max-width: 900px; }}
        </style>
    </head>
    <body>
        <h1>Analysis Report</h1>
        <div class="summary">{summary_html}</div>
    """

    for chart_name, fig in charts_dict.items():
        div_id = safe_div_id(chart_name)
        if hasattr(fig, 'to_html'):
            fig_html = fig.to_html(include_plotlyjs=False, full_html=False, div_id=div_id)
        else:
            fig_html = f'<p>Chart {html.escape(chart_name)} is unavailable.</p>'
        html_content += f"""
        <div class="chart-container">
            <h2>{html.escape(chart_name)}</h2>
            {fig_html}
        </div>
        """

    html_content += "</body>\n</html>"

    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f'✓ HTML exported: {html_path}')

    metadata = {
        'Generated': datetime.now().isoformat(),
        'Records': len(df),
        'Columns': list(df.columns),
        'Data Range': str(df['date'].min()) + ' to ' + str(df['date'].max()) if 'date' in df.columns else 'N/A',
    }

    metadata_path = report_dir / metadata_filename
    with open(metadata_path, 'w', encoding='utf-8') as file:
        file.write('# Analysis Report\n\n')
        for key, value in metadata.items():
            file.write(f'- **{key}:** {value}\n')
    print(f'✓ Metadata created: {metadata_path}')

    return str(report_dir)


def verify_exports(report_dir: str) -> None:
    report_path = Path(report_dir)
    required_files = ['cleaned_data.csv', 'summary_report.pdf', 'interactive_report.html', 'README.md']

    for filename in required_files:
        filepath = report_path / filename
        if filepath.exists():
            print(f'✓ {filename}: {filepath.stat().st_size} bytes')
        else:
            print(f'✗ {filename}: MISSING')

    csv_path = report_path / 'cleaned_data.csv'
    try:
        df_test = pd.read_csv(csv_path)
        print(f'✓ CSV readable: {len(df_test)} rows, {len(df_test.columns)} columns')
    except Exception as exc:
        print(f'✗ CSV read failed: {exc}')

    html_path = report_path / 'interactive_report.html'
    print(f'\nOpen in browser: file://{html_path.resolve()}')


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / 'data' / 'processed'
    orders_path = data_dir / 'merged_customer_orders.csv'
    revenue_path = data_dir / 'processed_time_series_revenue.csv'

    orders_df = pd.read_csv(orders_path, parse_dates=['order_date'])
    revenue_df = pd.read_csv(revenue_path, parse_dates=['date'])

    summary = (
        '## Churn Analysis\n'
        'Support speed is strongly linked to customer retention. Fast response times keep customers, while delays increase churn. '
        'This export includes cleaned order data, an executive summary, and interactive charts for stakeholder review.'
    )

    try:
        import plotly.graph_objs as go

        fig_revenue = go.Figure(
            go.Scatter(x=revenue_df['date'], y=revenue_df['revenue'], mode='lines+markers', name='Revenue')
        )
        fig_churn = go.Figure(
            go.Bar(x=orders_df['payment_status'].value_counts().index.astype(str), y=orders_df['payment_status'].value_counts().values, name='Payment Status')
        )
        charts = {'Revenue Trend': fig_revenue, 'Payment Status Distribution': fig_churn}
    except ImportError:
        charts = {}

    output_folder = export_analysis(orders_df, summary, charts, str(base_dir / 'output'))
    verify_exports(output_folder)
