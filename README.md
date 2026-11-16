# E-Commerce Sales Trend & Customer Analysis

**Project 03 — Customer Churn / Sales Trend Analysis**  
**Track:** Data Science & AI  

---

## Project Overview

This project is an end-to-end sales and customer analysis of an online retail business. Using real transaction data from the **Online Retail II** dataset (spanning December 2010 to December 2011), the goal is to help store managers answer practical business questions:

1. **When does the business make the most money?** (Monthly trends and seasonality)
2. **Which product categories sell best?** (Category revenue, order counts, and item prices)
3. **Who are our most valuable customers?** (Testing the Pareto 80/20 rule)
4. **What practical actions should management take next?** (Specific, numbers-backed recommendations)

The analysis is presented in a single, well-documented Jupyter notebook and summarized in a clean, one-page business brief PDF.

---

## Key Findings

- **Total Sales:** £10.67 million across 19,960 orders, with an average order value of £534.40.
- **Strong Holiday Peak:** Sales rise steadily through autumn and reach their peak in **November 2011 at £1.51M** (+30.7% growth over October).
- **Post-Holiday Slowdown:** Sales drop sharply in **February 2011 to £523k** (-24.3% drop month-over-month), which is nearly 3 times lower than the November peak.
- **Top Categories:** `Home & Decor` (£2.76M) and `Kitchen & Dining` (£2.64M) drive **over 50% of total revenue**, with seasonal items spiking heavily during Q4.
- **The Pareto Principle (80/20 Rule):** Customer spending is heavily concentrated:
  - The **top 10% of customers (434 accounts)** generate **61.4% of total revenue** (£5.47 million).
  - The **top 20% of customers (868 accounts)** generate **74.6% of total revenue**.
  - Customer #14646 alone spent over £280,000.

---

## Practical Business Recommendations

1. **VIP Loyalty Program for Top 10% Customers:**  
   Because the top 10% of customers bring in 61% of total revenue, losing even a handful of these accounts would hurt cash flow. Management should assign dedicated account support, provide volume reorder discounts, and offer early access to seasonal stock.
2. **Beat the February Dip with an Early Restock Clearance:**  
   To counter the 24% sales drop in February, launch a "New Year / Spring Restock" campaign in mid-January with tiered discounts (e.g. 15% off orders above £300) to incentivize retail shop owners to restock early.
3. **Cross-Category Product Bundling:**  
   Home and Kitchen products make up half of sales, while Bags and Luggage sell frequently. Adding "Frequently Bought Together" bundle offers on the website can lift the average order value by 5% to 10%.

---

## Project Structure

```text
├── ecommerce_sales_analysis.ipynb   # Complete Jupyter Notebook containing all 8 steps
├── ecommerce_executive_brief.pdf     # 1-page business brief PDF for managers
├── ecommerce_executive_brief.png     # Visual preview of the 1-page business brief
├── online_retail_II.xlsx            # Original dataset (UCI Machine Learning Repository)
├── online_retail_II.parquet         # Fast-loading cached version of the dataset
├── project-3-guide.pdf               # Project guide and requirements
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## Step-by-Step Methodology

The project strictly follows the 8 steps from the learner guide:

1. **Understand the business question:** Formulate the key questions a store manager needs answered.
2. **Create or load the data:** Ingest the dataset and check for missing values, duplicates, and cancelled orders (`Invoice` starting with `'C'`).
3. **Add date features:** Compute revenue (`Quantity * Price`), extract month, weekday, quarter, and categorize product descriptions into realistic categories.
4. **Analyse the trend:** Group by month, compute month-over-month growth with `pct_change()`, find the best and worst months, and plot a line chart.
5. **Compare categories:** Use `groupby` for total revenue, mean item spend, and order count; build a monthly pivot table and plot category bars.
6. **Find your best customers:** Calculate spend per customer, test the 80/20 rule, and plot the cumulative revenue (Lorenz / Pareto) curve.
7. **Write recommendations:** Provide 3 actionable recommendations backed by exact numbers.
8. **Present it:** Summarize the project using the standard headings (*Context, Key findings, Recommendations, Next steps*) and generate a clean, one-page PDF.

---

## How to Run

### Requirements
- Python 3.10+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Notebook
1. Clone or download this project folder.
2. Open your terminal in this directory and launch Jupyter:
   ```bash
   jupyter notebook ecommerce_sales_analysis.ipynb
   ```
3. Run all cells from top to bottom. The notebook will process the data, display all tables and charts, and automatically re-generate `ecommerce_executive_brief.pdf`.
