import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

CHART_COLORS = [
    PALETTE['primary'],
    PALETTE['secondary'],
    PALETTE['success'],
    PALETTE['warning'],
    '#9467bd',
]


def chart1_revenue_by_product():
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    revenue = [4.5e6, 3.2e6, 2.1e6, 1.4e6, 0.9e6]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(products, revenue, color=PALETTE['primary'])
    ax.set_xlabel('Revenue ($)', fontsize=12)
    ax.set_ylabel('Product Line', fontsize=12)
    ax.set_title('Last Quarter Revenue by Product Line', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    for bar, value in zip(bars, revenue):
        ax.text(value + 50000, bar.get_y() + bar.get_height() / 2, f'${value/1e6:.1f}M', va='center', fontsize=10)
    ax.annotate(
        'Top performer',
        xy=(revenue[0], 0),
        xytext=(revenue[0] + 200000, -0.2),
        arrowprops=dict(arrowstyle='->', color=PALETTE['warning'], lw=2),
        fontsize=11,
        color=PALETTE['warning'],
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'chart1_revenue_by_product.png', dpi=300, bbox_inches='tight')
    plt.close(fig)


def chart2_revenue_trend():
    months = pd.date_range(start='2024-01-01', periods=12, freq='ME')
    data = {
        'Month': months,
        'Product A': [420000, 440000, 460000, 450000, 470000, 490000, 510000, 530000, 550000, 570000, 590000, 610000],
        'Product B': [310000, 320000, 330000, 340000, 345000, 360000, 370000, 380000, 390000, 405000, 420000, 435000],
        'Product C': [210000, 205000, 215000, 220000, 225000, 230000, 235000, 240000, 245000, 250000, 255000, 260000],
    }
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Month'], df['Product A'], marker='o', linewidth=2, color=PALETTE['primary'], label='Product A')
    ax.plot(df['Month'], df['Product B'], marker='s', linewidth=2, color=PALETTE['secondary'], label='Product B')
    ax.plot(df['Month'], df['Product C'], marker='^', linewidth=2, color=PALETTE['success'], label='Product C')
    ax.set_title('Revenue Trend by Top 3 Products (Last 12 Months)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)
    peak_date = df.loc[df['Product A'].idxmax(), 'Month']
    peak_value = df['Product A'].max()
    ax.annotate(
        'Product A peak',
        xy=(peak_date, peak_value),
        xytext=(peak_date, peak_value + 25000),
        arrowprops=dict(arrowstyle='->', color=PALETTE['warning'], lw=2),
        fontsize=11,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7),
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'chart2_revenue_trend.png', dpi=300, bbox_inches='tight')
    plt.close(fig)


def chart3_order_value_distribution():
    np.random.seed(0)
    order_values = np.concatenate([
        np.random.normal(80, 30, 1200),
        np.random.normal(300, 80, 600),
        np.random.normal(550, 100, 200),
    ])
    order_values = np.clip(order_values, 5, None)
    fig, ax = plt.subplots(figsize=(10, 6))
    bins = [0, 100, 200, 300, 400, 500, 600, 800]
    counts, _, patches = ax.hist(order_values, bins=bins, color=PALETTE['primary'], edgecolor='white')
    ax.set_title('Distribution of Order Values', fontsize=14, fontweight='bold')
    ax.set_xlabel('Order Value ($)', fontsize=12)
    ax.set_ylabel('Number of Orders', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    for patch, count in zip(patches, counts):
        ax.text(patch.get_x() + patch.get_width() / 2, count + 5, int(count), ha='center', va='bottom', fontsize=9)
    ax.annotate(
        'Most orders below $100',
        xy=(80, counts[0]),
        xytext=(180, counts[0] + 50),
        arrowprops=dict(arrowstyle='->', color=PALETTE['warning'], lw=2),
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'chart3_order_value_distribution.png', dpi=300, bbox_inches='tight')
    plt.close(fig)


def chart4_revenue_composition():
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    product_lines = ['Product A', 'Product B', 'Product C']
    revenue = {
        'Product A': [1200000, 1300000, 1400000, 1500000],
        'Product B': [900000, 950000, 980000, 1020000],
        'Product C': [600000, 620000, 610000, 630000],
    }
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(quarters))
    for idx, product in enumerate(product_lines):
        values = revenue[product]
        ax.bar(quarters, values, bottom=bottom, color=CHART_COLORS[idx], label=product)
        bottom += np.array(values)
    ax.set_title('Quarterly Revenue Composition by Product Line', fontsize=14, fontweight='bold')
    ax.set_xlabel('Quarter', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.legend(title='Product Line', fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
    ax.annotate(
        'Product A share expanding',
        xy=('Q4', revenue['Product A'][-1] + revenue['Product B'][-1] / 2),
        xytext=(2.5, 2.8e6),
        arrowprops=dict(arrowstyle='->', color=PALETTE['warning'], lw=2),
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'chart4_revenue_composition.png', dpi=300, bbox_inches='tight')
    plt.close(fig)


def chart5_marketing_vs_revenue():
    marketing_spend = np.array([50, 70, 80, 60, 90, 110, 120, 105, 130, 145, 160, 175]) * 1000
    revenue = np.array([400000, 520000, 560000, 500000, 610000, 720000, 760000, 700000, 820000, 880000, 910000, 980000])
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(marketing_spend, revenue, color=PALETTE['secondary'], s=80, alpha=0.8, label='Monthly spend')
    coeffs = np.polyfit(marketing_spend, revenue, 1)
    trend = np.poly1d(coeffs)
    x_line = np.linspace(marketing_spend.min(), marketing_spend.max(), 100)
    ax.plot(x_line, trend(x_line), color=PALETTE['primary'], linewidth=2, label='Trend line')
    ax.set_title('Marketing Spend vs Revenue', fontsize=14, fontweight='bold')
    ax.set_xlabel('Marketing Spend ($)', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=11)
    outlier_x = marketing_spend[3]
    outlier_y = revenue[3]
    ax.annotate(
        'Lower revenue month',
        xy=(outlier_x, outlier_y),
        xytext=(outlier_x + 15000, outlier_y - 80000),
        arrowprops=dict(arrowstyle='->', color=PALETTE['warning'], lw=2),
        fontsize=11,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8),
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'chart5_marketing_vs_revenue.png', dpi=300, bbox_inches='tight')
    plt.close(fig)


def main():
    chart1_revenue_by_product()
    chart2_revenue_trend()
    chart3_order_value_distribution()
    chart4_revenue_composition()
    chart5_marketing_vs_revenue()
    print('Saved 5 charts to', OUTPUT_DIR)

if __name__ == '__main__':
    main()
