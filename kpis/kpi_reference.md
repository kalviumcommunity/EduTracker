# 📖 Formal KPI Reference Document

This document establishes canonical, company-wide KPI definitions, mathematical formulas, data sources, target ranges, ownership, and update frequencies to eliminate discrepancies across Finance, Sales, and Product teams.

---

## 1. Monthly Active Users (MAU)
* **Definition**: Distinct, unique customer accounts that have completed at least one transaction in the last 30 rolling calendar days.
* **Formula**: `COUNT(DISTINCT customer_id) WHERE transaction_date >= TODAY() - 30 days`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: 5,000 - 6,000 active users
* **Owner**: Head of Product
* **Update Frequency**: Daily
* **Notes**: Core indicator of product engagement and monthly retention. Excludes unverified account creations and cancelled signups.

---

## 2. Average Revenue Per Customer (RPC / ARPU)
* **Definition**: Total monetary revenue generated across all completed transactions divided by the total count of unique active customers in the same timeframe.
* **Formula**: `SUM(amount) / COUNT(DISTINCT customer_id) WHERE payment_status = 'COMPLETED'`
* **Data Source**: `transactions` table (columns: `amount`, `customer_id`, `payment_status`)
* **Target Range**: $90.00 - $110.00
* **Owner**: Finance & Revenue Operations Lead
* **Update Frequency**: Daily / Monthly Close
* **Notes**: Measures unit economic value per active customer account. High-value Enterprise accounts heavily elevate this metric.

---

## 3. Monthly Churn Rate
* **Definition**: The percentage of active customers from the prior 30-day period who executed zero transactions in the subsequent 30-day period.
* **Formula**: `(Active_Users_Period_1 - Retained_Users_Period_2) / Active_Users_Period_1`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: 0.0% - 5.0% (0.00 - 0.05)
* **Owner**: Customer Success Director
* **Update Frequency**: Weekly / Monthly
* **Notes**: Key metric for revenue retention. Early indicators of churn trigger automated customer success interventions.

---

## 4. Payment Success Rate
* **Definition**: The proportion of payment transaction attempts that successfully process without gateway declines, authorization failures, or user cancellations.
* **Formula**: `COUNT(transactions WHERE payment_status = 'SUCCESS') / COUNT(total_payment_attempts)`
* **Data Source**: `payment_gateway_logs` table (columns: `transaction_id`, `payment_status`)
* **Target Range**: 95.0% - 100.0% (0.95 - 1.00)
* **Owner**: Engineering / Infrastructure Team
* **Update Frequency**: Real-time / Hourly
* **Notes**: Indicates checkout health and gateway reliability. Drop below 95% triggers immediate engineering PagerDuty alert.

---

## 5. Customer Acquisition Cost (CAC)
* **Definition**: Total marketing, advertising, and sales campaign expenditures incurred divided by the total number of new paying customers acquired within the same period.
* **Formula**: `Total_Sales_and_Marketing_Expenses / New_Paying_Customers_Acquired`
* **Data Source**: `financial_ledger` table & `transactions` table
* **Target Range**: $0.00 - $50.00
* **Owner**: VP of Marketing
* **Update Frequency**: Monthly
* **Notes**: Must be evaluated in conjunction with LTV (LTV:CAC ratio target > 3.0).

---

## 6. Total Monthly Revenue
* **Definition**: Aggregate dollar value of all successfully completed customer transactions within the current billing month.
* **Formula**: `SUM(amount) WHERE payment_status = 'SUCCESS' AND transaction_date WITHIN CURRENT_MONTH`
* **Data Source**: `transactions` table (columns: `amount`, `payment_status`, `transaction_date`)
* **Target Range**: $500,000.00 - $750,000.00
* **Owner**: Chief Financial Officer (CFO)
* **Update Frequency**: Daily
* **Notes**: Decomposes hierarchically by Customer Segment (Enterprise, SMB, Startup) and Product Tier (Basic, Pro, Enterprise Plan).
