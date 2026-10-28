from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="📊",
    layout="wide",
)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "Online Retail.xlsx"

st.title("📊 Interactive Retail Sales Dashboard")
st.write(
    "Explore historical retail sales, discover top products, and compare "
    "country performance using real transaction data."
)


@st.cache_data(show_spinner="Loading and cleaning retail data...")
def load_data(file_path: str) -> pd.DataFrame:
    data = pd.read_excel(file_path)
    data.columns = data.columns.str.strip()

    required = {
        "InvoiceNo", "StockCode", "Description", "Quantity",
        "InvoiceDate", "UnitPrice", "CustomerID", "Country"
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            "The dataset is missing expected columns: " + ", ".join(sorted(missing))
        )

    data["InvoiceNo"] = data["InvoiceNo"].astype(str).str.strip()
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Quantity"] = pd.to_numeric(data["Quantity"], errors="coerce")
    data["UnitPrice"] = pd.to_numeric(data["UnitPrice"], errors="coerce")
    data["Description"] = data["Description"].astype("string").str.strip()
    data["Country"] = data["Country"].astype("string").str.strip()

    data = data.dropna(
        subset=["InvoiceDate", "Quantity", "UnitPrice", "Description", "Country"]
    )
    # Exclude cancellation invoices and non-positive sales lines for this dashboard.
    data = data[
        ~data["InvoiceNo"].str.upper().str.startswith("C")
        & (data["Quantity"] > 0)
        & (data["UnitPrice"] > 0)
        & data["Description"].ne("")
    ].copy()

    data["Revenue"] = data["Quantity"] * data["UnitPrice"]
    data["Date"] = data["InvoiceDate"].dt.date
    data["Month"] = data["InvoiceDate"].dt.to_period("M").astype(str)
    return data


if not DATA_PATH.exists():
    st.error("Dataset file not found.")
    st.info("Make sure 'Online Retail.xlsx' is inside the project's data folder.")
    st.code("Interactive_Analytics_Dashboard/data/Online Retail.xlsx")
    st.stop()

try:
    df = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.info("Check that the Excel file is intact and install the requirements.")
    st.stop()

if df.empty:
    st.error("No valid sales records remain after cleaning.")
    st.stop()

st.sidebar.header("🔎 Filters")
min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

all_countries = sorted(df["Country"].dropna().unique().tolist())
default_country = ["United Kingdom"] if "United Kingdom" in all_countries else all_countries[:1]
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=all_countries,
    default=default_country,
)
top_n = st.sidebar.slider("Top products to display", min_value=5, max_value=20, value=10)

if len(date_range) != 2:
    st.info("Choose both a start date and an end date.")
    st.stop()

start_date, end_date = date_range
if start_date > end_date:
    st.warning("The start date must be on or before the end date.")
    st.stop()
if not selected_countries:
    st.info("Select at least one country in the sidebar.")
    st.stop()

filtered = df[
    df["Date"].between(start_date, end_date)
    & df["Country"].isin(selected_countries)
].copy()

if filtered.empty:
    st.warning("No sales match these filters. Try a wider date range or more countries.")
    st.stop()

revenue = float(filtered["Revenue"].sum())
orders = int(filtered["InvoiceNo"].nunique())
customers = int(filtered["CustomerID"].nunique())
units = int(filtered["Quantity"].sum())
average_order_value = revenue / orders if orders else 0.0

st.caption(
    f"Period: {start_date:%d %b %Y} – {end_date:%d %b %Y} · "
    f"{len(filtered):,} transaction lines after cleaning"
)

st.subheader("Key performance indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total revenue", f"£{revenue:,.2f}")
k2.metric("Orders", f"{orders:,}")
k3.metric("Unique customers", f"{customers:,}")
k4.metric("Units sold", f"{units:,}")

st.subheader("Monthly revenue trend")
monthly = (
    filtered.groupby("Month", as_index=False)["Revenue"]
    .sum()
    .sort_values("Month")
)
trend_fig = px.line(
    monthly,
    x="Month",
    y="Revenue",
    markers=True,
    template="plotly_white",
    labels={"Month": "Month", "Revenue": "Revenue (£)"},
)
trend_fig.update_layout(hovermode="x unified", yaxis_tickprefix="£")
st.plotly_chart(trend_fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Top products by revenue")
    product_sales = (
        filtered.groupby("Description", as_index=False)["Revenue"]
        .sum()
        .nlargest(top_n, "Revenue")
        .sort_values("Revenue")
    )
    product_fig = px.bar(
        product_sales,
        x="Revenue",
        y="Description",
        orientation="h",
        template="plotly_white",
        labels={"Revenue": "Revenue (£)", "Description": "Product"},
    )
    product_fig.update_layout(xaxis_tickprefix="£")
    st.plotly_chart(product_fig, use_container_width=True)

with right:
    st.subheader("Top countries by revenue")
    country_sales = (
        filtered.groupby("Country", as_index=False)["Revenue"]
        .sum()
        .nlargest(10, "Revenue")
        .sort_values("Revenue")
    )
    country_fig = px.bar(
        country_sales,
        x="Revenue",
        y="Country",
        orientation="h",
        template="plotly_white",
        labels={"Revenue": "Revenue (£)", "Country": "Country"},
    )
    country_fig.update_layout(xaxis_tickprefix="£")
    st.plotly_chart(country_fig, use_container_width=True)

st.subheader("Order value distribution")
order_values = (
    filtered.groupby("InvoiceNo", as_index=False)["Revenue"]
    .sum()
    .rename(columns={"Revenue": "Order revenue (£)"})
)
st.metric("Average order value", f"£{average_order_value:,.2f}")
order_fig = px.histogram(
    order_values,
    x="Order revenue (£)",
    nbins=40,
    template="plotly_white",
    labels={"Order revenue (£)": "Order revenue (£)"},
)
st.plotly_chart(order_fig, use_container_width=True)

st.subheader("Filtered transaction records")
display_columns = [
    "InvoiceNo", "InvoiceDate", "Description", "Quantity",
    "UnitPrice", "Revenue", "Country", "CustomerID"
]
st.dataframe(
    filtered[display_columns].sort_values("InvoiceDate", ascending=False),
    use_container_width=True,
    hide_index=True,
)

csv_bytes = filtered[display_columns].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered sales as CSV",
    data=csv_bytes,
    file_name="filtered_sales.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "Data source: UCI Online Retail (historical 2010–2011 transactions). "
    "Revenue is Quantity × UnitPrice in GBP. Cancellation invoices and "
    "non-positive quantities/prices are excluded from this sales view. "
    "This is an analytical view, not an official accounting statement."
)
