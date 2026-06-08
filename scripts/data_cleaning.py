from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"


def clean_nav_history() -> pd.DataFrame:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nav_path = DATASETS_DIR / "02_nav_history.csv"
    nav_df = pd.read_csv(nav_path)

    nav_df["date"] = pd.to_datetime(nav_df["date"], errors="coerce")
    nav_df = nav_df.dropna(subset=["date", "amfi_code", "nav"])
    nav_df = nav_df.drop_duplicates()
    nav_df = nav_df[nav_df["nav"] > 0]

    nav_df = nav_df.sort_values(["amfi_code", "date"])

    def _reindex_and_fill(group: pd.DataFrame) -> pd.DataFrame:
        current_amfi_code = group.name
        group = group.sort_values("date")
        date_index = pd.date_range(start=group["date"].min(), end=group["date"].max(), freq="D")
        group = group.set_index("date").reindex(date_index).ffill()
        group["amfi_code"] = current_amfi_code
        group = group.reset_index().rename(columns={"index": "date"})
        return group

    nav_df = (
        nav_df.groupby("amfi_code", group_keys=False)
        .apply(_reindex_and_fill)
        .reset_index(drop=True)
    )

    nav_df = nav_df[nav_df["nav"] > 0]
    nav_df = nav_df.sort_values(["amfi_code", "date"])

    output_path = OUTPUT_DIR / "clean_02_nav_history.csv"
    nav_df.to_csv(output_path, index=False)
    print(f"Saved cleaned NAV history to {output_path}")
    return nav_df


def clean_investor_transactions() -> pd.DataFrame:
    tx_path = DATASETS_DIR / "08_investor_transactions.csv"
    tx_df = pd.read_csv(tx_path)

    object_cols = tx_df.select_dtypes(include=["object"]).columns
    tx_df[object_cols] = tx_df[object_cols].apply(lambda col: col.astype(str).str.strip())

    tx_df["transaction_date"] = pd.to_datetime(tx_df["transaction_date"], errors="coerce")
    tx_df["transaction_type"] = tx_df["transaction_type"].str.upper()

    type_map = {
        "SIP": "SIP",
        "LUMPSUM": "Lumpsum",
        "REDEMPTION": "Redemption",
    }
    tx_df["transaction_type"] = tx_df["transaction_type"].map(type_map)

    tx_df = tx_df.dropna(subset=["transaction_date", "transaction_type", "amount_inr"])
    tx_df = tx_df[tx_df["amount_inr"] > 0]
    tx_df = tx_df[tx_df["kyc_status"].isin(["Verified", "Pending"])]

    output_path = OUTPUT_DIR / "clean_08_investor_transactions.csv"
    tx_df.to_csv(output_path, index=False)
    return tx_df


def clean_scheme_performance() -> pd.DataFrame:
    perf_path = DATASETS_DIR / "07_scheme_performance.csv"
    perf_df = pd.read_csv(perf_path)

    return_cols = [
        col
        for col in perf_df.columns
        if col.startswith("return_") or col.startswith("benchmark_")
    ]

    for col in return_cols + ["sharpe_ratio", "expense_ratio_pct"]:
        if col in perf_df.columns:
            perf_df[col] = pd.to_numeric(perf_df[col], errors="coerce")

    if "sharpe_ratio" in perf_df.columns:
        perf_df["sharpe_ratio_anomaly"] = perf_df["sharpe_ratio"] < 0

    perf_df = perf_df.dropna(subset=["expense_ratio_pct"])
    perf_df = perf_df[perf_df["expense_ratio_pct"].between(0.1, 2.5, inclusive="both")]

    output_path = OUTPUT_DIR / "clean_07_scheme_performance.csv"
    perf_df.to_csv(output_path, index=False)
    return perf_df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()


if __name__ == "__main__":
    main()
