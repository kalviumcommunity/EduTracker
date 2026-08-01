import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
    'neutral': '#7f7f7f',
}


def chart1_revenue_trend():
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    revenue = np.linspace(400000, 560000, len(dates)) + np.random.normal(0, 15000, len(dates))
    order_count = np.random.poisson(120, len(dates))
    fig = go.Figure(data=go.Scatter(
        x=dates,
        y=revenue,
        mode='lines+markers',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.0f}<br>Orders: %{customdata}<extra></extra>',
        line=dict(color=PALETTE['primary'], width=2),
        marker=dict(size=6),
        customdata=order_count,
    ))
    fig.update_layout(
        title='Daily Revenue Trend',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        height=550,
        template='plotly_white'
    )
    fig.write_html(OUTPUT_DIR / 'plotly_chart1_revenue_trend.html')


def chart2_product_performance():
    products = ['Product A', 'Product B', 'Product C', 'Product D']
    revenue = [520000, 430000, 380000, 210000]
    order_count = [1400, 1200, 900, 500]
    avg_order_value = [371, 358, 422, 420]
    fig = go.Figure(data=go.Bar(
        x=products,
        y=revenue,
        marker=dict(color=PALETTE['secondary']),
        hovertemplate='<b>%{x}</b><br>'
                      'Revenue: $%{y:,.0f}<br>'
                      'Order count: %{customdata[0]:,}<br>'
                      'Avg order: $%{customdata[1]:.0f}<extra></extra>',
        customdata=np.stack([order_count, avg_order_value], axis=-1),
    ))
    fig.update_layout(
        title='Revenue by Product with Order Metrics',
        xaxis_title='Product',
        yaxis_title='Revenue ($)',
        height=550,
        template='plotly_white'
    )
    fig.write_html(OUTPUT_DIR / 'plotly_chart2_product_performance.html')


def chart3_metric_selector():
    products = ['Product A', 'Product B', 'Product C', 'Product D']
    revenue_data = [50000, 75000, 120000, 45000]
    profit_data = [15000, 22000, 35000, 10000]
    order_count = [1000, 1500, 2500, 800]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=products,
        y=revenue_data,
        name='Revenue',
        marker=dict(color=PALETTE['primary']),
        visible=True
    ))
    fig.add_trace(go.Bar(
        x=products,
        y=profit_data,
        name='Profit',
        marker=dict(color=PALETTE['secondary']),
        visible=False
    ))
    fig.add_trace(go.Bar(
        x=products,
        y=order_count,
        name='Order Count',
        marker=dict(color=PALETTE['success']),
        visible=False
    ))
    fig.update_layout(
        updatemenus=[dict(
            active=0,
            x=0.0,
            xanchor='left',
            y=1.15,
            yanchor='top',
            buttons=[
                dict(label='Revenue', method='update',
                     args=[{'visible': [True, False, False]},
                           {'title': 'Revenue by Product'}]),
                dict(label='Profit', method='update',
                     args=[{'visible': [False, True, False]},
                           {'title': 'Profit by Product'}]),
                dict(label='Order Count', method='update',
                     args=[{'visible': [False, False, True]},
                           {'title': 'Order Count by Product'}])
            ]
        )],
        title='Product Performance',
        height=550,
        template='plotly_white'
    )
    fig.write_html(OUTPUT_DIR / 'plotly_chart3_metric_selector.html')


def chart4_interactive_scatter():
    x = np.linspace(1, 100, 100)
    y = 50000 + 8000 * np.sin(x / 10) + np.random.normal(0, 5000, len(x))
    fig = go.Figure(data=go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(color=PALETTE['warning'], size=10),
        hovertemplate='Week %{x:.0f}<br>Revenue: $%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Interactive Revenue Scatter',
        xaxis_title='Week Number',
        yaxis_title='Revenue ($)',
        dragmode='zoom',
        hovermode='closest',
        height=550,
        template='plotly_white'
    )
    fig.write_html(OUTPUT_DIR / 'plotly_chart4_interactive.html')


def chart5_streamlit_example():
    products = ['Product A', 'Product B', 'Product C']
    spend = [20000, 30000, 25000]
    revenue = [180000, 260000, 230000]
    fig = go.Figure(data=go.Scatter(
        x=spend,
        y=revenue,
        mode='markers+text',
        text=products,
        textposition='top center',
        marker=dict(color=PALETTE['primary'], size=12),
        hovertemplate='<b>%{text}</b><br>Marketing spend: $%{x:,.0f}<br>Revenue: $%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Marketing Spend vs Revenue',
        xaxis_title='Marketing Spend ($)',
        yaxis_title='Revenue ($)',
        height=550,
        template='plotly_white'
    )
    fig.write_html(OUTPUT_DIR / 'plotly_chart5_marketing_vs_revenue.html')


def main():
    chart1_revenue_trend()
    chart2_product_performance()
    chart3_metric_selector()
    chart4_interactive_scatter()
    chart5_streamlit_example()
    print('Generated Plotly charts in', OUTPUT_DIR)

if __name__ == '__main__':
    main()
