from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"


def load_schema(engine) -> None:
    schema_path = SQL_DIR / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys = ON")
        conn.connection.executescript(schema_sql)


def load_dim_fund(engine) -> pd.DataFrame:
    fund_path = DATASETS_DIR / "01_fund_master.csv"
    fund_df = pd.read_csv(fund_path)

    dim_cols = [
        "amfi_code",
        "fund_house",
        "scheme_name",
        "category",
        "sub_category",
        "expense_ratio_pct",
        "risk_category",
    ]
    dim_df = fund_df[dim_cols].drop_duplicates(subset=["amfi_code"])

    dim_df.to_sql("dim_fund", engine, if_exists="append", index=False)
    return dim_df


def load_fact_nav(engine, dim_codes: set[int]) -> None:
    nav_path = PROCESSED_DIR / "clean_02_nav_history.csv"
    nav_df = pd.read_csv(nav_path)

    nav_df = nav_df.rename(columns={"date": "nav_date"})
    nav_df = nav_df[nav_df["amfi_code"].isin(dim_codes)]
    nav_df["nav_date"] = nav_df["nav_date"].astype(str)
    nav_df = nav_df[["amfi_code", "nav_date", "nav"]]

    nav_df.to_sql("fact_nav", engine, if_exists="append", index=False)


def load_fact_transactions(engine, dim_codes: set[int]) -> None:
    tx_path = PROCESSED_DIR / "clean_08_investor_transactions.csv"
    tx_df = pd.read_csv(tx_path)

    tx_df = tx_df[tx_df["amfi_code"].isin(dim_codes)]
    tx_df["transaction_date"] = tx_df["transaction_date"].astype(str)
    tx_df["amount_inr"] = tx_df["amount_inr"].round(0).astype(int)
    tx_df = tx_df[
        [
            "investor_id",
            "amfi_code",
            "transaction_date",
            "amount_inr",
            "transaction_type",
            "state",
            "city_tier",
        ]
    ]

    tx_df.to_sql("fact_transactions", engine, if_exists="append", index=False)


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    load_schema(engine)

    dim_df = load_dim_fund(engine)
    dim_codes = set(dim_df["amfi_code"].tolist())

    load_fact_nav(engine, dim_codes)
    load_fact_transactions(engine, dim_codes)


if __name__ == "__main__":
    main()
