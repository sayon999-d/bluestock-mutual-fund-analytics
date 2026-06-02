from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def print_diagnostics(name: str, df: pd.DataFrame) -> None:
    print(f"\n{name}")
    print(f"Shape: {df.shape}")
    print("Dtypes:")
    print(df.dtypes)
    print("Head:")
    print(df.head())


def quality_check_amfi_codes(fund_df: pd.DataFrame, nav_df: pd.DataFrame) -> None:
    fund_codes = fund_df["amfi_code"].dropna().astype(int).unique()
    nav_codes = nav_df["amfi_code"].dropna().astype(int).unique()

    missing_codes = sorted(set(fund_codes) - set(nav_codes))
    if missing_codes:
        raise ValueError(
            f"Missing {len(missing_codes)} AMFI codes in nav_history: {missing_codes[:10]}"
        )

    if not nav_df["amfi_code"].is_monotonic_increasing:
        print("Warning: nav_history amfi_code column is not monotonic increasing.")
    else:
        print("nav_history amfi_code column is monotonic increasing.")

    print("AMFI code presence check passed.")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    dataframes: dict[str, pd.DataFrame] = {}
    for filename in DATASETS:
        path = RAW_DIR / filename
        df = pd.read_csv(path)
        dataframes[filename] = df
        print_diagnostics(filename, df)

    fund_df = dataframes["01_fund_master.csv"]
    nav_df = dataframes["02_nav_history.csv"]
    quality_check_amfi_codes(fund_df, nav_df)


if __name__ == "__main__":
    main()
