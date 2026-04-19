from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="UrbanEats",
    page_icon="🍗",
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
system_kpis_path = gold_root / "system_kpis"
business_kpis_path = gold_root / "business_kpis"

# -------------------------
# Styles
# -------------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #eef2f6;
        --panel: #ffffff;
        --panel-2: #f8fafc;
        --sidebar: #f6f7f9;
        --text: #17202a;
        --muted: #667085;
        --line: rgba(23, 32, 42, 0.08);
        --shadow: 0 10px 25px rgba(16, 24, 40, 0.06);

        --indigo: #5368df;
        --teal: #15b8a6;
        --mint: #7ad3c3;
        --coral: #ef6f6c;
        --slate: #98a2b3;
        --violet: #7e57c2;
    }

    .stApp {
        background: var(--bg);
    }

    section[data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.1rem;
        padding-bottom: 1.3rem;
    }

    .top-banner {
        background:
            radial-gradient(circle at top left, rgba(83,104,223,0.14), transparent 35%),
            radial-gradient(circle at top right, rgba(21,184,166,0.14), transparent 30%),
            linear-gradient(180deg, #ffffff 0%, #fbfcfd 100%);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 28px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
    }

    .tiny {
        color: var(--muted);
        font-size: 0.82rem;
        margin-bottom: 0.3rem;
    }

    .headline {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--text);
        line-height: 1.05;
        margin-bottom: 0.25rem;
    }

    .subhead {
        color: #475467;
        font-size: 1.02rem;
        margin-bottom: 0.55rem;
    }

    .flow-line {
        color: var(--muted);
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }

    .kpi-card {
        background: var(--panel);
        border-radius: 24px;
        padding: 1rem 1.05rem 0.95rem 1.05rem;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        min-height: 154px;
    }

    .kpi-bar-indigo,
    .kpi-bar-teal,
    .kpi-bar-coral,
    .kpi-bar-slate {
        height: 6px;
        border-radius: 999px;
        margin-bottom: 0.95rem;
    }

    .kpi-bar-indigo { background: var(--indigo); }
    .kpi-bar-teal   { background: var(--teal); }
    .kpi-bar-coral  { background: var(--coral); }
    .kpi-bar-slate  { background: var(--slate); }

    .kpi-label {
        color: #475467;
        font-size: 0.96rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
    }

    .kpi-value {
        color: var(--text);
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.4rem;
    }

    .kpi-foot {
        color: #98a2b3;
        font-size: 0.82rem;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text);
        margin-top: 0.6rem;
        margin-bottom: 0.15rem;
    }

    .section-sub {
        color: var(--muted);
        font-size: 0.94rem;
        margin-bottom: 0.8rem;
    }

    .soft-panel {
        background: var(--panel);
        border-radius: 24px;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        padding: 0.8rem 0.9rem 0.55rem 0.9rem;
    }

    .mini-kpi {
        background: var(--panel);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 18px;
        padding: 0.8rem 0.95rem;
    }

    .mini-kpi-title {
        color: #667085;
        font-size: 0.88rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .mini-kpi-value {
        color: var(--text);
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .sidebar-chip {
        background: #ffffff;
        border: 1px solid rgba(23, 32, 42, 0.08);
        border-radius: 16px;
        padding: 0.9rem 0.95rem;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.05);
        margin-bottom: 1rem;
    }

    .status-pill {
        display: inline-block;
        background: rgba(21,184,166,0.12);
        color: #0d9488;
        border-radius: 999px;
        padding: 0.28rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 800;
    }

    /* boton sidebar: respetando tu solución */
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
# Helpers
# -------------------------
@st.cache_data
def load_data():
    if not orders_path.exists():
        raise FileNotFoundError(f"Missing orders gold data: {orders_path}")
    if not demand_supply_path.exists():
        raise FileNotFoundError(f"Missing demand/supply gold data: {demand_supply_path}")
    if not anomalies_path.exists():
        raise FileNotFoundError(f"Missing anomalies gold data: {anomalies_path}")
    if not system_kpis_path.exists():
        raise FileNotFoundError(f"Missing system_kpis gold data: {system_kpis_path}")
    if not business_kpis_path.exists():
        raise FileNotFoundError(f"Missing business_kpis gold data: {business_kpis_path}")

    orders = pd.read_parquet(orders_path)
    demand_supply = pd.read_parquet(demand_supply_path)
    anomalies = pd.read_parquet(anomalies_path)
    system_kpis = pd.read_parquet(system_kpis_path)
    business_kpis = pd.read_parquet(business_kpis_path)

    if "window_start" in orders.columns:
        orders["window_start"] = pd.to_datetime(orders["window_start"])
    if "window_end" in orders.columns:
        orders["window_end"] = pd.to_datetime(orders["window_end"])

    return orders, demand_supply, anomalies, system_kpis, business_kpis


def safe_sum(df, col):
    if col not in df.columns or df.empty:
        return 0.0
    return float(df[col].fillna(0).sum())


def safe_mean(df, col):
    if col not in df.columns or df.empty:
        return 0.0
    s = df[col].dropna()
    return float(s.mean()) if not s.empty else 0.0


def safe_first(df, col):
    if col not in df.columns or df.empty:
        return 0
    return df.iloc[0][col]


def kpi_card(title, value, bar_class, subtitle):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="{bar_class}"></div>
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mini_kpi(title, value):
    st.markdown(
        f"""
        <div class="mini-kpi">
            <div class="mini-kpi-title">{title}</div>
            <div class="mini-kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# Sidebar
# -------------------------
st.sidebar.markdown("## 🍗 UrbanEats Monitor")
st.sidebar.caption("Group 7 · Spring 2026")
st.sidebar.caption("Synthetic food delivery observability")

st.sidebar.markdown(
    """
    <div class="sidebar-chip">
        <div class="status-pill">● System online</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Workspace",
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
st.sidebar.markdown("### Filters")

# -------------------------
# Load data
# -------------------------
try:
    orders_df, demand_supply_df, anomalies_df, system_kpis_df, business_kpis_df = load_data()
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
# KPI calculations
# -------------------------
# business_kpis are GLOBAL and should not be summed from window buckets
unique_orders = int(safe_first(business_kpis_df, "unique_orders"))
delivered_orders = int(safe_first(business_kpis_df, "delivered_orders"))
cancelled_orders = int(safe_first(business_kpis_df, "cancelled_orders"))
total_revenue = float(safe_first(business_kpis_df, "total_revenue"))
cancel_rate = float(safe_first(business_kpis_df, "cancel_rate")) * 100

# average order value can still be shown from the bucketed view
avg_order_value = safe_mean(orders_view, "avg_order_value")
zones_selected = len(selected_zones) if selected_zones else len(zones)

# system KPIs
order_events = int(safe_first(system_kpis_df, "order_events"))
delivery_events = int(safe_first(system_kpis_df, "delivery_events"))
total_events = int(safe_first(system_kpis_df, "total_events"))
active_zones = int(safe_first(system_kpis_df, "active_zones"))

last_sync = datetime.now().strftime("%H:%M:%S")

# -------------------------
# Header
# -------------------------
st.markdown(
    f"""
    <div class="top-banner">
        <div class="tiny">Last sync {last_sync}</div>
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="font-size:2rem;">🍗</div>
            <div>
                <div class="headline">UrbanEats Monitor</div>
                <div class="subhead">Operational intelligence for synthetic food delivery streams</div>
            </div>
        </div>
        <div class="flow-line">Python Generator → Azure Event Hubs → Spark → Azure Blob → Streamlit</div>
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
        kpi_card("Unique Orders", f"{unique_orders:,}", "kpi-bar-indigo", "Distinct customer orders")
    with c2:
        kpi_card("🏍️ Delivered Orders", f"{delivered_orders:,}", "kpi-bar-teal", "Successfully completed")
    with c3:
        kpi_card("💰 Total Revenue", f"€{total_revenue:,.2f}", "kpi-bar-slate", "Delivered-order revenue")
    with c4:
        kpi_card("❌ Cancellation Rate", f"{cancel_rate:.1f}%", "kpi-bar-coral", "Global cancellation share")

    st.markdown('<div class="section-title">System Activity</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Technical flow counters complementary to the business KPIs</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        mini_kpi("Order Events", f"{order_events:,}")
    with s2:
        mini_kpi("Delivery Events", f"{delivery_events:,}")
    with s3:
        mini_kpi("Total Events", f"{total_events:,}")
    with s4:
        mini_kpi("🗺️Active Zones", f"{active_zones:,}")

    st.markdown('<div class="section-title">Business Snapshot</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Current summary for the selected operational zones</div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.metric("Cancelled Orders", f"{cancelled_orders:,}")
    with b2:
        st.metric("Average Order Value", f"€{avg_order_value:,.2f}")
    with b3:
        st.metric("Zones Selected", f"{zones_selected}")
    with b4:
        success_rate = (delivered_orders / unique_orders * 100) if unique_orders > 0 else 0.0
        st.metric("Delivery Success", f"{success_rate:.1f}%")

    st.markdown('<div class="section-title">Demand trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">5-minute aggregation of distinct orders per selected zones</div>', unsafe_allow_html=True)

    if not orders_view.empty and "window_start" in orders_view.columns and "unique_orders" in orders_view.columns:
        series_df = (
            orders_view.groupby("window_start", as_index=False)["unique_orders"]
            .sum()
            .sort_values("window_start")
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=series_df["window_start"],
                y=series_df["unique_orders"],
                mode="lines",
                line=dict(color="#5368df", width=3),
                fill="tozeroy",
                fillcolor="rgba(83,104,223,0.14)",
                hovertemplate="%{x}<br>Distinct orders in bucket: %{y}<extra></extra>",
                name="Distinct orders",
            )
        )
        fig.update_layout(
            height=470,
            margin=dict(l=16, r=16, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            hovermode="x unified",
            xaxis_title="Time",
            yaxis_title="Distinct orders",
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="rgba(23, 32, 42, 0.08)")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
        st.markdown('<div class="small-card-title">Demand vs Supply</div>', unsafe_allow_html=True)
        if not demand_supply_view.empty:
            fig_ds = go.Figure()
            fig_ds.add_bar(
                x=demand_supply_view["zone_id"],
                y=demand_supply_view["waiting_orders"],
                name="Waiting orders",
                marker_color="#15b8a6",
            )
            fig_ds.add_bar(
                x=demand_supply_view["zone_id"],
                y=demand_supply_view["available_couriers"],
                name="Available couriers",
                marker_color="#5368df",
            )
            fig_ds.update_layout(
                barmode="group",
                height=360,
                margin=dict(l=8, r=8, t=8, b=8),
                paper_bgcolor="white",
                plot_bgcolor="white",
                legend_title_text="",
            )
            fig_ds.update_yaxes(gridcolor="rgba(23, 32, 42, 0.08)")
            st.plotly_chart(fig_ds, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
        st.markdown('<div class="small-card-title">Avg. Delivery Time</div>', unsafe_allow_html=True)
        if not anomalies_view.empty:
            color_map = anomalies_view["anomaly_flag"].map({0: "#cbd5e1", 1: "#ef6f6c"}).fillna("#cbd5e1")
            fig_an = go.Figure()
            fig_an.add_bar(
                x=anomalies_view["zone_id"],
                y=anomalies_view["avg_delivery_minutes"],
                marker_color=color_map,
                hovertemplate="Zone: %{x}<br>Avg delivery: %{y:.1f} min<extra></extra>",
            )
            fig_an.update_layout(
                height=360,
                margin=dict(l=8, r=8, t=8, b=8),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
            )
            fig_an.update_yaxes(gridcolor="rgba(23, 32, 42, 0.08)", title="Minutes")
            st.plotly_chart(fig_an, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Operations
# -------------------------
elif page == "Operations":
    st.markdown('<div class="section-title">Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Window-level operational KPIs for each zone</div>', unsafe_allow_html=True)

    cols = [
        c for c in [
            "window_start", "window_end", "zone_id", "orders_total", "unique_orders",
            "delivered_orders", "cancelled_orders", "avg_order_value", "total_revenue", "cancel_rate"
        ] if c in orders_view.columns
    ]

    st.dataframe(
        orders_view[cols].sort_values(["window_start", "zone_id"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )

    if not orders_view.empty:
        zone_summary_cols = [c for c in ["unique_orders", "delivered_orders", "cancelled_orders", "total_revenue"] if c in orders_view.columns]
        zone_summary = (
            orders_view.groupby("zone_id", as_index=False)[zone_summary_cols]
            .sum()
            .sort_values("unique_orders", ascending=False)
        )

        fig_ops = go.Figure()
        fig_ops.add_bar(x=zone_summary["zone_id"], y=zone_summary["unique_orders"], name="Distinct orders", marker_color="#5368df")
        fig_ops.add_bar(x=zone_summary["zone_id"], y=zone_summary["delivered_orders"], name="Delivered", marker_color="#15b8a6")
        fig_ops.add_bar(x=zone_summary["zone_id"], y=zone_summary["cancelled_orders"], name="Cancelled", marker_color="#ef6f6c")
        fig_ops.update_layout(
            barmode="group",
            height=430,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=8, r=8, t=10, b=8),
        )
        fig_ops.update_yaxes(gridcolor="rgba(23, 32, 42, 0.08)")
        st.plotly_chart(fig_ops, use_container_width=True)

# -------------------------
# Fleet & Couriers
# -------------------------
elif page == "Fleet & Couriers":
    st.markdown('<div class="section-title">Fleet & Couriers</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Zone pressure, courier availability and balance indicators</div>', unsafe_allow_html=True)

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
            title="Zone pressure map",
        )
        fig_fleet.update_layout(
            height=480,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=8, r=8, t=48, b=8),
        )
        fig_fleet.update_yaxes(gridcolor="rgba(23, 32, 42, 0.08)")
        st.plotly_chart(fig_fleet, use_container_width=True)

# -------------------------
# Pipeline Health
# -------------------------
else:
    st.markdown('<div class="section-title">Pipeline Health</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Gold layer readiness and anomaly tracking</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Orders Gold Rows", f"{len(orders_df):,}")
    with p2:
        st.metric("Demand/Supply Rows", f"{len(demand_supply_df):,}")
    with p3:
        st.metric("Anomaly Rows", f"{len(anomalies_df):,}")
    with p4:
        zones_in_alert = int(anomalies_view["anomaly_flag"].sum()) if "anomaly_flag" in anomalies_view.columns else 0
        st.metric("Zones in Alert", f"{zones_in_alert}")

    st.dataframe(
        anomalies_view.sort_values("avg_delivery_minutes", ascending=False),
        use_container_width=True,
        hide_index=True,
    )