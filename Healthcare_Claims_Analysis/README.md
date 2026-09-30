# Healthcare Claims & Admissions Data Analysis

An end-to-end data project analyzing real hospital admission records — built in three layers: Python (cleaning), SQL (analysis), and Power BI (visualization).

## Overview

This project cleans and analyzes a hospital admissions dataset (4,000 records: S/N, Gender, Diagnosis, Age, Amount billed, Date Admitted, Date Discharged), fixes real data quality issues found along the way, and surfaces cost and length-of-stay patterns.

**Note on scope:** This dataset has no fraud label. Records are flagged as statistical cost outliers (using the IQR method) — not as fraud. An outlier flag means "unusually high cost, worth a closer look," nothing more.

## Layer 1: Python (Data Cleaning & EDA)

`Healthcare_pipeline.py` loads the raw CSV, explores it for missing values and data issues, cleans it, and loads the result into a SQLite database.

**Key finding:** the `AMOUNT` column stored values with comma thousand separators (e.g., `"3,950.00"`), which caused pandas to misread ~98% of genuinely valid amounts as invalid. Fixed by stripping commas before numeric conversion — recovered the dataset from 56 usable rows to 3,988.

Other steps: parsed day-first dates (`dayfirst=True`), calculated `LENGTH_OF_STAY_DAYS`, and flagged statistical cost outliers using the IQR method (`COST_OUTLIER_FLAG`).

## Layer 2: SQL (Analysis)

`queries.sql` contains the analysis queries, including CTEs and window functions (`RANK() OVER`, `PARTITION BY`).

**Real findings from this layer:**
- The `DIAGNOSIS` field is free text, not standardized categories — grouping by exact text mostly produces single-case groups at the high-cost end.
- The same diagnosis appears with inconsistent spelling (e.g., "CERVICAL INSUFFICIENCY" / "CERVICAL INSUFFIENCY" / "CERVICAL INSUFFICENCY") — a real data-quality issue that would need normalization before reliable reporting.
- The `GENDER` field has inconsistent casing and stray values (`F`, `f`, `FF`, `M`, `m`, `MF`) — another field needing cleanup.
- Most records show 0-day length of stay; some of this is genuine same-day care, but part of it is because missing admission/discharge dates default to 0 in the cleaning step, which likely overstates the true same-day rate.

## Layer 3: Power BI (Dashboard)

`Healthcare_Dashboard.pbix` — a dashboard built directly on the cleaned data using DAX measures (not pre-aggregated in Python), including a measure that uses context transition to recalculate correctly when broken down by diagnosis.


## Tools Used

Python (pandas), SQLite, SQL (CTEs, window functions), Power BI (DAX)

## Honest Limitations

- No fraud/ground-truth label exists in this dataset — nothing here claims to detect fraud.
- The DIAGNOSIS field needs normalization for more meaningful category-level analysis.
- Length of stay figures should be interpreted with the missing-date caveat above.
