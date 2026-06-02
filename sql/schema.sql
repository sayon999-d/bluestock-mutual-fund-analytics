PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    risk_category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    nav_date TEXT NOT NULL,
    nav REAL NOT NULL CHECK (nav > 0),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    amount_inr INTEGER NOT NULL CHECK (amount_inr > 0),
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    state TEXT NOT NULL,
    city_tier TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi_date
ON fact_nav (amfi_code, nav_date);

CREATE INDEX IF NOT EXISTS idx_fact_transactions_amfi_date
ON fact_transactions (amfi_code, transaction_date);
