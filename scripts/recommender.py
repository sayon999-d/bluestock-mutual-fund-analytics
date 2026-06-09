from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


VALID_RISK_APPETITES = {"Low", "Moderate", "High"}
RISK_GRADE_MAP: dict[str, tuple[str, ...]] = {
    "Low": ("Low",),
    "Moderate": ("Moderate", "Moderately High"),
    "High": ("High", "Very High"),
}


def _load_sqlite_table(table_name: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found at {DB_PATH}. Run the ETL migration first."
        )
    conn = sqlite3.connect(DB_PATH.as_posix())
    try:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()


def _load_performance_frame() -> pd.DataFrame:
    candidates: Iterable[Path] = (
        PROCESSED_DIR / "clean_07_scheme_performance.csv",
        PROCESSED_DIR / "fund_scorecard.csv",
    )
    for candidate in candidates:
        if candidate.exists():
            df = pd.read_csv(candidate)
            if "risk_grade" not in df.columns and "risk_category" in df.columns:
                df["risk_grade"] = df["risk_category"]
            return df
    raise FileNotFoundError(
        "No processed performance file found. Expected 'clean_07_scheme_performance.csv' "
        "or 'fund_scorecard.csv' inside data/processed/."
    )


def _normalize_perf_frame(df: pd.DataFrame) -> pd.DataFrame:
    numeric_candidates = [
        "sharpe_ratio",
        "sortino_ratio",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "cagr_1yr",
        "cagr_3yr",
        "cagr_5yr",
        "aum_crore",
        "expense_ratio_pct",
    ]
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def recommend_funds(risk_appetite: str) -> pd.DataFrame:
    if risk_appetite not in VALID_RISK_APPETITES:
        raise ValueError(
            "risk_appetite must be exactly one of: 'Low', 'Moderate', or 'High'."
        )

    dim_fund = _load_sqlite_table("dim_fund")
    perf = _normalize_perf_frame(_load_performance_frame())

    merged = dim_fund.merge(perf, on="amfi_code", how="inner", suffixes=("_dim", "_perf"))
    for column in ["scheme_name", "fund_house", "category", "expense_ratio_pct"]:
        perf_column = f"{column}_perf"
        dim_column = f"{column}_dim"
        if perf_column in merged.columns:
            merged[column] = merged[perf_column]
        elif dim_column in merged.columns:
            merged[column] = merged[dim_column]

    merged = merged[merged["risk_grade"].isin(RISK_GRADE_MAP[risk_appetite])].copy()

    if merged.empty:
        return merged.head(0)

    sort_columns = [col for col in ["sharpe_ratio", "return_3yr_pct", "cagr_3yr"] if col in merged.columns]
    merged = merged.sort_values(sort_columns, ascending=[False] * len(sort_columns))
    merged = merged.head(3).reset_index(drop=True)
    merged.insert(0, "recommendation_rank", merged.index + 1)

    keep_columns = [
        "recommendation_rank",
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "risk_grade",
        "sharpe_ratio",
        "sortino_ratio",
        "return_3yr_pct" if "return_3yr_pct" in merged.columns else "cagr_3yr",
        "expense_ratio_pct",
        "aum_crore",
    ]
    keep_columns = [col for col in keep_columns if col in merged.columns]
    return merged[keep_columns].copy()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Bluestock mutual fund recommendations by risk appetite."
    )
    parser.add_argument(
        "risk_appetite",
        choices=sorted(VALID_RISK_APPETITES),
        help="Risk appetite bucket: Low, Moderate, or High",
    )
    args = parser.parse_args()

    recommendations = recommend_funds(args.risk_appetite)
    if recommendations.empty:
        print(f"No matching schemes found for risk appetite '{args.risk_appetite}'.")
    else:
        print(recommendations.to_string(index=False))


if __name__ == "__main__":
    main()
