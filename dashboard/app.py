import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Madrid Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# Paths
# -------------------------
cwd = Path.cwd()
repo_root = cwd.parent if cwd.name == "dashboard" else cwd

gold_root = repo_root / "data" / "gold"
orders_path = gold_root / "orders_kpi_5m"
demand_supply_path = gold_root / "demand_supply_zone"
anomalies_path = gold_root / "delivery_anomalies"

# -------------------------
# Custom theme / styles
# -------------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #f4f6f8;
        --card: #ffffff;
        --text: #1f2a37;
        --muted: #667085;
        --navy: #0f172a;
        --navy-2: #132238;
        --teal: #149a9b;
        --teal-soft: #47c0c1;
        --mint: #7cc7b2;
        --slate: #98a2b3;
        --rose: #e35d6a;
        --shadow: 0 10px 30px rgba(16, 24, 40, 0.08);
        --radius: 20px;
    }

    .stApp {
        background: var(--bg);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #132238 55%, #17314d 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 1.2rem;
        max-width: 1450px;
    }

    .hero-card {
        background: linear-gradient(180deg, #ffffff 0%, #fbfcfd 100%);
        border-radius: 24px;
        padding: 1.25rem 1.35rem;
        box-shadow: var(--shadow);
        border-left: 8px solid var(--teal);
        margin-bottom: 1rem;
    }

    .hero-kicker {
        color: var(--muted);
        font-size: 0.82rem;
        margin-bottom: 0.35rem;
    }

    .hero-title {
        color: var(--text);
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        color: #475467;
        font-size: 1.05rem;
        margin-bottom: 0.55rem;
    }

    .hero-flow {
        color: #667085;
        font-size: 0.98rem;
        margin-top: 0.5rem;
    }

    .metric-shell {
        background: var(--card);
        border-radius: 22px;
        padding: 1.1rem 1.1rem 1rem 1.1rem;
        box-shadow: var(--shadow);
        min-height: 160px;
        border: 1px solid rgba(15, 23, 42, 0.04);
    }

    .metric-line-teal {
        height: 5px;
        background: var(--teal);
        border-radius: 999px;
        margin: -0.1rem -0.1rem 0.9rem -0.1rem;
    }

    .metric-line-mint {
        height: 5px;
        background: var(--mint);
        border-radius: 999px;
        margin: -0.1rem -0.1rem 0.9rem -0.1rem;
    }

    .metric-line-slate {
        height: 5px;
        background: var(--slate);
        border-radius: 999px;
        margin: -0.1rem -0.1rem 0.9rem -0.1rem;
    }

    .metric-line-rose {
        height: 5px;
        background: var(--rose);
        border-radius: 999px;
        margin: -0.1rem -0.1rem 0.9rem -0.1rem;
    }

    .metric-label {
        color: #4b5565;
        font-size: 0.96rem;
        margin-bottom: 0.55rem;
        font-weight: 600;
    }

    .metric-value {
        color: #101828;
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.35rem;
    }

    .metric-sub {
        color: #98a2b3;
        font-size: 0.83rem;
    }

    .section-title {
        color: #1d2939;
        font-size: 1.95rem;
        font-weight: 800;
        margin-top: 0.35rem;
        margin-bottom: 0.25rem;
    }

    .section-subtitle {
        color: #667085;
        font-size: 0.92rem;
        margin-bottom: 0.85rem;
    }

    .small-card-title {
        color: #1f2a37;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .sidebar-badge {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 0.85rem 0.9rem;
        margin-top: 0.6rem;
        margin-bottom: 1.1rem;
    }

    /* TU ESTILO DEL BOTON - NO TOCADO */
    section[data-testid="stSidebar"] div.stButton > button {
        background: #149A9B !important;
        color: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.55rem 1rem !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.2) !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: #dbeafe !important;
        color: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:focus:not(:active) {
        color: #0f172a !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Data loading
# -------------------------
@st.cache_data
def load_data():
    if not orders_path.exists():
        raise FileNotFoundError(f"Missing orders gold data: {orders_path}")
    if not demand_supply_path.exists():
        raise FileNotFoundError(f"Missing demand/supply gold data: {demand_supply_path}")
    if not anomalies_path.exists():
        raise FileNotFoundError(f"Missing anomalies gold data: {anomalies_path}")

    orders = pd.read_parquet(orders_path)
    demand_supply = pd.read_parquet(demand_supply_path)
    anomalies = pd.read_parquet(anomalies_path)

    if "window_start" in orders.columns:
        orders["window_start"] = pd.to_datetime(orders["window_start"])
    if "window_end" in orders.columns:
        orders["window_end"] = pd.to_datetime(orders["window_end"])

    return orders, demand_supply, anomalies


def safe_sum(df, col):
    if col not in df.columns or df.empty:
        return 0.0
    return float(df[col].fillna(0).sum())


def safe_mean(df, col):
    if col not in df.columns or df.empty:
        return 0.0
    s = df[col].dropna()
    return float(s.mean()) if not s.empty else 0.0


def safe_nunique(df, col):
    if col not in df.columns or df.empty:
        return 0
    return int(df[col].nunique())


def metric_card(title, value, line_class, subtitle=""):
    st.markdown(
        f"""
        <div class="metric-shell">
            <div class="{line_class}"></div>
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Sidebar
# -------------------------
st.sidebar.markdown("## 🍽️ Madrid Analytics")
st.sidebar.caption("Group 7 · Spring 2026")
st.sidebar.caption("Food delivery operations intelligence")

st.sidebar.markdown(
    """
    <div class="sidebar-badge">
        <div style="font-size:1rem;font-weight:700;">🟢 Live</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Operations", "Fleet & Couriers", "Pipeline Health"],
    index=0,
)

auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
if auto_refresh:
    st_autorefresh(interval=30000, key="dashboard_autorefresh")

refresh = st.sidebar.button("↻ Refresh data")
if refresh:
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Controls")

# -------------------------
# Load
# -------------------------
try:
    orders_df, demand_supply_df, anomalies_df = load_data()
except Exception as e:
    st.error(f"Dashboard data could not be loaded: {e}")
    st.stop()

zones = []
if "zone_id" in orders_df.columns:
    zones = sorted([z for z in orders_df["zone_id"].dropna().unique().tolist()])

selected_zones = st.sidebar.multiselect(
    "Filter by zone",
    zones,
    default=zones if len(zones) <= 4 else zones[:4]
)

if selected_zones:
    orders_view = orders_df[orders_df["zone_id"].isin(selected_zones)].copy()
    demand_supply_view = demand_supply_df[demand_supply_df["zone_id"].isin(selected_zones)].copy()
    anomalies_view = anomalies_df[anomalies_df["zone_id"].isin(selected_zones)].copy()
else:
    orders_view = orders_df.copy()
    demand_supply_view = demand_supply_df.copy()
    anomalies_view = anomalies_df.copy()

# -------------------------
# KPIs
# -------------------------
order_events = int(safe_sum(orders_view, "orders_total"))
delivered_orders = int(safe_sum(orders_view, "delivered_orders"))
cancelled_orders = int(safe_sum(orders_view, "cancelled_orders"))
avg_order_value = safe_mean(orders_view, "avg_order_value")
cancel_rate = safe_mean(orders_view, "cancel_rate") * 100
total_revenue = safe_sum(orders_view, "total_revenue")
unique_orders = int(safe_sum(orders_view, "unique_orders")) if "unique_orders" in orders_view.columns else safe_nunique(orders_view, "zone_id")
last_refresh = datetime.now().strftime("%H:%M:%S")

# -------------------------
# Header
# -------------------------
st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-kicker">Last sync {last_refresh}</div>
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="font-size:2rem;">🍽️</div>
            <div>
                <div class="hero-title">Madrid Operations · Live</div>
                <div class="hero-subtitle">Real-time food delivery analytics · Group 7</div>
            </div>
        </div>
        <div class="hero-flow">Event Generator → Event Hub → Spark SQL → Azure Blob Storage → Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Overview
# -------------------------
if page == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Order Events", f"{order_events:,}", "metric-line-teal", "Windowed order-event count")
    with c2:
        metric_card("Delivered Orders", f"{delivered_orders:,}", "metric-line-mint", "Delivered lifecycle events")
    with c3:
        metric_card("Total Revenue", f"€{total_revenue:,.2f}", "metric-line-slate", "Delivered-order revenue")
    with c4:
        metric_card("Cancellation Rate", f"{cancel_rate:.1f}%", "metric-line-rose", "Windowed average")

    st.caption("Live operational snapshot built from Gold analytics outputs stored in Azure Blob.")

    st.markdown('<div class="section-title">Order Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Operational summary across the selected zones</div>', unsafe_allow_html=True)

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Cancelled Orders", f"{cancelled_orders:,}")
    with a2:
        st.metric("Average Order Value", f"€{avg_order_value:,.2f}")
    with a3:
        st.metric("Unique Orders", f"{unique_orders:,}")
    with a4:
        st.metric("Zones Selected", f"{len(selected_zones) if selected_zones else len(zones)}")

    st.markdown('<div class="section-title">Order events over time</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">5-minute buckets aggregated from Gold outputs</div>', unsafe_allow_html=True)

    if not orders_view.empty and "window_start" in orders_view.columns:
        series_df = (
            orders_view.groupby("window_start", as_index=False)["orders_total"]
            .sum()
            .sort_values("window_start")
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=series_df["window_start"],
                y=series_df["orders_total"],
                mode="lines",
                fill="tozeroy",
                line=dict(color="#2fa7a8", width=3),
                fillcolor="rgba(47, 167, 168, 0.18)",
                hovertemplate="%{x}<br>Order events: %{y}<extra></extra>",
                name="Order events",
            )
        )
        fig.update_layout(
            height=470,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Time",
            yaxis_title="Events",
            showlegend=False,
            hovermode="x unified",
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="rgba(15, 23, 42, 0.08)")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="small-card-title">Demand vs Supply by zone</div>', unsafe_allow_html=True)
        if not demand_supply_view.empty:
            fig_ds = go.Figure()
            fig_ds.add_bar(
                x=demand_supply_view["zone_id"],
                y=demand_supply_view["waiting_orders"],
                name="Waiting orders",
                marker_color="#8fd3d4",
            )
            fig_ds.add_bar(
                x=demand_supply_view["zone_id"],
                y=demand_supply_view["available_couriers"],
                name="Available couriers",
                marker_color="#187d94",
            )
            fig_ds.update_layout(
                barmode="group",
                height=360,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                legend_title_text="",
            )
            fig_ds.update_yaxes(gridcolor="rgba(15, 23, 42, 0.08)")
            st.plotly_chart(fig_ds, use_container_width=True)

    with right:
        st.markdown('<div class="small-card-title">Delivery anomaly monitor</div>', unsafe_allow_html=True)
        if not anomalies_view.empty:
            anomaly_colors = anomalies_view["anomaly_flag"].map({0: "#b7d6c2", 1: "#4bb3b5"}).fillna("#b7d6c2")

            fig_an = go.Figure()
            fig_an.add_bar(
                x=anomalies_view["zone_id"],
                y=anomalies_view["avg_delivery_minutes"],
                marker_color=anomaly_colors,
                hovertemplate="Zone: %{x}<br>Avg delivery: %{y:.1f} min<extra></extra>",
            )
            fig_an.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
            )
            fig_an.update_yaxes(gridcolor="rgba(15, 23, 42, 0.08)", title="Minutes")
            st.plotly_chart(fig_an, use_container_width=True)

# -------------------------
# Operations
# -------------------------
elif page == "Operations":
    st.markdown('<div class="section-title">Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Window-level KPI view for operational monitoring</div>', unsafe_allow_html=True)

    view_cols = [
        c for c in [
            "window_start", "window_end", "zone_id", "orders_total",
            "delivered_orders", "cancelled_orders", "avg_order_value", "total_revenue", "cancel_rate", "unique_orders"
        ] if c in orders_view.columns
    ]

    st.dataframe(
        orders_view[view_cols].sort_values(["window_start", "zone_id"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )

    if not orders_view.empty:
        zone_summary_cols = [c for c in ["orders_total", "delivered_orders", "cancelled_orders", "total_revenue"] if c in orders_view.columns]
        zone_summary = (
            orders_view.groupby("zone_id", as_index=False)[zone_summary_cols]
            .sum()
            .sort_values("orders_total", ascending=False)
        )

        fig_ops = go.Figure()
        fig_ops.add_bar(x=zone_summary["zone_id"], y=zone_summary["orders_total"], name="Order events", marker_color="#2fa7a8")
        fig_ops.add_bar(x=zone_summary["zone_id"], y=zone_summary["delivered_orders"], name="Delivered", marker_color="#7cc7b2")
        fig_ops.add_bar(x=zone_summary["zone_id"], y=zone_summary["cancelled_orders"], name="Cancelled", marker_color="#e35d6a")
        fig_ops.update_layout(
            barmode="group",
            height=420,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        fig_ops.update_yaxes(gridcolor="rgba(15, 23, 42, 0.08)")
        st.plotly_chart(fig_ops, use_container_width=True)

# -------------------------
# Fleet
# -------------------------
elif page == "Fleet & Couriers":
    st.markdown('<div class="section-title">Fleet & Couriers</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Supply-side operational balance and zone stress</div>', unsafe_allow_html=True)

    st.dataframe(
        demand_supply_view.sort_values("demand_supply_ratio", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    if not demand_supply_view.empty:
        fig_fleet = px.scatter(
            demand_supply_view,
            x="available_couriers",
            y="waiting_orders",
            size="demand_supply_ratio",
            color="zone_id",
            title="Zone stress map",
        )
        fig_fleet.update_layout(
            height=480,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        fig_fleet.update_yaxes(gridcolor="rgba(15, 23, 42, 0.08)")
        st.plotly_chart(fig_fleet, use_container_width=True)

# -------------------------
# Pipeline Health
# -------------------------
else:
    st.markdown('<div class="section-title">Pipeline Health</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Gold layer readiness and anomaly status</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Orders Gold Rows", f"{len(orders_df):,}")
    with p2:
        st.metric("Demand/Supply Rows", f"{len(demand_supply_df):,}")
    with p3:
        st.metric("Anomaly Rows", f"{len(anomalies_df):,}")
    with p4:
        anomaly_count = int(anomalies_view["anomaly_flag"].sum()) if "anomaly_flag" in anomalies_view.columns else 0
        st.metric("Zones in Alert", f"{anomaly_count}")

    st.dataframe(
        anomalies_view.sort_values("avg_delivery_minutes", ascending=False),
        use_container_width=True,
        hide_index=True,
    )