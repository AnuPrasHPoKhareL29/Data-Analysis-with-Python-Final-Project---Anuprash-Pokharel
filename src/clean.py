
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_DIR / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not RAW_FILE.exists():
        print(f"Dataset not found: {RAW_FILE}")
        print("Place Online Retail.xlsx inside data/raw/")
        return

    df = pd.read_excel(RAW_FILE)

    original_rows = len(df)
    print(f"Original number of rows: {original_rows:,}")

    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    print(f"Duplicate rows removed: {duplicate_count:,}")

    df.columns = df.columns.str.strip()

    for column in ["InvoiceNo", "StockCode", "Description", "Country"]:
        df[column] = df[column].astype("string").str.strip()

    df["Description"] = df["Description"].replace("", pd.NA)

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )
    df["CustomerID"] = pd.to_numeric(
        df["CustomerID"], errors="coerce"
    )

    missing_descriptions = int(df["Description"].isna().sum())
    missing_customer_ids = int(df["CustomerID"].isna().sum())
    invalid_dates = int(df["InvoiceDate"].isna().sum())
    invalid_quantities = int(
        (df["Quantity"].isna() | (df["Quantity"] <= 0)).sum()
    )
    invalid_prices = int(
        (df["UnitPrice"].isna() | (df["UnitPrice"] <= 0)).sum()
    )
    cancellations = int(
        df["InvoiceNo"].str.startswith("C", na=False).sum()
    )

    print("\nData-quality summary")
    print(f"Missing descriptions: {missing_descriptions:,}")
    print(f"Missing customer IDs: {missing_customer_ids:,}")
    print(f"Invalid invoice dates: {invalid_dates:,}")
    print(f"Invalid quantities: {invalid_quantities:,}")
    print(f"Invalid unit prices: {invalid_prices:,}")
    print(f"Cancellation invoice rows: {cancellations:,}")

    valid_rows = (
        df["Description"].notna()
        & df["InvoiceDate"].notna()
        & df["Quantity"].notna()
        & (df["Quantity"] > 0)
        & df["UnitPrice"].notna()
        & (df["UnitPrice"] > 0)
        & (~df["InvoiceNo"].str.startswith("C", na=False))
    )

    cleaned = df.loc[valid_rows].copy()

    cleaned["Revenue"] = (
        cleaned["Quantity"] * cleaned["UnitPrice"]
    ).round(2)

    cleaned["Year"] = cleaned["InvoiceDate"].dt.year
    cleaned["Month"] = cleaned["InvoiceDate"].dt.month
    cleaned["YearMonth"] = (
        cleaned["InvoiceDate"].dt.to_period("M").astype(str)
    )

    cleaned_file = OUTPUT_DIR / "cleaned_retail.csv"
    cleaned.to_csv(cleaned_file, index=False)

    summary = pd.DataFrame({
        "Metric": [
            "Original rows",
            "Duplicate rows removed",
            "Rows after duplicate removal",
            "Rows retained for sales analysis",
            "Rows excluded from sales analysis",
            "Missing customer IDs in retained data"
        ],
        "Value": [
            original_rows,
            duplicate_count,
            len(df),
            len(cleaned),
            len(df) - len(cleaned),
            int(cleaned["CustomerID"].isna().sum())
        ]
    })

    summary.to_csv(
        OUTPUT_DIR / "cleaning_summary.csv", index=False
    )

    print("\nCleaning completed.")
    print(f"Rows retained: {len(cleaned):,}")
    print(f"Rows excluded: {len(df) - len(cleaned):,}")
    print(f"Cleaned dataset: {cleaned_file}")
    print("Cleaning summary saved to data/processed/")

if __name__ == "__main__":
    main()