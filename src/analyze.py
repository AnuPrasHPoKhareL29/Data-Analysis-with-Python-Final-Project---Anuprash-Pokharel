
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "cleaned_retail.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

def main():
    if not DATA_FILE.exists():
        print("Cleaned dataset not found.")
        print("Run python src/clean.py first.")
        return

    print("Loading cleaned retail data...")
    df = pd.read_csv(
        DATA_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "Description": "string",
            "Country": "string"
        },
        parse_dates=["InvoiceDate"]
    )

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")

    df = df.dropna(
        subset=["InvoiceNo", "InvoiceDate", "Quantity",
                "UnitPrice", "Revenue", "Country"]
    ).copy()

    print(f"Rows available for analysis: {len(df):,}")
    print(f"Total revenue: {df['Revenue'].sum():,.2f}")

    country_revenue = (
        df.groupby("Country", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    country_revenue.to_csv(
        OUTPUT_DIR / "country_revenue.csv", index=False
    )

    print("\n1. Top 10 countries by revenue")
    print(country_revenue.head(10).to_string(index=False))

    product_quantity = (
        df.groupby("Description", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
    )

    product_quantity.to_csv(
        OUTPUT_DIR / "product_quantity.csv", index=False
    )

    print("\n2. Top 10 products by quantity sold")
    print(product_quantity.head(10).to_string(index=False))

    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    monthly_revenue = (
        df.groupby("YearMonth", as_index=False)["Revenue"]
        .sum()
        .sort_values("YearMonth")
    )

    monthly_revenue.to_csv(
        OUTPUT_DIR / "monthly_revenue.csv", index=False
    )

    print("\n3. Monthly revenue")
    print(monthly_revenue.to_string(index=False))

    identified_customers = df.dropna(subset=["CustomerID"]).copy()

    customer_revenue = (
        identified_customers.groupby("CustomerID", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique")
        )
        .sort_values("Revenue", ascending=False)
    )

    customer_revenue.to_csv(
        OUTPUT_DIR / "customer_revenue.csv", index=False
    )

    print("\n4. Top 10 customers by revenue")
    print(customer_revenue.head(10).to_string(index=False))

    order_summary = (
        df.groupby("InvoiceNo", as_index=False)
        .agg(
            OrderRevenue=("Revenue", "sum"),
            TotalItems=("Quantity", "sum"),
            InvoiceDate=("InvoiceDate", "first"),
            Country=("Country", "first")
        )
    )

    order_summary.to_csv(
        OUTPUT_DIR / "order_summary.csv", index=False
    )

    average_order_value = order_summary["OrderRevenue"].mean()
    median_order_value = order_summary["OrderRevenue"].median()
    total_orders = order_summary["InvoiceNo"].nunique()

    order_metrics = pd.DataFrame({
        "Metric": [
            "Total orders",
            "Average order value",
            "Median order value",
            "Average items per order"
        ],
        "Value": [
            total_orders,
            round(average_order_value, 2),
            round(median_order_value, 2),
            round(order_summary["TotalItems"].mean(), 2)
        ]
    })

    order_metrics.to_csv(
        OUTPUT_DIR / "order_metrics.csv", index=False
    )

    print("\n5. Order-level metrics")
    print(order_metrics.to_string(index=False))

    plt.figure(figsize=(10, 5))
    plt.plot(
        monthly_revenue["YearMonth"],
        monthly_revenue["Revenue"],
        marker="o"
    )
    plt.title("Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "monthly_revenue.png", dpi=150)
    plt.close()

    top_countries = country_revenue.head(10).sort_values("Revenue")

    plt.figure(figsize=(10, 6))
    plt.barh(top_countries["Country"], top_countries["Revenue"])
    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "top_countries_revenue.png", dpi=150)
    plt.close()

    findings = [
        f"Total revenue across included records: {df['Revenue'].sum():.2f}.",
        f"Country with the highest revenue: {country_revenue.iloc[0]['Country']}.",
        f"Highest-quantity product: {product_quantity.iloc[0]['Description']}.",
        f"Number of distinct orders: {total_orders}.",
        f"Average order value: {average_order_value:.2f}."
    ]

    with open(OUTPUT_DIR / "preliminary_insights.txt", "w",
              encoding="utf-8") as file:
        file.write("Preliminary Retail Analysis Findings\n\n")
        for number, finding in enumerate(findings, start=1):
            file.write(f"{number}. {finding}\n")

    print("\nAnalysis complete.")
    print(f"Reports saved to: {OUTPUT_DIR}")
    print(f"Charts saved to: {CHART_DIR}")


if __name__ == "__main__":
    main()