# Bluestock Mutual Fund Analytics

Bluestock Mutual Fund Analytics is an end-to-end Indian fintech capstone built to ingest mutual fund source data, normalize it into a continuity-safe SQLite star schema, compute institutional-grade performance and risk metrics, and serve the results through a Streamlit executive dashboard.

This repository is organized for macOS + VS Code development and is designed to run entirely on a local machine with relative file paths and reproducible pipelines.

---

## Project Overview

The platform covers the full analytics lifecycle:

1. Raw ingestion from AMFI-aligned CSV assets and supplemental market files.
2. ETL sanitization with holiday/weekend NAV gap filling and transaction cleaning.
3. SQLite migration into a compact star schema.
4. Quantitative analytics for return, risk, tail-risk, cohort, continuity, and concentration analysis.
5. Streamlit-based dashboard delivery for executive use.

The main deliverables are:

- `run_pipeline.py` for one-click orchestration.
- `dashboard/app.py` for the interactive analytics workspace.
- `notebooks/03_eda_analysis.ipynb` and `notebooks/06_advanced_analytics.ipynb` for analytical narration.
- `reports/` for final PDF and PNG deliverables.

---

## Architecture Workflow

<div align="center">
  <svg width="1100" height="430" viewBox="0 0 1100 430" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bluestock mutual fund analytics architecture workflow">
    <defs>
      <linearGradient id="navyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0B1F3A"/>
        <stop offset="100%" stop-color="#14345C"/>
      </linearGradient>
      <linearGradient id="tealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1F8A8A"/>
        <stop offset="100%" stop-color="#2FA6A6"/>
      </linearGradient>
      <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#0B1F3A" flood-opacity="0.14"/>
      </filter>
      <style>
        .box-title { font: 700 18px 'Segoe UI', Arial, sans-serif; fill: #0B1F3A; }
        .box-text { font: 600 13px 'Segoe UI', Arial, sans-serif; fill: #405266; }
        .box-small { font: 500 12px 'Segoe UI', Arial, sans-serif; fill: #5B6B7A; }
        .arrow { stroke: #1F8A8A; stroke-width: 4; fill: none; marker-end: url(#arrowHead); }
        .section { fill: #FFFFFF; stroke: #DCE3EA; stroke-width: 1.5; rx: 18; ry: 18; filter: url(#shadow); }
        .section-dark { fill: url(#navyGrad); stroke: #0B1F3A; stroke-width: 1.5; rx: 18; ry: 18; filter: url(#shadow); }
        .section-teal { fill: url(#tealGrad); stroke: #1F8A8A; stroke-width: 1.5; rx: 18; ry: 18; filter: url(#shadow); }
        .white-title { font: 700 18px 'Segoe UI', Arial, sans-serif; fill: #FFFFFF; }
        .white-text { font: 600 13px 'Segoe UI', Arial, sans-serif; fill: #EAF4F7; }
      </style>
      <marker id="arrowHead" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto">
        <path d="M0,0 L12,6 L0,12 z" fill="#1F8A8A"/>
      </marker>
    </defs>

    <rect x="20" y="28" width="1060" height="372" rx="26" fill="#F7FAFC" stroke="#DCE3EA"/>
    <text x="550" y="62" text-anchor="middle" class="box-title" style="font-size:22px;">Bluestock Mutual Fund Analytics Architecture Workflow</text>

    <rect x="55" y="110" width="195" height="120" class="section-dark"/>
    <text x="152" y="144" text-anchor="middle" class="white-title">Raw CSV Inputs</text>
    <text x="152" y="171" text-anchor="middle" class="white-text">AMFI master, NAV, SIP,</text>
    <text x="152" y="191" text-anchor="middle" class="white-text">holdings, benchmarks</text>

    <rect x="290" y="110" width="225" height="120" class="section"/>
    <text x="402" y="144" text-anchor="middle" class="box-title">Pandas Validation</text>
    <text x="402" y="171" text-anchor="middle" class="box-text">Schema checks, type coercion,</text>
    <text x="402" y="191" text-anchor="middle" class="box-text">duplicate filtering, gap logic</text>

    <rect x="555" y="92" width="280" height="155" class="section-teal"/>
    <text x="695" y="128" text-anchor="middle" class="white-title">SQLite Relational Star Schema</text>
    <text x="695" y="157" text-anchor="middle" class="white-text">dim_fund</text>
    <text x="695" y="178" text-anchor="middle" class="white-text">fact_nav</text>
    <text x="695" y="199" text-anchor="middle" class="white-text">fact_transactions</text>
    <text x="695" y="220" text-anchor="middle" class="white-text">fact_performance</text>

    <rect x="875" y="110" width="170" height="120" class="section-dark"/>
    <text x="960" y="144" text-anchor="middle" class="white-title">Streamlit UI</text>
    <text x="960" y="171" text-anchor="middle" class="white-text">Interactive pages,</text>
    <text x="960" y="191" text-anchor="middle" class="white-text">filters, dashboards</text>

    <path d="M250 170 L290 170" class="arrow"/>
    <path d="M515 170 L555 170" class="arrow"/>
    <path d="M835 170 L875 170" class="arrow"/>

    <rect x="290" y="265" width="225" height="82" rx="16" fill="#FFFFFF" stroke="#DCE3EA"/>
    <text x="402" y="297" text-anchor="middle" class="box-title" style="font-size:16px;">Analytics Outputs</text>
    <text x="402" y="320" text-anchor="middle" class="box-small">scorecard, VaR/CVaR, cohort, HHI</text>

    <rect x="555" y="265" width="280" height="82" rx="16" fill="#FFFFFF" stroke="#DCE3EA"/>
    <text x="695" y="297" text-anchor="middle" class="box-title" style="font-size:16px;">Data Lineage and Reproducibility</text>
    <text x="695" y="320" text-anchor="middle" class="box-small">relative paths, ETL scripts, deterministic refresh</text>

    <path d="M402 230 L402 265" class="arrow"/>
    <path d="M695 247 L695 265" class="arrow"/>
  </svg>
</div>

---

## Local Environment Setup

### 1. Create a virtual environment

```bash
python3 -m venv venv
```

### 2. Activate it on macOS

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional notebook support

If Jupyter is not already available in VS Code, install the Jupyter extension and reopen the project folder so the notebooks render correctly.

---

## Execution Guide

### Run the full pipeline

```bash
python run_pipeline.py
```

This executes:

1. `scripts/data_cleaning.py`
2. `scripts/db_migration.py`
3. `scripts/recommender.py`

If a step fails, the pipeline stops immediately and logs the failure.

### Launch the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

---

## Repository Structure

```text
project 2/
├── .gitignore
├── README.md
├── requirements.txt
├── run_pipeline.py
├── scripts/
├── notebooks/
├── dashboard/
└── reports/
```

---

## Dataset & Deliverables Index

### A. Core relational and analytics layers

The production pipeline uses 3 SQLite tables and 5 curated analytics layers, giving the project 8 indexed data artifacts in total.

| Layer | File / Table | Type | Purpose |
|---|---|---:|---|
| 1 | `dim_fund` | SQLite table | Master fund dimension with scheme, category, expense ratio, and risk bucket. |
| 2 | `fact_nav` | SQLite table | Daily NAV fact table with continuity-safe filled history. |
| 3 | `fact_transactions` | SQLite table | Investor transaction fact table with SIP, Lumpsum, and Redemption records. |
| 4 | `fund_scorecard.csv` | Processed dataset | Composite scoring output for performance ranking. |
| 5 | `alpha_beta.csv` | Processed dataset | Regression risk table with alpha, beta, and R-squared. |
| 6 | `var_cvar_report.csv` | Processed dataset | Tail-risk summary for VaR and CVaR reporting. |
| 7 | `cohort_analysis.csv` | Processed dataset | Lifetime investor cohort behavior summary. |
| 8 | `sip_continuity_report.csv` | Processed dataset | SIP cadence retention and latency-risk reporting. |

### B. Additional analytics artifact

| File | Type | Purpose |
|---|---|---|
| `hhi_report.csv` | Processed dataset | Sector concentration analysis for equity holdings. |

### C. Key raw inputs

| File | Purpose |
|---|---|
| `data/raw/01_fund_master.csv` | Fund master source for dimension loading. |
| `data/raw/02_nav_history.csv` | Raw historical NAV series. |
| `data/raw/03_aum_by_fund_house.csv` | AMC-scale AUM analytics. |
| `data/raw/04_monthly_sip_inflows.csv` | SIP inflow trend analysis. |
| `data/raw/05_category_inflows.csv` | Category inflow heatmap analysis. |
| `data/raw/06_industry_folio_count.csv` | Folio growth trend analysis. |
| `data/raw/07_scheme_performance.csv` | Performance and risk feature source. |
| `data/raw/08_investor_transactions.csv` | Investor transaction source. |
| `data/raw/09_portfolio_holdings.csv` | Equity holdings and sector concentration source. |
| `data/raw/10_benchmark_indices.csv` | Market benchmark comparison source. |

### D. Final submission PDFs and presentation assets

| Deliverable | Location |
|---|---|
| Consolidated dashboard PDF | `reports/Dashboard.pdf` |
| Page 1 PDF export | `reports/01_industry_overview.pdf` |
| Page 2 PDF export | `reports/02_fund_performance.pdf` |
| Page 3 PDF export | `reports/03_investor_analytics.pdf` |
| Page 4 PDF export | `reports/04_sip_trends.pdf` |
| Main final report | `reports/Final_Report.pdf` |
| Presentation deck | `reports/Bluestock_MF_Presentation.pptx` |
| Rolling Sharpe chart | `reports/rolling_sharpe_chart.png` |

---

## Final Report Blueprint

Target length: 15 to 20 pages

### 1. Executive Summary

Use this opening paragraph template:

> Bluestock Mutual Fund Analytics was built to transform raw mutual fund and investor transaction feeds into a continuity-safe analytical platform that supports performance benchmarking, tail-risk monitoring, investor behavioral analysis, and portfolio concentration assessment. The final outputs combine SQLite-backed data integrity, reproducible ETL, and an interactive Streamlit delivery layer to support executive decision-making.

Include:

- Objective and scope.
- What data was used.
- What analytic capabilities were delivered.
- Why the solution matters for Indian mutual fund platforms.

### 2. Data Ingestion Strategy

Include:

- Source inventory.
- AMFI-aligned master data approach.
- Why raw CSVs were retained as immutable inputs.
- Backup API fetch strategy for live NAV validation.

Copy-ready paragraph:

> The ingestion layer standardizes raw CSV files into structured assets while preserving source lineage. The fund master, NAV history, transaction records, holdings data, and benchmark series are separately validated before being passed into the cleaning and migration stages.

### 3. ETL Pipeline Architecture

Include:

- Data cleaning rules.
- NAV gap-fill policy.
- Transaction sanitization.
- SQLite star schema design.
- Relational joins and constraints.

Copy-ready paragraph:

> The ETL pipeline applies continuity-safe NAV reindexing to preserve daily price series across weekends and holidays, while transaction cleansing enforces positive amounts and categorical normalization. Cleaned outputs are then migrated into a compact SQLite star schema consisting of one dimension table and two fact tables.

### 4. Advanced Risk Analysis

Subsections:

- VaR 95%
- CVaR 95%
- Rolling 90-day Sharpe
- Cohort retention
- SIP continuity
- HHI concentration

Copy-ready paragraph:

> Tail-risk metrics identify the depth of adverse daily outcomes using historical return distributions, while rolling Sharpe trajectories expose whether recent performance is sustainable or weakening. Sector concentration and SIP cadence analyses add a behavioral and structural lens to the platform’s investment diagnostics.

### 5. Streamlit Interface Walkthrough

Subsections:

- Page 1: Industry overview.
- Page 2: Performance dynamics.
- Page 3: Investor and demographic analytics.
- Page 4: SIP and macro market trends.

Copy-ready paragraph:

> The Streamlit interface provides an executive-grade, four-page experience that layers KPI cards, interactivity filters, risk-return scatter plots, transaction analytics, and macro overlays into a single navigable workspace.

### 6. System Limitations

Include:

- Static source refresh dependency.
- SQLite as a single-user local store.
- NAV fill approximation across non-trading dates.
- Holdings data represents periodic disclosure snapshots.

Copy-ready paragraph:

> The current build is optimized for local analytical delivery rather than concurrent enterprise workloads. While continuity-safe interpolation makes the NAV series usable for daily analytics, it should still be interpreted as a cleaned market proxy rather than a live exchange-grade feed.

### 7. Strategic Investment Recommendations

Include:

- Favor top-ranked funds by composite score.
- Monitor funds with high VaR and elevated drawdown.
- Review at-risk SIP cohorts for retention intervention.
- Watch heavily concentrated equity schemes for sector shock exposure.

Copy-ready paragraph:

> The analysis suggests prioritizing high-composite-score funds with superior Sharpe, controlled drawdown, and acceptable expense ratios while maintaining active surveillance on concentrated equity portfolios and at-risk SIP investors.

---

## Code Cleaning and Refactoring Checklist

Use this checklist to sanitize all existing scripts:

1. Add Google-style docstrings to every public function and class.
2. Replace `print()` calls with `logging.info()`, `logging.warning()`, or `logging.error()` where operational visibility matters.
3. Keep `print()` only for notebook cells or intentional user-facing tabular output.
4. Standardize all paths with `pathlib.Path`; avoid hard-coded absolute paths.
5. Validate file existence before reading and raise clear `FileNotFoundError` messages.
6. Parse dates with `pd.to_datetime(..., errors="coerce")` before using time-series operations.
7. Enforce positive-value checks for NAV and transaction amount columns.
8. Reindex NAV history over `pd.date_range(..., freq="D")` and forward-fill missing observations.
9. Guard all SQLite writes with foreign-key-safe schema loading and consistent table names.
10. Use `.to_sql(..., if_exists="append")` only after the schema is in place.
11. Validate all dashboard inputs before filtering to avoid empty-frame crashes.
12. Keep plotting functions isolated so chart styling can be reused across notebooks and the Streamlit app.

---

## Quick Start Commands

```bash
source venv/bin/activate
python run_pipeline.py
streamlit run dashboard/app.py
```

---

## Notes for macOS + VS Code

- Open this repository folder directly in VS Code.
- Select the project Python interpreter from the virtual environment.
- Run notebooks using the VS Code Jupyter extension.
- Use `Cmd + Shift + P` to switch interpreters if needed.
- For PDF exports from the dashboard, use the browser print dialog and save pages into `reports/`.
