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

## fact_aum
| Column | Type | Constraints | Definition |
| --- | --- | --- | --- |
| aum_id | INTEGER | Primary Key, Auto-increment | Surrogate key for AMC AUM records. |
| fund_house | TEXT | NOT NULL | Asset management company name (matches dim_fund). |
| date | TEXT | NOT NULL | Quarterly reporting date (ISO-8601 format). |
| aum_crore | INTEGER | NOT NULL, aum_crore >= 0 | Assets Under Management represented in Indian Crores. |
| num_schemes | INTEGER | NOT NULL | Total active fund schemes managed by the AMC. |

## fact_scheme_performance
| Column | Type | Constraints | Definition |
| --- | --- | --- | --- |
| performance_id | INTEGER | Primary Key, Auto-increment | Surrogate key for performance rows. |
| amfi_code | INTEGER | Foreign Key to dim_fund | Unique AMFI code identifying the scheme. |
| return_1yr_pct | REAL | NOT NULL | 1-year absolute percentage return historical metric. |
| return_3yr_pct | REAL | NOT NULL | 3-year Compounded Annual Growth Rate (CAGR) %. |
| return_5yr_pct | REAL | NOT NULL | 5-year Compounded Annual Growth Rate (CAGR) %. |
| sharpe_ratio | REAL | NOT NULL | Risk-adjusted metric evaluating excess return per unit risk. |
| sortino_ratio | REAL | NOT NULL | Performance evaluation focused purely on downside deviation risk. |
| alpha | REAL | NOT NULL | Jensen's Alpha mapping outperformance vs market index benchmarks. |
| beta | REAL | NOT NULL | Market systematic volatility sensitivity coefficient. |
| max_drawdown_pct | REAL | NOT NULL | Worst peak-to-trough value decline percentage. |
| morningstar_rating | INTEGER | CHECK(morningstar_rating BETWEEN 1 AND 5) | 1-to-5 star quantitative evaluation score. |

## fact_portfolio_holdings
| Column | Type | Constraints | Definition |
| --- | --- | --- | --- |
| holding_id | INTEGER | Primary Key, Auto-increment | Surrogate key for granular holding entries. |
| amfi_code | INTEGER | Foreign Key to dim_fund | Unique AMFI code linking to the parent fund scheme. |
| stock_symbol | TEXT | NOT NULL | Official exchange equity identifier ticket (NSE/BSE ticker). |
| stock_name | TEXT | NOT NULL | Legal corporate name of the underlying equity asset. |
| sector | TEXT | NOT NULL | Industry classification sector grouping. |
| weight_pct | REAL | NOT NULL | Portfolio asset allocation exposure weight percentage. |
| market_value_cr | REAL | NOT NULL | Current net market capitalization value in Indian Crores. |
| portfolio_date | TEXT | NOT NULL | Snapshot reporting timestamp (ISO-8601). |

## Extended Relationships
| From | To | Relationship |
| --- | --- | --- |
| fact_scheme_performance.amfi_code | dim_fund.amfi_code | One-to-one (Fund profile metric mapping). |
| fact_portfolio_holdings.amfi_code | dim_fund.amfi_code | Many-to-one (Granular equity holdings to fund dimension). |
