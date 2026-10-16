
import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "online_retail.db"
SQL_PATH = PROJECT_ROOT / "sql" / "reports.sql"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sql_reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def split_sql_queries(sql_text):
    """Split the SQL file into individual queries using semicolons."""
    return [
        query.strip()
        for query in sql_text.split(";")
        if query.strip()
    ]

def main():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(
            f"SQL file not found: {SQL_PATH}"
        )

    sql_text = SQL_PATH.read_text(encoding="utf-8")
    queries = split_sql_queries(sql_text)

    print(f"Found {len(queries)} SQL queries.")

    with sqlite3.connect(DATABASE_PATH) as connection:
        for number, query in enumerate(queries, start=1):
            result = pd.read_sql_query(query, connection)

            output_path = OUTPUT_DIR / f"query_{number:02d}.csv"
            result.to_csv(output_path, index=False)

            print(
                f"Query {number}: {len(result)} rows "
                f"-> {output_path.relative_to(PROJECT_ROOT)}"
            )

            if not result.empty:
                print(result.head(5).to_string(index=False))
            else:
                print("No rows returned.")

            print("-" * 60)

    print("All SQL reports executed successfully.")

if __name__ == "__main__":
    main()