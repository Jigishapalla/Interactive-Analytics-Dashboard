# Interactive Retail Sales Analytics Dashboard

## Business question
How are sales performing over time, which products generate the most revenue, and which countries perform best?

## Features
- KPI cards for revenue, orders, unique customers, and units sold
- Interactive date-range and country filters
- Monthly revenue trend
- Top products and top countries by revenue
- Order value distribution and average order value
- Filtered transaction table and CSV export

## Dataset
This project uses the UCI Online Retail dataset. The dataset contains historical transactions from a UK-based online retailer (2010–2011). Revenue is calculated as `Quantity × UnitPrice` in GBP.

For this dashboard, cancellation invoices and transaction lines with non-positive quantities or prices are excluded. Results therefore represent the filtered positive-sales view, not official accounting totals.

## Run locally (Windows / VS Code)
1. Extract the project ZIP.
2. Open the `Interactive_Analytics_Dashboard` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. (Optional) Create/activate an Anaconda environment if you use one.
5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Run the dashboard:

   ```bash
   python -m streamlit run app.py
   ```

7. Open the local address shown in the terminal, usually `http://localhost:8501`.

## Project structure
```text
Interactive_Analytics_Dashboard/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── Online Retail.xlsx
```
