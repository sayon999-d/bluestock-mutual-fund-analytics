-- Query 1: Top 5 mutual funds by total transaction volume
SELECT
    f.amfi_code,
    f.scheme_name,
    SUM(t.amount_inr) AS total_transaction_volume
FROM fact_transactions t
JOIN dim_fund f ON f.amfi_code = t.amfi_code
GROUP BY f.amfi_code, f.scheme_name
ORDER BY total_transaction_volume DESC
LIMIT 5;

-- Query 2: Rolling 3-month average NAV per month for a fund scheme
WITH monthly_nav AS (
    SELECT
        amfi_code,
        strftime('%Y-%m-01', nav_date) AS nav_month,
        AVG(nav) AS avg_nav
    FROM fact_nav
    WHERE amfi_code = :amfi_code
    GROUP BY amfi_code, nav_month
)
SELECT
    amfi_code,
    nav_month,
    avg_nav,
    AVG(avg_nav) OVER (
        PARTITION BY amfi_code
        ORDER BY nav_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3m_avg_nav
FROM monthly_nav
ORDER BY nav_month;

-- Query 3: Total investment amount and transaction count by state
SELECT
    state,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- Query 4: Aggregate volume split by city tier
SELECT
    city_tier,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
WHERE city_tier IN ('T30', 'B30')
GROUP BY city_tier
ORDER BY total_amount_inr DESC;

-- Query 5: Funds with an expense ratio under 1%
SELECT
    amfi_code,
    scheme_name,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Query 6: Average ticket size by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    AVG(amount_inr) AS avg_ticket_size,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;

-- Query 7: Monthly transaction totals by city tier
SELECT
    city_tier,
    strftime('%Y-%m-01', transaction_date) AS tx_month,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY city_tier, tx_month
ORDER BY tx_month, city_tier;

-- Query 8: Top 3 funds per state by transaction volume
WITH ranked_funds AS (
    SELECT
        t.state,
        f.scheme_name,
        SUM(t.amount_inr) AS total_amount_inr,
        DENSE_RANK() OVER (
            PARTITION BY t.state
            ORDER BY SUM(t.amount_inr) DESC
        ) AS fund_rank
    FROM fact_transactions t
    JOIN dim_fund f ON f.amfi_code = t.amfi_code
    GROUP BY t.state, f.scheme_name
)
SELECT
    state,
    scheme_name,
    total_amount_inr
FROM ranked_funds
WHERE fund_rank <= 3
ORDER BY state, fund_rank;

-- Query 9: SIP vs Lumpsum mix by fund category
SELECT
    f.category,
    t.transaction_type,
    COUNT(*) AS transaction_count,
    SUM(t.amount_inr) AS total_amount_inr
FROM fact_transactions t
JOIN dim_fund f ON f.amfi_code = t.amfi_code
WHERE t.transaction_type IN ('SIP', 'Lumpsum')
GROUP BY f.category, t.transaction_type
ORDER BY f.category, total_amount_inr DESC;

-- Query 10: Investor cohorts by first transaction month
WITH first_tx AS (
    SELECT
        investor_id,
        strftime('%Y-%m-01', MIN(transaction_date)) AS cohort_month
    FROM fact_transactions
    GROUP BY investor_id
),
cohort_tx AS (
    SELECT
        f.cohort_month,
        strftime('%Y-%m-01', t.transaction_date) AS tx_month,
        SUM(t.amount_inr) AS total_amount_inr,
        COUNT(DISTINCT t.investor_id) AS active_investors
    FROM fact_transactions t
    JOIN first_tx f ON f.investor_id = t.investor_id
    GROUP BY f.cohort_month, tx_month
)
SELECT
    cohort_month,
    tx_month,
    total_amount_inr,
    active_investors
FROM cohort_tx
ORDER BY cohort_month, tx_month;