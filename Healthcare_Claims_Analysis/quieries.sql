-- Healthcare Claims & Admissions Data Analysis
-- Layer 2: SQL Analysis
-- Run against healthcare_analytics.db, table: hospital_admissions

-- 1. Average bill and length of stay by diagnosis
SELECT
    DIAGNOSIS,
    COUNT(*) AS num_cases,
    ROUND(AVG(AMOUNT), 2) AS avg_amount,
    ROUND(AVG(LENGTH_OF_STAY_DAYS), 1) AS avg_stay_days
FROM hospital_admissions
GROUP BY DIAGNOSIS
ORDER BY avg_amount DESC
LIMIT 10;


-- 2. Cost outliers by diagnosis
-- NOTE: COST_OUTLIER_FLAG is a statistical outlier flag (IQR method), not a
-- fraud determination. This dataset has no fraud label.
SELECT
    DIAGNOSIS,
    COUNT(*) AS outlier_count,
    ROUND(AVG(AMOUNT), 2) AS avg_outlier_amount
FROM hospital_admissions
WHERE COST_OUTLIER_FLAG = 'ABOVE_THRESHOLD'
GROUP BY DIAGNOSIS
ORDER BY outlier_count DESC
LIMIT 10;


-- 3. CTE + RANK window function: diagnoses ranked by average cost
WITH diagnosis_avg AS (
    SELECT
        DIAGNOSIS,
        AVG(AMOUNT) AS avg_amount,
        COUNT(*) AS num_cases
    FROM hospital_admissions
    GROUP BY DIAGNOSIS
)
SELECT
    DIAGNOSIS,
    num_cases,
    ROUND(avg_amount, 2) AS avg_amount,
    RANK() OVER (ORDER BY avg_amount DESC) AS cost_rank
FROM diagnosis_avg
ORDER BY cost_rank
LIMIT 10;


-- 4. Window function: each bill compared to its diagnosis's average
SELECT
    "S/N",
    DIAGNOSIS,
    AMOUNT,
    ROUND(AVG(AMOUNT) OVER (PARTITION BY DIAGNOSIS), 2) AS diagnosis_avg_amount,
    ROUND(AMOUNT - AVG(AMOUNT) OVER (PARTITION BY DIAGNOSIS), 2) AS diff_from_avg
FROM hospital_admissions
ORDER BY diff_from_avg DESC
LIMIT 15;


-- 5. Gender breakdown of cost outliers
SELECT
    GENDER,
    COUNT(*) AS total_cases,
    SUM(CASE WHEN COST_OUTLIER_FLAG = 'ABOVE_THRESHOLD' THEN 1 ELSE 0 END) AS outlier_cases,
    ROUND(100.0 * SUM(CASE WHEN COST_OUTLIER_FLAG = 'ABOVE_THRESHOLD' THEN 1 ELSE 0 END) / COUNT(*), 1) AS outlier_pct
FROM hospital_admissions
GROUP BY GENDER;


-- 6. Length of stay distribution check
SELECT
    LENGTH_OF_STAY_DAYS,
    COUNT(*) AS num_records
FROM hospital_admissions
GROUP BY LENGTH_OF_STAY_DAYS
ORDER BY num_records DESC
LIMIT 10;