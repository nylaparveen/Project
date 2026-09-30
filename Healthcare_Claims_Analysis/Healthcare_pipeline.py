"""
Healthcare Claims & Admissions Data Analysis
Cleans a raw hospital admissions CSV, explores it for data quality issues
and cost patterns, flags statistically unusual bills using an IQR-based
threshold, and loads the cleaned data into a local SQLite database.
"""

import os
import sqlite3
import pandas as pd


def explore_data(file_path: str) -> pd.DataFrame:
    """
    Loads the raw CSV and prints basic exploratory checks:
    dataset size, missing values, and billing amount statistics.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find file: {file_path}")

    df = pd.read_csv(file_path)

    # The raw column headers have extra spaces (e.g. " AGE ", " AMOUNT  ").
    # Strip whitespace from every column name so we can reference them cleanly.
    df.columns = df.columns.str.strip()

    print("=== Exploratory Data Analysis ===")
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}\n")

    # Check for missing values in each column
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print("Missing values found:")
        print(missing)
    else:
        print("No missing values found.")
    print()

    df["AMOUNT"] = df["AMOUNT"].astype(str).str.replace(",", "", regex=False)
    
    # Basic statistics on the billing amount
    if "AMOUNT" in df.columns:
        # Before converting to numbers, capture which raw values will fail —
        # this tells us exactly what's wrong with the data, instead of just
        # silently losing rows.
        numeric_attempt = pd.to_numeric(df["AMOUNT"], errors="coerce")
        failed_mask = numeric_attempt.isna() & df["AMOUNT"].notna()
        failed_values = df.loc[failed_mask, "AMOUNT"]

        if len(failed_values) > 0:
            print(f"AMOUNT: {len(failed_values)} values could not be converted to numbers.")
            print("Sample of the actual raw text found in these rows:")
            print(failed_values.value_counts().head(10))
            print()

        df["AMOUNT"] = numeric_attempt

        print("Amount summary (valid numeric values only):")
        print(df["AMOUNT"].describe())
        print()

        # Use the IQR method to flag unusually high bills.
        # Anything above Q3 + 1.5*IQR is considered a statistical outlier.
        q1 = df["AMOUNT"].quantile(0.25)
        q3 = df["AMOUNT"].quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr

        outliers = df[df["AMOUNT"] > upper_bound]
        print(f"Outlier threshold (Q3 + 1.5*IQR): {upper_bound:,.2f}")
        print(f"Number of outlier bills: {len(outliers)} ({len(outliers)/len(df)*100:.1f}% of records)")
        print()

    # Most common diagnoses, since this dataset has no fraud label —
    # this is a genuine, honest angle this data can actually support.
    if "DIAGNOSIS" in df.columns:
        print("Top diagnoses by frequency:")
        print(df["DIAGNOSIS"].value_counts().head(10))
        print()

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataset: removes rows missing key fields, fixes data types,
    and calculates length of hospital stay from admission/discharge dates.
    """
    print("=== Cleaning Data ===")

    # Drop rows where we don't have a serial number or amount —
    # these rows can't be meaningfully analysed.
    before = len(df)
    df = df.dropna(subset=["S/N", "AMOUNT"]).copy()
    print(f"Dropped {before - len(df)} rows missing S/N or AMOUNT")

    # Convert admission/discharge dates to real date objects so we can
    # calculate the number of days between them.
    # Dates in this file are in day/month/year format (e.g. 01/03/2024).
    if "DATE ADMITTED" in df.columns and "DATE DISCHARGED" in df.columns:
        df["DATE ADMITTED"] = pd.to_datetime(df["DATE ADMITTED"], errors="coerce", dayfirst=True)
        df["DATE DISCHARGED"] = pd.to_datetime(df["DATE DISCHARGED"], errors="coerce", dayfirst=True)

        # Length of stay = discharge date minus admission date, in days.
        # Negative values (data entry errors) are set to 0.
        df["LENGTH_OF_STAY_DAYS"] = (df["DATE DISCHARGED"] - df["DATE ADMITTED"]).dt.days
        df["LENGTH_OF_STAY_DAYS"] = df["LENGTH_OF_STAY_DAYS"].clip(lower=0).fillna(0).astype(int)
        print("Calculated LENGTH_OF_STAY_DAYS from admission/discharge dates")

    # Flag unusually high bills using the same IQR method from the EDA step.
    # IMPORTANT: this is a statistical outlier flag, not a fraud determination.
    # It highlights records that are worth a closer manual look — nothing more.
    if "AMOUNT" in df.columns:
        q1 = df["AMOUNT"].quantile(0.25)
        q3 = df["AMOUNT"].quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr

        df["COST_OUTLIER_FLAG"] = df["AMOUNT"].apply(
            lambda amount: "ABOVE_THRESHOLD" if amount > upper_bound else "NORMAL_RANGE"
        )
        flagged_count = (df["COST_OUTLIER_FLAG"] == "ABOVE_THRESHOLD").sum()
        print(f"Flagged {flagged_count} records as ABOVE_THRESHOLD (billing amount above ${upper_bound:,.2f})")

    print()
    return df


def load_to_database(df: pd.DataFrame, db_path: str) -> None:
    """
    Saves the cleaned data into a local SQLite database table.
    """
    print("=== Loading to Database ===")

    conn = sqlite3.connect(db_path)
    df.to_sql("hospital_admissions", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Saved {len(df)} cleaned records to '{db_path}' (table: hospital_admissions)")


if __name__ == "__main__":
    SOURCE_FILE = "PROJECT RESEARCH final.csv"
    DATABASE_FILE = "healthcare_analytics.db"

    raw_df = explore_data(SOURCE_FILE)
    cleaned_df = clean_data(raw_df)
    load_to_database(cleaned_df, DATABASE_FILE)

    print("\nDone. Open healthcare_analytics.db in DB Browser for SQLite to explore the results.")