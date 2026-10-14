
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_DIR = PROJECT_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not DATA_FILE.exists():
        print("Dataset not found:", DATA_FILE)
        print("Place Online Retail.xlsx inside data/raw/")
        return

    df = pd.read_excel(DATA_FILE)

    print("=" * 50)
    print("ONLINE RETAIL - INITIAL DATA EXPLORATION")
    print("=" * 50)

    print("\nDataset shape:", df.shape)
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nSummary statistics:")
    print(df.describe(include="all").transpose())

    missing = df.isnull().sum().rename("MissingValues")
    duplicates = df.duplicated().sum()

    quality_report = pd.DataFrame({
        "DataType": df.dtypes.astype(str),
        "MissingValues": missing,
        "UniqueValues": df.nunique(dropna=True)
    })

    quality_report.to_csv(
        OUTPUT_DIR / "data_quality_report.csv"
    )

    print("\nMissing values by column:")
    print(missing)
    print("\nDuplicate rows:", duplicates)

    print("\nInvalid quantity rows:", (df["Quantity"] <= 0).sum())
    print("Invalid unit price rows:", (df["UnitPrice"] <= 0).sum())

    cancelled = df["InvoiceNo"].astype(str).str.startswith("C")
    print("Cancellation invoice rows:", cancelled.sum())

    sales = df.loc[
        (df["Quantity"] > 0)
        & (df["UnitPrice"] > 0)
        & (~cancelled)
    ].copy()

    sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]

    print("\n--- Preliminary Sales Analysis ---")
    print("Rows included in preliminary analysis:", len(sales))
    print("Total calculated revenue:", round(sales["Revenue"].sum(), 2))

    print("\nTop 10 countries by calculated revenue:")
    country_sales = (
        sales.groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(country_sales)

    print("\nTop 10 products by quantity sold:")
    product_sales = (
        sales.groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(product_sales)

    country_sales.to_csv(OUTPUT_DIR / "top_countries_by_revenue.csv")
    product_sales.to_csv(OUTPUT_DIR / "top_products_by_quantity.csv")

    print("\nAnalysis complete.")
    print("Preliminary reports saved in the outputs folder.")


if __name__ == "__main__":
    main()