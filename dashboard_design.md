# Dashboard Design Documentation

## Information Hierarchy Applied
- Level 1 (Status): 5 KPI cards at the top provide an executive summary of revenue, customer health, average sale size, churn, and marketing effectiveness.
- Level 2 (Trends): 3 trend charts in the middle reveal momentum and changes over time for revenue, customer behavior, and campaign engagement.
- Level 3 (Segments): 2 comparison charts show revenue by customer segment and revenue by region, highlighting where growth and risk are concentrated.
- Level 4 (Detail): Drill-down filters and a detailed data table allow analysts to inspect underlying records and export selected data.

## Design Principles Applied
1. Progressive Disclosure: High-level KPIs are visible immediately, deeper insights are available through charts, and full detail is behind filters.
2. Spatial Organisation: The most important status metrics are placed at the top, with trends below, then segmentation, and finally the detailed explorer.
3. Consistent Metaphor: Blue for core business metrics, green for positive targets, orange for comparative context, red for risk or concern.
4. Context Over Numbers: Each chart contains titles, axis labels, and reference lines so viewers understand not just the value, but whether it is on track.

## Colour Palette
- Primary: #1f77b4 (blue) - main business metrics
- Secondary: #ff7f0e (orange) - comparison or secondary trend lines
- Success: #2ca02c (green) - target lines and positive outcomes
- Danger: #d62728 (red) - churn, risk, and caution signals

## Target Audience
- Primary: VP of Sales (daily user, checks KPIs and trends and wants regional/revenue breakdowns)
- Secondary: CEO (weekly glance, reads KPI row and top-line trend direction)
- Tertiary: Analysts (uses filters and exports for deeper investigation and operational follow-up)

## Data Sources
- KPI values: Computed from curated revenue and customer tables or views such as `vw_monthly_revenue` and `vw_active_customers`
- Trend data: Queried from aggregated daily/monthly revenue and customer engagement tables
- Segment data: Derived from a segment view like `vw_customer_segments` or comparable segment-level revenue tables

## KPI Selection and Business Questions
- Revenue: "Are we hitting top-line growth targets?" Critical for CEO and sales leadership.
- Active Customers: "Is customer adoption and retention improving?" Important for sales and product decisions.
- Avg Order Value: "Are we increasing value per transaction?" Measures revenue efficiency.
- Churn Rate: "Is customer attrition rising or falling?" Key for both sales and executive risk monitoring.
- Marketing ROI: "Is campaign spend translating into business outcomes?" Essential for marketing and finance alignment.

## Trend Charts and Their Insights
- Revenue Trend: Shows whether the business is maintaining or exceeding revenue targets over time.
- Customer Growth vs Churn: Reveals whether growth is driven by new customers or offset by attrition.
- Campaign Engagement: Connects marketing activity with business outcomes, showing if campaigns are gaining momentum.

## Segment Breakdown Insights
- Revenue by Customer Segment: Helps identify which customer segments are most valuable and where to focus sales efforts.
- Revenue by Region: Shows geographic performance, guiding resource allocation and regional strategy.

## Progressive Disclosure Details
- Filters let users narrow the view by segment and date range.
- The detailed table shows customer-level records, allowing analysts to verify KPI drivers and spot anomalies.
- The download option provides a direct export path for further offline analysis.
