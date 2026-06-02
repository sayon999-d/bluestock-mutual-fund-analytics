# Mutual Fund Analytics Data Dictionary

## dim_fund
| Column | Type | Constraints | Definition |
| --- | --- | --- | --- |
| amfi_code | INTEGER | Primary Key | Unique AMFI code for each mutual fund scheme. |
| fund_house | TEXT | NOT NULL | Asset management company name. |
| scheme_name | TEXT | NOT NULL | Official scheme name. |
| category | TEXT | NOT NULL | High level category (e.g., Equity, Debt). |
| sub_category | TEXT | NOT NULL | Category segmentation (e.g., Large Cap). |
| expense_ratio_pct | REAL | NOT NULL | Annual expense ratio in percent. |
| risk_category | TEXT | NOT NULL | Risk classification assigned by the fund house. |

## fact_nav
| Column | Type | Constraints | Definition |
| --- | --- | --- | --- |
| nav_id | INTEGER | Primary Key, Auto-increment | Surrogate key for NAV records. |
| amfi_code | INTEGER | Foreign Key to dim_fund | AMFI code for the scheme. |
| nav_date | TEXT | NOT NULL | Date of the NAV record (ISO-8601). |
| nav | REAL | NOT NULL, nav > 0 | Net asset value for the scheme on nav_date. |

## fact_transactions
| Column | Type | Constraints | Definition |
| --- | --- | --- | --- |
| tx_id | INTEGER | Primary Key, Auto-increment | Transaction identifier. |
| investor_id | TEXT | NOT NULL | Unique investor account identifier. |
| amfi_code | INTEGER | Foreign Key to dim_fund | AMFI code for the scheme. |
| transaction_date | TEXT | NOT NULL | Date of the investor transaction (ISO-8601). |
| amount_inr | INTEGER | NOT NULL, amount_inr > 0 | Transaction value in INR. |
| transaction_type | TEXT | NOT NULL, ENUM | SIP, Lumpsum, or Redemption. |
| state | TEXT | NOT NULL | State of the investor location. |
| city_tier | TEXT | NOT NULL | Geographic tier classification (T30 or B30). |

## Relationships
| From | To | Relationship |
| --- | --- | --- |
| fact_nav.amfi_code | dim_fund.amfi_code | Many-to-one (NAV records to fund dimension). |
| fact_transactions.amfi_code | dim_fund.amfi_code | Many-to-one (transactions to fund dimension). |
