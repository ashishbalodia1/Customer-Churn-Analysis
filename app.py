import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="E-Commerce Sales & Customer Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean UI styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Function to categorize product descriptions
def get_category(desc):
    if not isinstance(desc, str):
        return 'Other Items'
    d = desc.upper()
    if any(k in d for k in ['CHRISTMAS', 'XMAS', 'EASTER', 'HALLOWEEN', 'HEART', 'GIFT', 'BIRTHDAY']):
        return 'Seasonal & Gifts'
    elif any(k in d for k in ['BAG', 'LUNCH', 'JUMBO', 'TOTE', 'PURSE', 'SHOPPER']):
        return 'Bags & Luggage'
    elif any(k in d for k in ['MUG', 'TEA', 'COFFEE', 'CAKE', 'BAKING', 'BOTTLE', 'BOWL', 'PLATE', 'JAR', 'CUP']):
        return 'Kitchen & Dining'
    elif any(k in d for k in ['CANDLE', 'LIGHT', 'LANTERN', 'HOLDER', 'CLOCK', 'FRAME', 'MIRROR', 'CUSHION', 'WOODEN']):
        return 'Home & Decor'
    elif any(k in d for k in ['PAPER', 'CARD', 'FELT', 'PENCIL', 'PEN', 'NOTEBOOK', 'STICKER', 'RIBBON', 'CRAFT']):
        return 'Stationery & Craft'
    else:
        return 'Other Items'

# Load and clean data with caching
@st.cache_data
def load_data():
    parquet_file = 'online_retail_II.parquet'
    excel_file = 'online_retail_II.xlsx'

    if os.path.exists(parquet_file):
        df = pd.read_parquet(parquet_file)
    elif os.path.exists(excel_file):
        df = pd.read_excel(excel_file, sheet_name='Year 2010-2011')
        df['Invoice'] = df['Invoice'].astype(str)
        df['StockCode'] = df['StockCode'].astype(str)
        df['Description'] = df['Description'].astype(str)
        df.to_parquet(parquet_file, index=False)
    else:
        rng = np.random.default_rng(42)
        n = 5000
        df = pd.DataFrame({
            "Invoice": [f"INV{1000 + i}" for i in range(n)],
            "StockCode": [f"ITEM_{rng.integers(10, 99)}" for _ in range(n)],
            "Description": rng.choice(["Ceramic Mug", "Vintage Lantern", "Jumbo Bag", "Christmas Tree Light", "Paper Card Set"], n),
            "Quantity": rng.integers(1, 25, n),
            "InvoiceDate": pd.to_datetime("2021-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
            "Price": rng.gamma(2.0, 4.0, n).round(2),
            "Customer ID": rng.integers(1001, 1301, n).astype(float),
            "Country": "United Kingdom"
        })

    # Clean data
    df_clean = df.drop_duplicates().copy()
    df_clean = df_clean[
        (~df_clean['Invoice'].astype(str).str.startswith('C')) & 
        (df_clean['Quantity'] > 0) & 
        (df_clean['Price'] > 0)
    ].copy()

    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
    df_clean['amount'] = (df_clean['Quantity'] * df_clean['Price']).round(2)
    df_clean['month'] = df_clean['InvoiceDate'].dt.to_period('M').astype(str)
    df_clean['weekday'] = df_clean['InvoiceDate'].dt.day_name()
    df_clean['quarter'] = df_clean['InvoiceDate'].dt.to_period('Q').astype(str)
    df_clean['category'] = df_clean['Description'].apply(get_category)

    return df_clean

# Load data
df = load_data()

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.title("🔍 Dashboard Filters")
st.sidebar.markdown("Filter sales data interactively:")

# Month multiselect
all_months = sorted(df['month'].unique())
selected_months = st.sidebar.multiselect(
    "Select Month(s):",
    options=all_months,
    default=all_months
)

# Category multiselect
all_categories = sorted(df['category'].unique())
selected_categories = st.sidebar.multiselect(
    "Select Product Categories:",
    options=all_categories,
    default=all_categories
)

# Apply filters
filtered_df = df[
    (df['month'].isin(selected_months)) &
    (df['category'].isin(selected_categories))
]

st.sidebar.markdown("---")
st.sidebar.subheader("📄 One-Page Brief")
pdf_path = 'ecommerce_executive_brief.pdf'
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    st.sidebar.download_button(
        label="📥 Download Executive Brief (PDF)",
        data=pdf_bytes,
        file_name="ecommerce_executive_brief.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.sidebar.markdown("---")
st.sidebar.markdown("**Author:** Ashish Balodia  \n**Project:** InternCircle Project 3  \n**Dataset:** Online Retail II (UCI)")

# ----------------- MAIN HEADER -----------------
st.markdown('<div class="main-header">📊 E-Commerce Sales & Customer Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive real-time monitoring of revenue trends, category performance, and Pareto customer segments</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please select at least one month and category.")
    st.stop()

# ----------------- KPI METRIC CARDS -----------------
total_revenue = filtered_df['amount'].sum()
total_orders = filtered_df['Invoice'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

# Customer Pareto for filtered data
reg_cust = filtered_df.dropna(subset=['Customer ID'])
if not reg_cust.empty:
    spend_per_cust = reg_cust.groupby('Customer ID')['amount'].sum().sort_values(ascending=False)
    top_10_count = int(np.ceil(0.10 * len(spend_per_cust)))
    top_10_share = (spend_per_cust.head(top_10_count).sum() / spend_per_cust.sum() * 100) if len(spend_per_cust) > 0 else 0
else:
    top_10_share = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Net Sales", f"£{total_revenue / 1e6:.2f}M" if total_revenue >= 1e6 else f"£{total_revenue:,.0f}")
with col2:
    st.metric("Total Completed Orders", f"{total_orders:,}")
with col3:
    st.metric("Average Order Value (AOV)", f"£{avg_order_value:.2f}")
with col4:
    st.metric("Top 10% Customer Share", f"{top_10_share:.1f}%")

st.markdown("---")

# ----------------- TABS SECTION -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Revenue Trends & Seasonality",
    "🏷️ Category Performance",
    "👥 Customer Pareto (80/20) Analysis",
    "📑 Executive Brief & Recommendations"
])

# ----------------- TAB 1: REVENUE TRENDS -----------------
with tab1:
    st.subheader("Monthly Revenue Trajectory")
    monthly_sales = filtered_df.groupby('month')['amount'].sum().reset_index()
    monthly_sales['MoM Growth (%)'] = (monthly_sales['amount'].pct_change() * 100).round(1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    # Top plot: Line chart
    ax1.plot(monthly_sales['month'], monthly_sales['amount'] / 1000, marker='o', color='#2563EB', linewidth=2.5)
    ax1.fill_between(monthly_sales['month'], monthly_sales['amount'] / 1000, color='#3B82F6', alpha=0.15)
    ax1.set_ylabel("Revenue (£k)", fontsize=10, fontweight='bold')
    ax1.set_title("Monthly Sales (£ Thousands)", fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Highlight peak
    if len(monthly_sales) > 0:
        best_row = monthly_sales.loc[monthly_sales['amount'].idxmax()]
        best_idx = monthly_sales.index.get_loc(monthly_sales['amount'].idxmax())
        ax1.scatter([best_row['month']], [best_row['amount'] / 1000], color='#DC2626', s=80, zorder=5)
        ax1.annotate(f"Peak: {best_row['month']}\n£{best_row['amount']/1000:,.0f}k",
                     xy=(best_idx, best_row['amount'] / 1000),
                     xytext=(best_idx - 0.8, best_row['amount'] / 1000 * 0.92),
                     arrowprops=dict(facecolor='#DC2626', shrink=0.08, width=1.2, headwidth=5),
                     color='#DC2626', fontweight='bold')

    # Bottom plot: MoM Growth bar chart
    colors = ['#10B981' if g >= 0 else '#EF4444' for g in monthly_sales['MoM Growth (%)'].fillna(0)]
    ax2.bar(monthly_sales['month'], monthly_sales['MoM Growth (%)'].fillna(0), color=colors, width=0.5)
    ax2.axhline(0, color='#64748B', linestyle='-', linewidth=0.8)
    ax2.set_ylabel("Growth (%)", fontsize=9, fontweight='bold')
    ax2.set_xlabel("Month", fontsize=10, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    st.pyplot(fig)

    # Day of week pattern
    st.markdown("#### Weekly Order Patterns")
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_df = filtered_df.groupby('weekday')['amount'].sum().reindex(dow_order).dropna().reset_index()
    
    col_dow1, col_dow2 = st.columns([2, 1])
    with col_dow1:
        fig_dow, ax_dow = plt.subplots(figsize=(8, 3.5))
        ax_dow.bar(dow_df['weekday'], dow_df['amount'] / 1000, color='#3B82F6', edgecolor='#1D4ED8')
        ax_dow.set_ylabel("Revenue (£k)", fontsize=9, fontweight='bold')
        ax_dow.set_title("Revenue by Day of Week", fontsize=11, fontweight='bold')
        ax_dow.tick_params(axis='x', rotation=30)
        ax_dow.grid(True, axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()
        st.pyplot(fig_dow)
    with col_dow2:
        st.markdown("**Observations:**")
        st.markdown("- **Peak Trading Days:** Weekdays (Thursday & Wednesday) dominate order volume.")
        st.markdown("- **Seasonality:** Major revenue surge begins in autumn (Sept–Nov) peaking for holiday gifting.")

# ----------------- TAB 2: CATEGORY PERFORMANCE -----------------
with tab2:
    st.subheader("Product Category Breakdown")
    cat_summary = filtered_df.groupby('category').agg(
        Total_Revenue=('amount', 'sum'),
        Order_Count=('Invoice', 'nunique'),
        Avg_Item_Spend=('amount', 'mean')
    ).sort_values('Total_Revenue', ascending=False)
    cat_summary['Share (%)'] = (cat_summary['Total_Revenue'] / cat_summary['Total_Revenue'].sum() * 100).round(1)

    col_cat1, col_cat2 = st.columns([1.2, 1])
    with col_cat1:
        fig_cat, ax_cat = plt.subplots(figsize=(7, 4))
        bars = ax_cat.barh(cat_summary.index[::-1], cat_summary['Total_Revenue'].values[::-1] / 1000, color='#3B82F6')
        ax_cat.set_title("Total Revenue by Category (£k)", fontsize=11, fontweight='bold')
        ax_cat.set_xlabel("Revenue (£ Thousands)", fontsize=9)
        ax_cat.grid(True, axis='x', linestyle='--', alpha=0.4)
        for b in bars:
            w = b.get_width()
            ax_cat.text(w + 10, b.get_y() + b.get_height()/2, f"£{w:,.0f}k", va='center', fontsize=8)
        ax_cat.set_xlim(0, max(cat_summary['Total_Revenue'] / 1000) * 1.2)
        plt.tight_layout()
        st.pyplot(fig_cat)

    with col_cat2:
        st.markdown("#### Category Metrics Table")
        display_cat = cat_summary.copy()
        display_cat['Total_Revenue'] = display_cat['Total_Revenue'].map("£{:,.2f}".format)
        display_cat['Avg_Item_Spend'] = display_cat['Avg_Item_Spend'].map("£{:.2f}".format)
        display_cat['Share (%)'] = display_cat['Share (%)'].map("{:.1f}%".format)
        st.dataframe(display_cat, use_container_width=True)

    st.markdown("#### Monthly Revenue by Category (Pivot Table)")
    pivot_df = filtered_df.pivot_table(index='month', columns='category', values='amount', aggfunc='sum', fill_value=0)
    st.dataframe(pivot_df.style.format("£{:,.0f}"), use_container_width=True)

# ----------------- TAB 3: CUSTOMER PARETO (80/20) -----------------
with tab3:
    st.subheader("Customer Spend Concentration (Pareto 80/20 Principle)")
    if reg_cust.empty:
        st.info("No registered customer data available for the current filter selection.")
    else:
        cust_spend_all = reg_cust.groupby('Customer ID')['amount'].sum().sort_values(ascending=False)
        total_reg_rev = cust_spend_all.sum()
        total_reg_customers = len(cust_spend_all)

        n_top10 = int(np.ceil(0.10 * total_reg_customers))
        rev_top10 = cust_spend_all.head(n_top10).sum()
        pct_top10 = (rev_top10 / total_reg_rev * 100) if total_reg_rev > 0 else 0

        n_top20 = int(np.ceil(0.20 * total_reg_customers))
        rev_top20 = cust_spend_all.head(n_top20).sum()
        pct_top20 = (rev_top20 / total_reg_rev * 100) if total_reg_rev > 0 else 0

        col_p1, col_p2 = st.columns([1.3, 1])
        with col_p1:
            fig_p, ax_p = plt.subplots(figsize=(7, 4.2))
            cum_cust = np.linspace(0, 100, total_reg_customers)
            cum_rev = np.cumsum(cust_spend_all.values) / total_reg_rev * 100

            ax_p.plot(cum_cust, cum_rev, color='#1E40AF', linewidth=2.5, label='Actual Customer Spend')
            ax_p.plot([0, 100], [0, 100], color='#94A3B8', linestyle='--', label='Equal Share (Baseline)')
            ax_p.axvline(10, color='#D97706', linestyle=':')
            ax_p.scatter([10], [pct_top10], color='#D97706', s=50, zorder=5)
            ax_p.annotate(f"Top 10% bring {pct_top10:.0f}%", xy=(10, pct_top10),
                         xytext=(18, pct_top10 - 8),
                         arrowprops=dict(facecolor='#D97706', shrink=0.08, width=1, headwidth=4),
                         fontweight='bold', color='#D97706')

            ax_p.set_title("Lorenz Curve: Customer Revenue Concentration", fontsize=11, fontweight='bold')
            ax_p.set_xlabel("% of Customers", fontsize=9)
            ax_p.set_ylabel("Cumulative % of Sales", fontsize=9)
            ax_p.legend(loc='lower right', fontsize=8.5)
            ax_p.grid(True, linestyle='--', alpha=0.4)
            plt.tight_layout()
            st.pyplot(fig_p)

        with col_p2:
            st.markdown("#### Pareto Rule Findings")
            st.markdown(f"- **Total Registered Accounts:** {total_reg_customers:,}")
            st.markdown(f"- **Top 10% ({n_top10:,} accounts):** Generate **£{rev_top10:,.2f}** ({pct_top10:.1f}% of sales)")
            st.markdown(f"- **Top 20% ({n_top20:,} accounts):** Generate **£{rev_top20:,.2f}** ({pct_top20:.1f}% of sales)")
            st.info("💡 **Insight:** The Pareto principle holds strong. Protecting the top 10% client accounts is critical because losing even a small fraction directly damages over 60% of commercial revenue.")

        st.markdown("#### Top 10 Most Valuable Client Accounts")
        top_10_table = pd.DataFrame({
            'Customer ID': [str(int(c)) for c in cust_spend_all.head(10).index],
            'Total Spend': cust_spend_all.head(10).values,
            'Order Count': [reg_cust[reg_cust['Customer ID'] == c]['Invoice'].nunique() for c in cust_spend_all.head(10).index]
        })
        top_10_table['Total Spend'] = top_10_table['Total Spend'].map("£{:,.2f}".format)
        st.dataframe(top_10_table, use_container_width=True)

# ----------------- TAB 4: EXECUTIVE BRIEF & RECOMMENDATIONS -----------------
with tab4:
    st.subheader("📑 One-Page Business Brief for Management")
    st.markdown("*Structured for executive review in under 2 minutes.*")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("### 1. Context")
        st.write("We analyzed over 530,000 completed transactions from the Online Retail II dataset (December 2010 to December 2011) to understand seasonal sales trends, identify best-selling products, and find our most valuable customer accounts.")

        st.markdown("### 2. Key Findings")
        st.markdown("- **Sales peak in November (£1.51M):** Revenue builds up during autumn and peaks in November due to holiday shopping. The slowest full month is **February (£523k)**, which is nearly 3 times lower than November.")
        st.markdown("- **Two categories make up half the sales:** Home & Decor (£2.76M) and Kitchen & Dining (£2.64M) drive over 50% of all revenue.")
        st.markdown("- **Pareto rule holds:** The **top 10% of customers (434 accounts) generate 61.4% of sales** (£5.47M), while the top 20% generate 74.6%.")

    with col_b2:
        st.markdown("### 3. Actionable Recommendations")
        st.markdown("1. **VIP Loyalty Program:** Give dedicated support, early access to seasonal collections, and bulk reorder discounts to the top 10% of customers who bring in over 60% of revenue.")
        st.markdown("2. **Beat the February Dip:** Run a January restocking clearance promotion (e.g. 15% off orders over £300) so retail shop owners restock before the slow month.")
        st.markdown("3. **Cross-Category Bundles:** Pair popular Home and Kitchen products with Bags on the website to lift average order value by 5% to 10%.")

        st.markdown("### 4. Implementation Next Steps")
        st.markdown("- **Month 1:** Reach out to the top 50 corporate clients and set up VIP benefits.")
        st.markdown("- **Month 2:** Launch the January clearance sale and introduce product bundles on the store.")
        st.markdown("- **Month 3:** Review Q1 performance and place advance inventory orders for Q4 holiday stock.")

    st.markdown("---")
    if os.path.exists(pdf_path):
        st.download_button(
            label="📥 Download Complete One-Page Brief (PDF)",
            data=pdf_bytes,
            file_name="ecommerce_executive_brief.pdf",
            mime="application/pdf"
        )

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: #94A3B8; font-size: 0.85rem;'>E-Commerce Sales & Customer Analytics Dashboard | InternCircle Project 3 | Developed by Ashish Balodia</div>", unsafe_allow_html=True)
