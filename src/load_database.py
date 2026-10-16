
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "cleaned_retail.csv"
DB_DIR = PROJECT_DIR / "data" / "database"
DB_FILE = DB_DIR / "online_retail.db"

DB_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not DATA_FILE.exists():
        print("Cleaned dataset not found. Run python src/clean.py first.")
        return

    print("Reading cleaned dataset...")
    df = pd.read_csv(DATA_FILE, dtype={"InvoiceNo": str, "StockCode": str})

    # Normalize identifiers and prepare the data
    df["InvoiceNo"] = df["InvoiceNo"].str.strip()
    df["StockCode"] = df["StockCode"].str.strip()
    df["Description"] = df["Description"].fillna("Unknown").str.strip()
    df["Country"] = df["Country"].fillna("Unknown").str.strip()

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")

    # Keep rows with the required invoice, product, date, quantity and price
    df = df.dropna(
        subset=["InvoiceNo", "StockCode", "InvoiceDate",
                "Quantity", "UnitPrice", "Revenue"]
    ).copy()

    # Use whole-number IDs when present; keep missing IDs as None
    df["CustomerID"] = df["CustomerID"].apply(
        lambda x: int(x) if pd.notna(x) else None
    )

    # Build dimension tables
    customers = (
        df.loc[df["CustomerID"].notna(), ["CustomerID", "Country"]]
        .drop_duplicates(subset=["CustomerID"])
        .copy()
    )

    products = (
        df[["StockCode", "Description"]]
        .drop_duplicates(subset=["StockCode"])
        .copy()
    )

    # One invoice should have one date and customer ID.
    # Country is included on the invoice to support country-level reporting.
    invoices = (
        df.groupby("InvoiceNo", as_index=False)
        .agg(
            InvoiceDate=("InvoiceDate", "min"),
            CustomerID=("CustomerID", "first"),
            Country=("Country", "first")
        )
    )

    invoice_items = df[
        ["InvoiceNo", "StockCode", "Quantity", "UnitPrice", "Revenue"]
    ].copy()

    # Use a surrogate line-item ID because an invoice can contain repeated
    # occurrences of a stock code in the source data.
    invoice_items.insert(
        0, "InvoiceItemID", range(1, len(invoice_items) + 1)
    )

    # Create the relational database
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.executescript("""
            DROP TABLE IF EXISTS InvoiceItems;
            DROP TABLE IF EXISTS Invoices;
            DROP TABLE IF EXISTS Products;
            DROP TABLE IF EXISTS Customers;

            CREATE TABLE Customers (
                CustomerID INTEGER PRIMARY KEY,
                Country TEXT NOT NULL
            );

            CREATE TABLE Products (
                StockCode TEXT PRIMARY KEY,
                Description TEXT NOT NULL
            );

            CREATE TABLE Invoices (
                InvoiceNo TEXT PRIMARY KEY,
                InvoiceDate TEXT NOT NULL,
                CustomerID INTEGER,
                Country TEXT NOT NULL,
                FOREIGN KEY (CustomerID)
                    REFERENCES Customers(CustomerID)
            );

            CREATE TABLE InvoiceItems (
                InvoiceItemID INTEGER PRIMARY KEY,
                InvoiceNo TEXT NOT NULL,
                StockCode TEXT NOT NULL,
                Quantity INTEGER NOT NULL CHECK (Quantity > 0),
                UnitPrice REAL NOT NULL CHECK (UnitPrice > 0),
                Revenue REAL NOT NULL CHECK (Revenue >= 0),
                FOREIGN KEY (InvoiceNo)
                    REFERENCES Invoices(InvoiceNo),
                FOREIGN KEY (StockCode)
                    REFERENCES Products(StockCode)
            );
        """)

        customers.to_sql("Customers", connection, if_exists="append", index=False)
        products.to_sql("Products", connection, if_exists="append", index=False)

        invoices["InvoiceDate"] = invoices["InvoiceDate"].astype(str)
        invoices.to_sql("Invoices", connection, if_exists="append", index=False)
        invoice_items.to_sql(
            "InvoiceItems", connection, if_exists="append", index=False
        )

        # Verify the relationships and table counts
        connection.execute("PRAGMA foreign_key_check")
        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print("\nDatabase loading results:")
        for table in ["Customers", "Products", "Invoices", "InvoiceItems"]:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count:,} rows")

        if foreign_key_errors:
            print("Foreign key errors found:", foreign_key_errors[:10])
        else:
            print("Foreign key check: passed")

    print(f"\nDatabase saved to: {DB_FILE}")


if __name__ == "__main__":
    main()