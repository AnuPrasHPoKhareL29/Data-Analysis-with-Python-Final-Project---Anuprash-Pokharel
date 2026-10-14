
from pathlib import Path
import pandas as pd

# Find the project folder and dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "raw" / "Online Retail.xlsx"

if not file_path.exists():
    print("Dataset not found.")
    print("Place Online Retail.xlsx inside data/raw/")
else:
    data = pd.read_excel(file_path)

    print("Dataset loaded successfully!")
    print("Number of rows:", data.shape[0])
    print("Number of columns:", data.shape[1])

    print("\nFirst five records:")
    print(data.head())

    print("\nColumn information:")
    data.info()

    print("\nMissing values:")
    print(data.isnull().sum())