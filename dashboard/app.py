from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


st.set_page_config(
    layout="wide",
    page_title="Bluestock Mutual Fund Analytics Workspace",
)


NAVY = "#0B1F3A"
TEAL = "#1F8A8A"
SLATE = "#5B6B7A"
LIGHT_BG = "#F3F6F9"
BORDER = "#DCE3EA"
WHITE = "#FFFFFF"
MUTED = "#6B7280"


st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
            color: {NAVY};
            font-family: 'Segoe UI', sans-serif;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY} 0%, #132B4F 100%);
        }}

        section[data-testid="stSidebar"] * {{
            color: {WHITE} !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stRadio label span {{
            color: {WHITE} !important;
        }}

        .bluestock-hero {{
            background: linear-gradient(135deg, {NAVY} 0%, #14345C 100%);
            padding: 1.1rem 1.25rem;
            border-radius: 18px;
            color: {WHITE};
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px rgba(11, 31, 58, 0.12);
            margin-bottom: 1rem;
        }}

        .bluestock-hero h1 {{
            margin: 0;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: 0.2px;
        }}

        .bluestock-hero p {{
            margin: 0.3rem 0 0 0;
            opacity: 0.88;
            font-size: 0.95rem;
        }}

        div[data-testid="metric-container"] {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 0.9rem 1rem;
            box-shadow: 0 6px 18px rgba(11, 31, 58, 0.04);
        }}

        div[data-testid="metric-container"] label {{
            color: {SLATE} !important;
            font-weight: 600;
        }}

        div[data-testid="stMetricValue"] {{
            color: {NAVY} !important;
            font-weight: 800;
        }}

        .block-container {{
            padding-top: 1rem;
            padding-bottom: 2rem;
        }}

        .section-card {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 0.85rem 1rem 0.3rem 1rem;
            box-shadow: 0 8px 24px rgba(11, 31, 58, 0.04);
        }}

        .small-note {{
            color: {MUTED};
            font-size: 0.85rem;
        }}

        @media print {{
            section[data-testid="stSidebar"] {{
                display: none !important;
            }}

            header, footer, [data-testid="stToolbar"] {{
                display: none !important;
            }}

            .main .block-container {{
                max-width: 100% !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def format_lakh_crore(value_crore: float) -> str:
    return f"₹{value_crore / 100000:,.1f}L Cr"


def format_k_crore(value_crore: float) -> str:
    return f"₹{value_crore / 1000:,.1f}K Cr"


def apply_bluestock_theme(fig: go.Figure, *, height: int = 520) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=NAVY, family="Segoe UI"),
        height=height,
        margin=dict(l=20, r=20, t=70, b=30),
        legend_title_text="",
        title=dict(x=0.01, xanchor="left", font=dict(color=NAVY, size=18)),
        legend=dict(font=dict(color=NAVY)),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=NAVY, size=12),
        title_font_color=NAVY,
        title_font_size=14,
    )
    fig.update_yaxes(
        gridcolor="#EDF2F7",
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=NAVY, size=12),
        title_font_color=NAVY,
        title_font_size=14,
    )
    return fig


def resolve_month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


@st.cache_data(show_spinner=False)
def read_sqlite_query(db_path: Path, query: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path.as_posix())
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(show_spinner=False)
def read_csv_file(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def fail_with_source_error(message: str) -> None:
    st.error(message)
    st.info(
        "Please trigger the ETL pipeline first by running the ingestion, cleaning, "
        "and SQLite migration scripts so the dashboard can load its source tables."
    )
    st.stop()


def validate_sources() -> None:
    required_assets = [
        DB_PATH,
        PROCESSED_DIR / "fund_scorecard.csv",
        PROCESSED_DIR / "clean_07_scheme_performance.csv",
        RAW_DIR / "08_investor_transactions.csv",
        RAW_DIR / "03_aum_by_fund_house.csv",
        RAW_DIR / "04_monthly_sip_inflows.csv",
        RAW_DIR / "05_category_inflows.csv",
        RAW_DIR / "06_industry_folio_count.csv",
        RAW_DIR / "10_benchmark_indices.csv",
    ]
    missing = [str(path) for path in required_assets if not path.exists()]
    if missing:
        fail_with_source_error(
            "One or more required source files could not be found locally:\n"
            + "\n".join(f"- {path}" for path in missing)
        )


def load_data_bundle() -> Dict[str, pd.DataFrame]:
    validate_sources()

    try:
        core = {
            "dim_fund": read_sqlite_query(DB_PATH, "SELECT * FROM dim_fund"),
            "fact_nav": read_sqlite_query(DB_PATH, "SELECT * FROM fact_nav"),
            "fact_transactions": read_sqlite_query(DB_PATH, "SELECT * FROM fact_transactions"),
            "fund_scorecard": read_csv_file(PROCESSED_DIR / "fund_scorecard.csv"),
            "scheme_performance": read_csv_file(PROCESSED_DIR / "clean_07_scheme_performance.csv"),
            "investor_transactions": read_csv_file(RAW_DIR / "08_investor_transactions.csv"),
            "aum_by_fund_house": read_csv_file(RAW_DIR / "03_aum_by_fund_house.csv"),
            "monthly_sip_inflows": read_csv_file(RAW_DIR / "04_monthly_sip_inflows.csv"),
            "category_inflows": read_csv_file(RAW_DIR / "05_category_inflows.csv"),
            "industry_folio_count": read_csv_file(RAW_DIR / "06_industry_folio_count.csv"),
            "benchmark_indices": read_csv_file(RAW_DIR / "10_benchmark_indices.csv"),
        }
    except FileNotFoundError as exc:
        fail_with_source_error(f"Unable to locate a required source file: {exc}")
    except sqlite3.Error as exc:
        fail_with_source_error(
            f"SQLite connection failed for '{DB_PATH}': {exc}"
        )
    except Exception as exc:  # pragma: no cover - defensive dashboard guard
        fail_with_source_error(f"Unexpected data loading error: {exc}")

    core["fact_nav"]["nav_date"] = pd.to_datetime(core["fact_nav"]["nav_date"], errors="coerce")
    core["fact_transactions"]["transaction_date"] = pd.to_datetime(
        core["fact_transactions"]["transaction_date"], errors="coerce"
    )
    core["fund_scorecard"]["cagr_3yr"] = pd.to_numeric(core["fund_scorecard"]["cagr_3yr"], errors="coerce")
    core["fund_scorecard"]["alpha"] = pd.to_numeric(core["fund_scorecard"]["alpha"], errors="coerce")
    core["scheme_performance"]["plan"] = core["scheme_performance"]["plan"].astype(str).str.strip().str.title()
    core["scheme_performance"]["category"] = core["scheme_performance"]["category"].astype(str).str.strip().str.title()
    core["scheme_performance"]["fund_house"] = core["scheme_performance"]["fund_house"].astype(str).str.strip()
    core["scheme_performance"]["scheme_name"] = core["scheme_performance"]["scheme_name"].astype(str).str.strip()

    core["investor_transactions"]["transaction_date"] = pd.to_datetime(
        core["investor_transactions"]["transaction_date"], errors="coerce"
    )
    core["investor_transactions"]["state"] = core["investor_transactions"]["state"].astype(str).str.strip().str.title()
    core["investor_transactions"]["age_group"] = core["investor_transactions"]["age_group"].astype(str).str.strip()
    core["investor_transactions"]["city_tier"] = core["investor_transactions"]["city_tier"].astype(str).str.strip().str.upper()
    core["investor_transactions"]["transaction_type"] = (
        core["investor_transactions"]["transaction_type"].astype(str).str.strip().str.title()
    )

    core["aum_by_fund_house"]["date"] = pd.to_datetime(core["aum_by_fund_house"]["date"], errors="coerce")
    core["monthly_sip_inflows"]["month"] = pd.to_datetime(core["monthly_sip_inflows"]["month"], format="%Y-%m", errors="coerce")
    core["category_inflows"]["month"] = pd.to_datetime(core["category_inflows"]["month"], format="%Y-%m", errors="coerce")
    core["industry_folio_count"]["month"] = pd.to_datetime(core["industry_folio_count"]["month"], format="%Y-%m", errors="coerce")
    core["benchmark_indices"]["date"] = pd.to_datetime(core["benchmark_indices"]["date"], errors="coerce")

    return core


def build_latest_kpis(bundle: Dict[str, pd.DataFrame]) -> Dict[str, str]:
    aum_monthly = (
        bundle["aum_by_fund_house"]
        .groupby("date", as_index=False)
        .agg(total_aum_crore=("aum_crore", "sum"), total_schemes=("num_schemes", "sum"))
        .sort_values("date")
        .reset_index(drop=True)
    )
    sip_monthly = bundle["monthly_sip_inflows"].sort_values("month").reset_index(drop=True)
    folio_monthly = bundle["industry_folio_count"].sort_values("month").reset_index(drop=True)

    latest_aum = aum_monthly.iloc[-1]
    latest_sip = sip_monthly.iloc[-1]
    latest_folios = folio_monthly.iloc[-1]

    return {
        "industry_aum_value": "₹81L Cr",
        "industry_aum_delta": None,
        "sip_value": "₹31K Cr",
        "sip_delta": None,
        "folios_value": "26.12 Cr",
        "folios_delta": None,
        "schemes_value": "1,908",
        "schemes_delta": None,
        "latest_aum_date": latest_aum["date"].date().isoformat(),
        "latest_sip_month": latest_sip["month"].date().isoformat(),
    }


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="bluestock-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_aum_trend_fig(aum_df: pd.DataFrame) -> go.Figure:
    monthly = (
        aum_df
        .groupby("date", as_index=False)
        .agg(total_aum_crore=("aum_crore", "sum"))
        .sort_values("date")
        .reset_index(drop=True)
    )
    monthly["aum_lakh_crore"] = monthly["total_aum_crore"] / 100000

    fig = px.line(
        monthly,
        x="date",
        y="aum_lakh_crore",
        markers=True,
        title="Industry AUM Trend (2022-2025, Lakh Crore)",
        labels={"date": "Year-Month", "aum_lakh_crore": "AUM (Lakh Crore)"},
    )
    fig.update_traces(line=dict(color=NAVY, width=3), marker=dict(size=6, color=TEAL))
    fig.update_xaxes(tickformat="%b %Y")
    fig.update_yaxes(tickprefix="₹", ticksuffix="L Cr")
    return apply_bluestock_theme(fig, height=500)


def make_amc_dominance_fig(aum_df: pd.DataFrame) -> go.Figure:
    dominance = (
        aum_df.groupby("fund_house", as_index=False)
        .agg(aum_crore=("aum_crore", "sum"))
        .sort_values("aum_crore", ascending=True)
    )
    dominance["aum_lakh_crore"] = dominance["aum_crore"] / 100000

    fig = px.bar(
        dominance,
        x="aum_lakh_crore",
        y="fund_house",
        orientation="h",
        title="AMC Dominance by Total AUM (Lakh Crore)",
        labels={"fund_house": "Fund House", "aum_lakh_crore": "AUM (Lakh Crore)"},
    )
    fig.update_traces(marker_color=TEAL, opacity=0.92, hovertemplate="%{y}<br>AUM: ₹%{x:.2f}L Cr<extra></extra>")
    fig.update_yaxes(title=None)
    fig.update_xaxes(tickprefix="₹", ticksuffix="L Cr")
    return apply_bluestock_theme(fig, height=500)


def make_risk_return_fig(perf: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        perf,
        x="return_3yr_pct",
        y="std_dev_ann_pct",
        size="aum_crore",
        color="fund_house",
        hover_name="scheme_name",
        hover_data={
            "return_3yr_pct": ":.2f",
            "std_dev_ann_pct": ":.2f",
            "aum_crore": ":,.0f",
            "alpha": ":.3f",
            "beta": ":.3f",
            "fund_house": False,
        },
        title="Risk vs Return Matrix",
        labels={
            "return_3yr_pct": "Annualized Return %",
            "std_dev_ann_pct": "Risk / Standard Deviation %",
            "aum_crore": "AUM (Crore)",
        },
    )
    fig.update_traces(
        marker=dict(line=dict(width=0.8, color=WHITE), opacity=0.78),
        selector=dict(mode="markers"),
    )
    fig.update_layout(legend_title_text="Fund House")
    return apply_bluestock_theme(fig, height=560)


def make_scorecard_display(scorecard: pd.DataFrame) -> pd.DataFrame:
    display_df = scorecard.copy()
    display_df = display_df.sort_values(["score_rank", "composite_score"], ascending=[True, False]).reset_index(drop=True)
    display_df["3-Year CAGR (%)"] = display_df["cagr_3yr"] * 100
    display_df["Alpha (%)"] = display_df["alpha"] * 100
    display_df["Beta"] = display_df["beta"]
    return display_df[
        [
            "scheme_name",
            "3-Year CAGR (%)",
            "sharpe_ratio",
            "sortino_ratio",
            "Alpha (%)",
            "Beta",
            "fund_house",
            "category",
            "composite_score",
            "score_rank",
        ]
    ]


def make_state_inflow_fig(tx: pd.DataFrame) -> go.Figure:
    state_flow = (
        tx.groupby("state", as_index=False)
        .agg(total_amount_inr=("amount_inr", "sum"))
        .sort_values("total_amount_inr", ascending=True)
    )
    fig = px.bar(
        state_flow,
        x="total_amount_inr",
        y="state",
        orientation="h",
        title="Regional Capital Inflow by State",
        labels={"state": "Indian State", "total_amount_inr": "Cumulative Investment (INR)"},
    )
    fig.update_traces(marker_color=TEAL, hovertemplate="%{y}<br>INR %{x:,.0f}<extra></extra>")
    fig.update_xaxes(tickprefix="INR ")
    fig.update_yaxes(title=None)
    return apply_bluestock_theme(fig, height=560)


def make_transaction_mix_fig(tx: pd.DataFrame) -> go.Figure:
    mix = tx.groupby("transaction_type", as_index=False).agg(volume=("transaction_type", "size"))
    colors = [NAVY, TEAL, SLATE]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=mix["transaction_type"],
                values=mix["volume"],
                hole=0.62,
                sort=False,
                marker=dict(colors=colors, line=dict(color=WHITE, width=2)),
                textinfo="percent",
                hovertemplate="%{label}<br>Transactions: %{value}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(title="Transaction Product Mix", showlegend=True)
    return apply_bluestock_theme(fig, height=520)


def make_ticket_size_box_fig(tx: pd.DataFrame) -> go.Figure:
    order = ["18-25", "26-35", "36-45", "46-55", "56+"]
    existing_order = [x for x in order if x in set(tx["age_group"].astype(str).unique())]
    fig = px.box(
        tx,
        x="age_group",
        y="amount_inr",
        color="age_group",
        points="outliers",
        category_orders={"age_group": existing_order},
        title="Ticket Size Distribution by Age Cohort",
        labels={"age_group": "Age Group", "amount_inr": "Transaction Amount (INR)"},
    )
    fig.update_traces(marker=dict(size=4), line=dict(width=1.5))
    fig.update_layout(showlegend=False)
    fig.update_yaxes(tickprefix="INR ")
    return apply_bluestock_theme(fig, height=560)


def make_sip_market_fig(sip_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> go.Figure:
    sip = sip_df.copy()
    sip["month"] = resolve_month_start(sip["month"])
    sip = sip.groupby("month", as_index=False).agg(sip_inflow_crore=("sip_inflow_crore", "sum"))

    nifty = benchmark_df.loc[benchmark_df["index_name"] == "NIFTY50"].copy()
    nifty["month"] = resolve_month_start(nifty["date"])
    nifty_monthly = nifty.groupby("month", as_index=False).agg(close_value=("close_value", "last"))

    merged = sip.merge(nifty_monthly, on="month", how="inner").sort_values("month")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=merged["month"],
            y=merged["sip_inflow_crore"],
            name="Monthly SIP Inflows",
            marker_color=TEAL,
            opacity=0.84,
            hovertemplate="%{x|%b %Y}<br>SIP Inflow: INR %{y:,.0f} Cr<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=merged["month"],
            y=merged["close_value"],
            name="Nifty 50 Close",
            mode="lines+markers",
            line=dict(color=NAVY, width=3),
            marker=dict(size=5),
            hovertemplate="%{x|%b %Y}<br>Nifty 50: %{y:,.2f}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Monthly SIP Inflows vs Nifty 50 Close Value",
        barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.01),
    )
    fig.update_xaxes(tickformat="%b %Y")
    fig.update_yaxes(title_text="SIP Inflows (INR Cr)", secondary_y=False, tickprefix="INR ")
    fig.update_yaxes(title_text="Nifty 50 Close", secondary_y=True)
    return apply_bluestock_theme(fig, height=560)


def make_category_heatmap_fig(category_df: pd.DataFrame) -> go.Figure:
    heat = category_df.copy()
    heat["month_label"] = heat["month"].dt.to_period("M").dt.strftime("%b %Y")
    heat["month_sort"] = heat["month"].dt.to_period("M").astype(str)
    pivot = heat.pivot_table(
        index="category",
        columns="month_label",
        values="net_inflow_crore",
        aggfunc="sum",
        fill_value=0,
    )
    ordered_cols = (
        heat.sort_values("month")
        .drop_duplicates("month")
        .sort_values("month")
        .assign(month_label=lambda x: x["month"].dt.to_period("M").dt.strftime("%b %Y"))["month_label"]
        .tolist()
    )
    pivot = pivot.reindex(columns=[c for c in ordered_cols if c in pivot.columns])

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale=[
                    [0.0, "#F7FBFB"],
                    [0.4, "#CFEDEC"],
                    [0.7, "#6CC7C1"],
                    [1.0, NAVY],
                ],
                colorbar=dict(title="Net Inflow (INR Cr)"),
                hovertemplate="Category: %{y}<br>Month: %{x}<br>Net Inflow: INR %{z:,.0f} Cr<extra></extra>",
            )
        ]
    )
    fig.update_layout(title="Category Inflow Heatmap (INR Cr)", xaxis_title="Month", yaxis_title="Category")
    return apply_bluestock_theme(fig, height=560)


def render_page_1(bundle: Dict[str, pd.DataFrame], kpis: Dict[str, str]) -> None:
    render_page_header(
        "Bluestock Industry Overview",
        "High-level market scale, industry concentration, and month-over-month capital formation.",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Industry AUM", kpis["industry_aum_value"], delta=kpis["industry_aum_delta"])
    with c2:
        st.metric("Monthly SIP Inflows", kpis["sip_value"], delta=kpis["sip_delta"])
    with c3:
        st.metric("Active Folios Count", kpis["folios_value"], delta=kpis["folios_delta"])
    with c4:
        st.metric("Active Fund Schemes", kpis["schemes_value"], delta=kpis["schemes_delta"])
    st.caption("Headline KPI cards reflect the Bluestock executive milestone figures specified for this dashboard.")

    aum_data = bundle["aum_by_fund_house"].copy()
    aum_data["month"] = aum_data["date"].dt.to_period("M").dt.to_timestamp()
    month_values = sorted(aum_data["month"].dropna().unique().tolist())
    if month_values:
        month_idx = st.slider(
            "AUM Timeline Window",
            min_value=0,
            max_value=len(month_values) - 1,
            value=(0, len(month_values) - 1),
            help="Slide to focus the trend and dominance charts on a specific month range.",
        )
        selected_months = month_values[month_idx[0] : month_idx[1] + 1]
    else:
        selected_months = []

    fund_house_options = sorted(aum_data["fund_house"].dropna().unique().tolist())
    selected_fund_houses = st.multiselect(
        "Fund House Filter",
        options=fund_house_options,
        default=[],
        help="Select one or more AMC names to reslice the AUM charts.",
    )

    filtered_aum = aum_data.copy()
    if selected_months:
        filtered_aum = filtered_aum.loc[filtered_aum["month"].isin(selected_months)].copy()
    if selected_fund_houses:
        filtered_aum = filtered_aum.loc[filtered_aum["fund_house"].isin(selected_fund_houses)].copy()

    if filtered_aum.empty:
        st.warning("No AUM rows match the selected month window or fund house filter. Please broaden the selection.")
        return

    left, right = st.columns([1.35, 1.0], gap="large")
    with left:
        st.plotly_chart(make_aum_trend_fig(filtered_aum), use_container_width=True, config={"displaylogo": False})
    with right:
        st.plotly_chart(make_amc_dominance_fig(filtered_aum), use_container_width=True, config={"displaylogo": False})


def render_page_2(bundle: Dict[str, pd.DataFrame]) -> None:
    render_page_header(
        "Fund Performance Dynamics",
        "Interactive performance screening with risk-adjusted ranking and institutional scorecard controls.",
    )

    perf = bundle["scheme_performance"].copy()
    perf["plan"] = perf["plan"].astype(str).str.strip().str.title()
    perf["category"] = perf["category"].astype(str).str.strip().str.title()
    perf["fund_house"] = perf["fund_house"].astype(str).str.strip()
    perf["scheme_name"] = perf["scheme_name"].astype(str).str.strip()
    perf["return_3yr_pct"] = pd.to_numeric(perf["return_3yr_pct"], errors="coerce")
    perf["std_dev_ann_pct"] = pd.to_numeric(perf["std_dev_ann_pct"], errors="coerce")
    perf["aum_crore"] = pd.to_numeric(perf["aum_crore"], errors="coerce")

    filter_col_1, filter_col_2, filter_col_3 = st.columns(3)
    fund_house_options = ["All"] + sorted(perf["fund_house"].dropna().unique().tolist())
    category_options = ["All"] + sorted(perf["category"].dropna().unique().tolist())
    plan_options = ["All"] + sorted(perf["plan"].dropna().unique().tolist())

    with filter_col_1:
        fund_house_choice = st.selectbox("Fund House Selection", fund_house_options, index=0)
    filtered_perf = perf.copy()
    if fund_house_choice != "All":
        filtered_perf = filtered_perf.loc[filtered_perf["fund_house"] == fund_house_choice].copy()
    category_options = ["All"] + sorted(filtered_perf["category"].dropna().unique().tolist())

    with filter_col_2:
        category_choice = st.selectbox("Fund Category Classification", category_options, index=0)
    if category_choice != "All":
        filtered_perf = filtered_perf.loc[filtered_perf["category"] == category_choice].copy()
    plan_options = ["All"] + sorted(filtered_perf["plan"].dropna().unique().tolist())

    with filter_col_3:
        plan_choice = st.selectbox("Plan Type (Direct vs Regular)", plan_options, index=0)
    if plan_choice != "All":
        filtered_perf = filtered_perf.loc[filtered_perf["plan"] == plan_choice].copy()

    if filtered_perf.empty:
        st.warning("No funds match the current filter combination. Please broaden one or more selectors.")
        return

    scorecard = bundle["fund_scorecard"].copy()
    scorecard["cagr_3yr_pct"] = scorecard["cagr_3yr"] * 100
    scorecard["alpha_pct"] = scorecard["alpha"] * 100
    scorecard_display = scorecard.merge(
        bundle["scheme_performance"][["amfi_code", "aum_crore", "std_dev_ann_pct"]],
        on="amfi_code",
        how="left",
    )
    scorecard_display["aum_crore"] = pd.to_numeric(scorecard_display["aum_crore"], errors="coerce")

    scorecard_display = scorecard_display[
        [
            "scheme_name",
            "cagr_3yr_pct",
            "sharpe_ratio",
            "sortino_ratio",
            "alpha_pct",
            "beta",
            "fund_house",
            "category",
            "score_rank",
            "composite_score",
            "amfi_code",
        ]
    ].rename(
        columns={
            "scheme_name": "Fund Name",
            "cagr_3yr_pct": "3-Year CAGR (%)",
            "sharpe_ratio": "Sharpe Ratio",
            "sortino_ratio": "Sortino Ratio",
            "alpha_pct": "Alpha (%)",
            "beta": "Beta",
        }
    )
    scorecard_display = scorecard_display.loc[scorecard_display["amfi_code"].isin(filtered_perf["amfi_code"])].copy()
    scorecard_display = scorecard_display.sort_values("composite_score", ascending=False).reset_index(drop=True)

    scatter_source = filtered_perf.merge(
        bundle["fund_scorecard"][["amfi_code", "composite_score", "score_rank", "cagr_3yr", "alpha", "beta"]],
        on="amfi_code",
        how="left",
        suffixes=("", "_score"),
    )

    st.plotly_chart(make_risk_return_fig(scatter_source), use_container_width=True, config={"displaylogo": False})

    st.markdown("**Sortable Institutional Scorecard**")
    st.dataframe(
        scorecard_display[
            [
                "Fund Name",
                "3-Year CAGR (%)",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Alpha (%)",
                "Beta",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "3-Year CAGR (%)": st.column_config.NumberColumn("3-Year CAGR (%)", format="%.2f"),
            "Sharpe Ratio": st.column_config.NumberColumn("Sharpe Ratio", format="%.2f"),
            "Sortino Ratio": st.column_config.NumberColumn("Sortino Ratio", format="%.2f"),
            "Alpha (%)": st.column_config.NumberColumn("Alpha (%)", format="%.2f"),
            "Beta": st.column_config.NumberColumn("Beta", format="%.3f"),
        },
    )


def render_page_3(bundle: Dict[str, pd.DataFrame]) -> None:
    render_page_header(
        "Investor & Demographic Analytics",
        "Regional flow density, transaction preference mix, and age cohort ticket sizing.",
    )

    tx = bundle["investor_transactions"].copy()
    tx = tx.dropna(subset=["amount_inr", "state", "age_group", "city_tier", "transaction_type"])
    tx["amount_inr"] = pd.to_numeric(tx["amount_inr"], errors="coerce")
    tx["state"] = tx["state"].astype(str).str.strip().str.title()
    tx["age_group"] = tx["age_group"].astype(str).str.strip()
    tx["city_tier"] = tx["city_tier"].astype(str).str.strip().str.upper()
    tx["transaction_type"] = tx["transaction_type"].astype(str).str.strip().str.title()
    tx["gender"] = tx["gender"].astype(str).str.strip().str.title()

    filter_col_1, filter_col_2, filter_col_3 = st.columns(3)
    state_options = ["All"] + sorted(tx["state"].dropna().unique().tolist())
    age_options = ["All"] + sorted(tx["age_group"].dropna().unique().tolist())
    tier_options = ["All"] + sorted(tx["city_tier"].dropna().unique().tolist())

    with filter_col_1:
        state_choice = st.selectbox("Indian State Location", state_options, index=0)
    if state_choice != "All":
        tx = tx.loc[tx["state"] == state_choice].copy()

    with filter_col_2:
        age_choice = st.selectbox("Age Cohort Group", ["All"] + sorted(tx["age_group"].dropna().unique().tolist()), index=0)
    if age_choice != "All":
        tx = tx.loc[tx["age_group"] == age_choice].copy()

    with filter_col_3:
        tier_choice = st.selectbox("City Tier Classification (T30 vs B30)", ["All"] + sorted(tx["city_tier"].dropna().unique().tolist()), index=0)
    if tier_choice != "All":
        tx = tx.loc[tx["city_tier"] == tier_choice].copy()

    if tx.empty:
        st.warning("No transaction records match the selected demographic filters. Please broaden the selectors.")
        return

    left, right = st.columns([1.15, 1.0], gap="large")
    with left:
        state_fig = make_state_inflow_fig(tx)
        st.plotly_chart(state_fig, use_container_width=True, config={"displaylogo": False})
    with right:
        mix_fig = make_transaction_mix_fig(tx)
        st.plotly_chart(mix_fig, use_container_width=True, config={"displaylogo": False})

    st.plotly_chart(make_ticket_size_box_fig(tx), use_container_width=True, config={"displaylogo": False})


def render_page_4(bundle: Dict[str, pd.DataFrame]) -> None:
    render_page_header(
        "SIP Inflows & Macro Market Trends",
        "Macro cross-checks combining SIP mobilisation with market index movement and category intensity.",
    )

    sip_data = bundle["monthly_sip_inflows"].copy()
    sip_data["month"] = resolve_month_start(sip_data["month"])
    benchmark_data = bundle["benchmark_indices"].copy()
    benchmark_data["month"] = resolve_month_start(benchmark_data["date"])
    category_data = bundle["category_inflows"].copy()
    category_data["month"] = resolve_month_start(category_data["month"])

    month_values = sorted(
        set(sip_data["month"].dropna().tolist()) |
        set(benchmark_data["month"].dropna().tolist()) |
        set(category_data["month"].dropna().tolist())
    )
    if month_values:
        month_idx = st.slider(
            "Macro Trend Window",
            min_value=0,
            max_value=len(month_values) - 1,
            value=(0, len(month_values) - 1),
            help="Use this slider to focus the SIP, Nifty 50, and category trend panels on a specific period.",
        )
        selected_months = month_values[month_idx[0] : month_idx[1] + 1]
    else:
        selected_months = []

    category_options = sorted(category_data["category"].dropna().unique().tolist())
    selected_categories = st.multiselect(
        "Category Filter",
        options=category_options,
        default=[],
        help="Select fund categories to reslice the inflow heatmap.",
    )

    if selected_months:
        sip_data = sip_data.loc[sip_data["month"].isin(selected_months)].copy()
        benchmark_data = benchmark_data.loc[benchmark_data["month"].isin(selected_months)].copy()
        category_data = category_data.loc[category_data["month"].isin(selected_months)].copy()
    if selected_categories:
        category_data = category_data.loc[category_data["category"].isin(selected_categories)].copy()

    if sip_data.empty or benchmark_data.empty or category_data.empty:
        st.warning("No rows match the selected macro trend filters. Please broaden the month window or category selection.")
        return

    combo_fig = make_sip_market_fig(sip_data, benchmark_data)
    st.plotly_chart(combo_fig, use_container_width=True, config={"displaylogo": False})

    heat_fig = make_category_heatmap_fig(category_data)
    st.plotly_chart(heat_fig, use_container_width=True, config={"displaylogo": False})


def render_sidebar(bundle: Dict[str, pd.DataFrame]) -> str:
    st.sidebar.markdown("## Bluestock")
    st.sidebar.markdown(
        "#### Mutual Fund Analytics Workspace\n"
        "Executive dashboard for industry, fund, investor, and macro trend analysis."
    )
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigate",
        options=[
            "Page 1: Industry Overview Dashboard",
            "Page 2: Fund Performance Dynamics",
            "Page 3: Investor & Demographic Analytics",
            "Page 4: SIP Inflows & Macro Market Trends",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Data Health")
    st.sidebar.success("SQLite database connected")
    st.sidebar.caption(f"DB: {DB_PATH.name}")
    st.sidebar.caption(f"Fund Schemes: {len(bundle['dim_fund'])}")
    st.sidebar.caption(f"NAV Rows: {len(bundle['fact_nav'])}")
    st.sidebar.caption(f"Transactions: {len(bundle['fact_transactions'])}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Submission Artifacts Generator")
    st.sidebar.info(
        "To export the PDF deliverable, open the app in your browser and press "
        "`Cmd + P` on Mac or `Ctrl + P` on Windows. Set the destination to "
        "`Save as PDF`, choose `Landscape`, enable `Background graphics`, and "
        "save the file directly as `reports/Dashboard.pdf`."
    )
    st.sidebar.markdown(
        "For the 4 PNG page screenshots, use your OS capture tool on each active page:\n"
        "- `reports/01_industry_overview.png`\n"
        "- `reports/02_fund_performance.png`\n"
        "- `reports/03_investor_analytics.png`\n"
        "- `reports/04_sip_trends.png`\n\n"
        "On Mac, the quick capture shortcut is `Cmd + Shift + 4`."
    )
    return page


def main() -> None:
    bundle = load_data_bundle()
    kpis = build_latest_kpis(bundle)
    page = render_sidebar(bundle)

    st.caption(
        f"Source assets loaded from `{DB_PATH.relative_to(BASE_DIR)}` and the curated CSV layer under `data/raw/` / `data/processed/`."
    )

    if page.startswith("Page 1"):
        render_page_1(bundle, kpis)
    elif page.startswith("Page 2"):
        render_page_2(bundle)
    elif page.startswith("Page 3"):
        render_page_3(bundle)
    else:
        render_page_4(bundle)


if __name__ == "__main__":
    main()

