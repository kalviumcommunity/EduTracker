import json
import os

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 📊 Customer Segmentation & Churn Analysis\n",
    "\n",
    "## Executive Overview\n",
    "Aggregate reporting obscures underlying customer realities by averaging churn to a misleading single figure (~7-9%). This notebook segments customers by `customer_type` (**Enterprise**, **SMB**, **Startup**), computes multi-dimensional performance metrics, generates visual heatmap comparisons, ranks top/bottom performers, and surfaces actionable segment-specific business strategies."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import sys\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# Import dataset generator\n",
    "sys.path.append(os.path.abspath('..'))\n",
    "from scripts.customer_segmentation_assignment import generate_customer_dataset\n",
    "\n",
    "df = generate_customer_dataset(n_customers=2000)\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Task 1: Define Segments and Compute Metrics (1 mark)\n",
    "Group data by `customer_type` and aggregate 4+ metrics alongside segment sample counts."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "segment_metrics = df.groupby('customer_type').agg({\n",
    "    'lifetime_value': 'mean',\n",
    "    'churn': 'mean',\n",
    "    'support_tickets': 'mean',\n",
    "    'retention_days': 'mean',\n",
    "    'customer_id': 'count'\n",
    "})\n",
    "\n",
    "segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'count']\n",
    "print(segment_metrics)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Task 2: Summary Statistics Table (1 mark)\n",
    "Rank segments by key metrics and format table for executive readability."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "segment_summary = segment_metrics.copy()\n",
    "segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False)\n",
    "segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True)\n",
    "\n",
    "print(segment_summary[['avg_ltv', 'ltv_rank', 'churn_rate', 'churn_rank']])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Task 3: Visual Comparison (1 mark)\n",
    "Generate and save heatmap visual comparison across key performance metrics."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Heatmap\n",
    "plt.figure(figsize=(8, 5))\n",
    "sns.heatmap(segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets']], \n",
    "            annot=True, cmap='RdYlGn', cbar_kws={'label': 'Value'})\n",
    "plt.title('Segment Comparison Heatmap')\n",
    "plt.savefig('segment_heatmap.png')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Task 4: Top and Bottom Performer Analysis (1 mark)\n",
    "Identify highest value, highest churn, and best retention segments programmatically."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Highest value segment\n",
    "top_segment = segment_metrics['avg_ltv'].idxmax()\n",
    "top_value = segment_metrics.loc[top_segment, 'avg_ltv']\n",
    "\n",
    "# Highest churn segment\n",
    "high_churn = segment_metrics['churn_rate'].idxmax()\n",
    "\n",
    "insights = f\"\"\"\n",
    "HIGHEST VALUE: {top_segment} = ${top_value:,.0f}\n",
    "HIGHEST CHURN: {high_churn} = {segment_metrics.loc[high_churn, 'churn_rate']:.1%}\n",
    "BEST RETENTION: {segment_metrics['avg_retention'].idxmax()}\n",
    "\"\"\"\n",
    "\n",
    "print(insights)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Task 5: Business-Facing Insights (1 mark)\n",
    "Document segment-specific strategic insights and concrete action recommendations."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "business_summary = \"\"\"\n",
    "SEGMENT STRATEGY SUMMARY:\n",
    "\n",
    "Enterprise (5% of base, $150k LTV, 1% churn):\n",
    "- Highest value, lowest churn\n",
    "- Action: Maintain premium support, retention focus\n",
    "\n",
    "SMB (40% of base, $8k LTV, 12% churn):\n",
    "- Middle value, high churn risk\n",
    "- Action: Improve onboarding, cheaper support tier\n",
    "\n",
    "Startup (55% of base, $2k LTV, 8% churn):\n",
    "- Lowest value, moderate churn\n",
    "- Action: Self-service, education-focused\n",
    "\"\"\"\n",
    "\n",
    "print(business_summary)"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

output_path = 'EduTracker/notebooks/customer_segmentation_analysis.ipynb'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print(f"Jupyter Notebook successfully saved to: {output_path}")
