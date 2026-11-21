import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Pizza Sales Dashboard",
    page_icon="🍕",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main-header {
    background-color: #1F3B67;
    padding: 15px;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel(
        "data/Pizza Sales.xlsx"
    )

    # Remove total row
    df = df[df["Order ID"] != "Total"]

    df["Order Date"] = pd.to_datetime(
        df["Order Date"]
    )

    return df


df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

store_filter = st.sidebar.multiselect(
    "Store",
    options=sorted(df["Store"].dropna().unique()),
    default=sorted(df["Store"].dropna().unique())
)

category_filter = st.sidebar.multiselect(
    "Category",
    options=sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique())
)

size_filter = st.sidebar.multiselect(
    "Size",
    options=sorted(df["Size"].dropna().unique()),
    default=sorted(df["Size"].dropna().unique())
)

date_range = st.sidebar.date_input(
    "Date Range",
    (
        df["Order Date"].min(),
        df["Order Date"].max()
    )
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["Store"].isin(store_filter)
]

filtered_df = filtered_df[
    filtered_df["Category"].isin(category_filter)
]

filtered_df = filtered_df[
    filtered_df["Size"].isin(size_filter)
]

if len(date_range) == 2:

    start_date = pd.to_datetime(
        date_range[0]
    )

    end_date = pd.to_datetime(
        date_range[1]
    )

    filtered_df = filtered_df[
        (
            filtered_df["Order Date"]
            >= start_date
        )
        &
        (
            filtered_df["Order Date"]
            <= end_date
        )
    ]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_sales = filtered_df["Total Sales"].sum()

total_orders = (
    filtered_df["Order ID"]
    .nunique()
)

total_units = (
    filtered_df["Quantity"]
    .sum()
)

avg_order_value = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

top_pizza = (
    filtered_df.groupby("Pizza")
    ["Total Sales"]
    .sum()
    .idxmax()
)

top_store = (
    filtered_df.groupby("Store")
    ["Total Sales"]
    .sum()
    .idxmax()
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class='main-header'>
<h1>🍕 October 2026 Pizza Sales Performance Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    "💰 Total Sales",
    f"${total_sales:,.2f}"
)

c2.metric(
    "📦 Orders",
    f"{total_orders:,}"
)

c3.metric(
    "🍕 Units Sold",
    f"{total_units:,}"
)

c4.metric(
    "📈 Avg Order Value",
    f"${avg_order_value:,.2f}"
)

c5.metric(
    "🏆 Top Pizza",
    top_pizza
)

c6.metric(
    "🏬 Top Store",
    top_store
)

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

st.info(
    f"""
    Showing {len(filtered_df)} transactions |
    Stores: {filtered_df['Store'].nunique()} |
    Categories: {filtered_df['Category'].nunique()} |
    Pizzas: {filtered_df['Pizza'].nunique()}
    """
)

# --------------------------------------------------
# WEEK COLUMN
# --------------------------------------------------

filtered_df["Week"] = (
    filtered_df["Order Date"]
    .dt.isocalendar()
    .week
)

# --------------------------------------------------
# WEEKLY SALES TREND
# --------------------------------------------------

weekly_sales = (
    filtered_df.groupby("Week")
    ["Total Sales"]
    .sum()
    .reset_index()
)

fig_weekly = px.line(
    weekly_sales,
    x="Week",
    y="Total Sales",
    markers=True,
    title="Weekly Sales Trend"
)

# --------------------------------------------------
# SALES BY STORE
# --------------------------------------------------

store_sales = (
    filtered_df.groupby("Store")
    ["Total Sales"]
    .sum()
    .reset_index()
)

fig_store = px.bar(
    store_sales,
    x="Store",
    y="Total Sales",
    color="Store",
    text_auto=".0f",
    title="Sales by Store"
)

# --------------------------------------------------
# TOP PIZZAS
# --------------------------------------------------

pizza_sales = (
    filtered_df.groupby("Pizza")
    ["Total Sales"]
    .sum()
    .reset_index()
)

pizza_sales = pizza_sales.sort_values(
    "Total Sales",
    ascending=False
)

fig_pizza = px.bar(
    pizza_sales,
    x="Total Sales",
    y="Pizza",
    orientation="h",
    color="Total Sales",
    title="Top Selling Pizzas"
)

# --------------------------------------------------
# FIRST ROW CHARTS
# --------------------------------------------------

r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    st.plotly_chart(
        fig_weekly,
        use_container_width=True
    )

with r1c2:
    st.plotly_chart(
        fig_store,
        use_container_width=True
    )

with r1c3:
    st.plotly_chart(
        fig_pizza,
        use_container_width=True
    )

# --------------------------------------------------
# CATEGORY MIX
# --------------------------------------------------

category_sales = (
    filtered_df.groupby("Category")
    ["Total Sales"]
    .sum()
    .reset_index()
)

fig_category = px.pie(
    category_sales,
    names="Category",
    values="Total Sales",
    hole=0.6,
    title="Category Mix",
    color_discrete_sequence=[
        "#1F77B4",
        "#2CA02C",
        "#FF7F0E"
    ]
)

# --------------------------------------------------
# SALES BY SIZE
# --------------------------------------------------

size_sales = (
    filtered_df.groupby("Size")
    ["Total Sales"]
    .sum()
    .reset_index()
)

fig_size = px.bar(
    size_sales,
    x="Size",
    y="Total Sales",
    color="Size",
    title="Sales by Size"
)

# --------------------------------------------------
# STORE SCORECARD
# --------------------------------------------------

scorecard = (
    filtered_df.groupby("Store")
    .agg(
        Sales=("Total Sales", "sum"),
        Orders=("Order ID", "count"),
        Units=("Quantity", "sum")
    )
    .reset_index()
)

scorecard["Avg Order"] = (
    scorecard["Sales"]
    /
    scorecard["Orders"]
)

scorecard["Share %"] = (
    scorecard["Sales"]
    /
    scorecard["Sales"].sum()
    * 100
)

scorecard["Sales"] = scorecard["Sales"].map(
    lambda x: f"${x:,.2f}"
)

scorecard["Avg Order"] = scorecard["Avg Order"].map(
    lambda x: f"${x:,.2f}"
)

scorecard["Share %"] = scorecard["Share %"].map(
    lambda x: f"{x:.1f}%"
)

# --------------------------------------------------
# SECOND ROW
# --------------------------------------------------

r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

with r2c2:
    st.plotly_chart(
        fig_size,
        use_container_width=True
    )

with r2c3:

    st.subheader(
        "Store Scorecard"
    )

    st.dataframe(
        scorecard,
        use_container_width=True
    )

# --------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------

csv = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="pizza_sales_filtered.csv",
    mime="text/csv"
)

# --------------------------------------------------
# TRANSACTION DETAILS
# --------------------------------------------------

st.markdown("---")

st.subheader(
    "Transaction Details"
)

display_df = filtered_df.copy()

if "Week" in display_df.columns:
    display_df = display_df.drop(
        columns=["Week"]
    )

st.dataframe(
    display_df,
    use_container_width=True
)