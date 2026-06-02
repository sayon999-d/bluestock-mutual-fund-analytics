from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

SCHEMES = {
    "HDFC Top 100 Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841,
}

API_URL = "https://api.mfapi.in/mf/{scheme_code}"


def fetch_nav_history(scheme_name: str, scheme_code: int) -> pd.DataFrame:
    response = requests.get(API_URL.format(scheme_code=scheme_code), timeout=30)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    nav_records = payload.get("data", [])
    if not nav_records:
        raise ValueError(f"No NAV records returned for {scheme_name} ({scheme_code}).")

    df = pd.DataFrame(nav_records)
    df = df.rename(columns={"date": "nav_date"})
    df["scheme_code"] = scheme_code
    df["scheme_name"] = scheme_name

    return df[["scheme_code", "scheme_name", "nav_date", "nav"]]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for scheme_name, scheme_code in SCHEMES.items():
        df = fetch_nav_history(scheme_name, scheme_code)
        output_path = RAW_DIR / f"live_nav_{scheme_code}.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved {scheme_name} NAV data to {output_path}")


if __name__ == "__main__":
    main()
