
# Online Retail ETL and Data Analysis Project

## Project Overview
This project analyzes retail transactions using Python and Pandas. The goal is to explore sales patterns, clean and transform the data, and eventually load it into a relational database for SQL reporting.

## Dataset
- **Name:** Online Retail
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online-retail)
- **Records:** 541,909
- **Columns:** 8
- **Period:** December 2010 – December 2011

## Project Structure
- `src/explore.py` — Python script for loading and inspecting the dataset.
- `01_Online_Retail_Initial_EDA.ipynb` — notebook for initial exploration.
- `requirements.txt` — required Python packages.
- `data/raw/` — location for the downloaded original Excel dataset.
- `data/processed/` — reserved for cleaned and transformed data.
- `outputs/` — location for generated analysis reports.

## Tools and Technologies
- Python
- Pandas
- VS Code
- SQL and a relational database (planned)

## Progress So Far

### Day 1

* Loaded the Online Retail dataset using Pandas.
* Inspected dataset dimensions, column names, data types, and missing values.

### Day 2

* Added duplicate-row and data-quality checks.
* Investigated non-positive quantities, prices, and cancellation invoices.
* Calculated preliminary sales revenue.
* Generated country revenue and product quantity rankings.
* Exported initial analysis reports to CSV.

## Next Steps

* Review data-quality findings and clean the dataset.
* Transform data for analysis.
* Design related database tables and an ERD.
* Load processed data into a database and create SQL reporting queries.


## How to Run
1. Download the dataset from the UCI link above.
2. Place `Online Retail.xlsx` inside `data/raw/`.
3. Install the required packages:

   `pip install -r requirements.txt`

4. Run the Python script from the project root:

   `python src/explore.py`

## Future Work
- Complete data cleaning and transformation.
- Design related database tables and an ERD.
- Load processed data into the database.
- Create SQL reporting queries.
- Document findings and prepare the final demonstration.