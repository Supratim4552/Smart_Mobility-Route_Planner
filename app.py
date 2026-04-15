"""
Smart Mobility — Hazard-Aware Route Planner
A Streamlit application for intelligent urban route planning with
real-time hazard simulation and interactive map visualization.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime

from hazard_simulator import HazardSimulator, HAZARD_TEMPLATES
from route_planner import plan_routes, RoutePoint, haversine_distance

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Mobility · Route Planner",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS for Premium Look
# ──────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global ────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ───────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #e0e0e0;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

/* ── Metric cards ──────────────────────── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea20, #764ba220);
    border: 1px solid #667eea40;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, .12);
}
div[data-testid="stMetric"] label {
    color: #a0a0c0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 1.6rem !important;
}

/* ── Expander ──────────────────────────── */
details {
    border: 1px solid #667eea30 !important;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #1a1a2e10, #16213e10) !important;
}

/* ── Tabs ──────────────────────────────── */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

/* ── Branded header ────────────────────── */
.brand-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 8px 32px rgba(102, 126, 234, .25);
}
.brand-header h1 {
    margin: 0; font-size: 2.2rem; font-weight: 700;
}
.brand-header p {
    margin: 0.4rem 0 0; opacity: 0.88; font-size: 1.05rem;
}

/* ── Route cards ───────────────────────── */
.route-card {
    border: 1px solid #e0e0e0;
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    background: #ffffff;
    transition: transform .2s, box-shadow .2s;
}
.route-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,.08);
}
.route-card.recommended {
    border: 2px solid #2ecc71;
    background: linear-gradient(135deg, #2ecc7108, #27ae6008);
}
.route-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-safe   { background: #2ecc7125; color: #27ae60; }
.badge-warn   { background: #f39c1225; color: #e67e22; }
.badge-danger { background: #e74c3c25; color: #c0392b; }

/* ── Hazard table severity dots ─────── */
.severity-dot {
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; margin-right: 6px;
}

/* ── Info tiles ─────────────────────── */
.info-tile {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.info-tile h3 { margin: 0 0 4px; font-size: 1.5rem; }
.info-tile p  { margin: 0; color: #6c757d; font-size: 0.85rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Preset city locations
# ──────────────────────────────────────────────
CITY_PRESETS = {
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Custom": {"lat": 0.0, "lon": 0.0},
}

# ──────────────────────────────────────────────
# Sidebar Controls
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚗 Smart Mobility")
    st.markdown("##### Hazard-Aware Route Planner")
    st.markdown("---")

    # City selection
    st.markdown("### 📍 Location Settings")
    city = st.selectbox("Select City", list(CITY_PRESETS.keys()), index=0)

    if city == "Custom":
        center_lat = st.number_input("Center Latitude", value=22.5726, format="%.4f")
        center_lon = st.number_input("Center Longitude", value=88.3639, format="%.4f")
    else:
        center_lat = CITY_PRESETS[city]["lat"]
        center_lon = CITY_PRESETS[city]["lon"]

    st.markdown("---")

    # Route endpoints
    st.markdown("### 🗺️ Route Endpoints")
    col_a, col_b = st.columns(2)
    with col_a:
        start_lat = st.number_input("Start Lat", value=center_lat - 0.015, format="%.4f")
    with col_b:
        start_lon = st.number_input("Start Lon", value=center_lon - 0.012, format="%.4f")

    col_c, col_d = st.columns(2)
    with col_c:
        end_lat = st.number_input("End Lat", value=center_lat + 0.018, format="%.4f")
    with col_d:
        end_lon = st.number_input("End Lon", value=center_lon + 0.015, format="%.4f")

    st.markdown("---")

    # Simulation controls
    st.markdown("### ⚙️ Simulation Controls")
    hazard_count = st.slider("Number of Hazards", 3, 10, 6)
    sim_radius = st.slider("Simulation Radius (km)", 1.0, 10.0, 4.0, step=0.5)

    regenerate = st.button("🔄  Simulate Hazards & Plan Routes", use_container_width=True, type="primary")

    st.markdown("---")
    st.caption(f"🕒 {datetime.now().strftime('%d %b %Y  •  %I:%M %p')}")

# ──────────────────────────────────────────────
# Session-state initialisation
# ──────────────────────────────────────────────
if "hazards" not in st.session_state or regenerate:
    sim = HazardSimulator(center_lat, center_lon, radius_km=sim_radius)
    st.session_state.hazards = sim.generate_hazards(count=hazard_count)
    st.session_state.risk_score = sim.calculate_risk_score()
    st.session_state.summary = sim.get_hazard_summary()

    start = RoutePoint(latitude=start_lat, longitude=start_lon, label="Start")
    end = RoutePoint(latitude=end_lat, longitude=end_lon, label="End")
    st.session_state.routes = plan_routes(start, end, st.session_state.hazards)

hazards = st.session_state.hazards
routes = st.session_state.routes
risk_score = st.session_state.risk_score
summary = st.session_state.summary

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown(
    """
<div class="brand-header">
    <h1>🚗 Smart Mobility Dashboard</h1>
    <p>AI-powered hazard-aware route planning for safer urban commutes</p>
</div>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# KPI Row
# ──────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Active Hazards", len(hazards))
k2.metric("Area Risk Score", f"{risk_score}%")
k3.metric("Routes Planned", len(routes))
best = min(routes, key=lambda r: r.risk_score)
k4.metric("Best Route Risk", f"{best.risk_score}%")

# ──────────────────────────────────────────────
# Main Content — Tabs
# ──────────────────────────────────────────────
tab_map, tab_routes, tab_hazards, tab_analytics = st.tabs(
    ["🗺️ Live Map", "🛣️ Routes", "⚠️ Hazards", "📊 Analytics"]
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — Interactive Map
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_map:
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="CartoDB dark_matter",
    )

    # Draw routes
    for route in routes:
        coords = [(p.latitude, p.longitude) for p in route.points]
        weight = 6 if route.is_recommended else 3
        opacity = 1.0 if route.is_recommended else 0.6
        folium.PolyLine(
            coords,
            color=route.color,
            weight=weight,
            opacity=opacity,
            tooltip=f"{route.name}  •  {route.distance_km} km  •  Risk {route.risk_score}%",
            dash_array="10 6" if not route.is_recommended else None,
        ).add_to(m)

    # Start / End markers
    folium.Marker(
        [start_lat, start_lon],
        tooltip="🟢 Start",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        [end_lat, end_lon],
        tooltip="🔴 Destination",
        icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
    ).add_to(m)

    # Hazard markers
    for h in hazards:
        icon_color = {"low": "lightgreen", "medium": "orange", "high": "red", "critical": "darkred"}.get(
            h.severity, "gray"
        )
        folium.CircleMarker(
            location=[h.latitude, h.longitude],
            radius=8,
            color=h.severity_color,
            fill=True,
            fill_color=h.severity_color,
            fill_opacity=0.7,
            tooltip=f"<b>{h.name}</b><br>{h.description}<br>Severity: {h.severity.upper()}",
        ).add_to(m)

        # Hazard radius circle
        folium.Circle(
            location=[h.latitude, h.longitude],
            radius=h.radius_m,
            color=h.severity_color,
            fill=True,
            fill_opacity=0.10,
            weight=1,
        ).add_to(m)

    st_folium(m, use_container_width=True, height=520, returned_objects=[])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — Route Details
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_routes:
    st.markdown("### Planned Routes")
    for route in routes:
        rec_class = "recommended" if route.is_recommended else ""
        if route.risk_score < 30:
            badge = '<span class="route-badge badge-safe">LOW RISK</span>'
        elif route.risk_score < 60:
            badge = '<span class="route-badge badge-warn">MODERATE RISK</span>'
        else:
            badge = '<span class="route-badge badge-danger">HIGH RISK</span>'

        rec_label = ' &nbsp;⭐ <b>RECOMMENDED</b>' if route.is_recommended else ""

        st.markdown(
            f"""
<div class="route-card {rec_class}">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <h3 style="margin:0">{route.name}{rec_label}</h3>
        {badge}
    </div>
    <hr style="margin:10px 0;border-color:#eee;">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center;">
        <div class="info-tile"><h3>{route.distance_km}</h3><p>Distance (km)</p></div>
        <div class="info-tile"><h3>{route.estimated_time_min}</h3><p>Est. Time (min)</p></div>
        <div class="info-tile"><h3>{route.hazard_count}</h3><p>Nearby Hazards</p></div>
        <div class="info-tile"><h3 style="color:{'#2ecc71' if route.risk_score<30 else '#e67e22' if route.risk_score<60 else '#e74c3c'}">{route.risk_score}%</h3><p>Risk Score</p></div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — Hazard Table
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_hazards:
    st.markdown("### Active Hazards")
    df = pd.DataFrame([h.to_dict() for h in hazards])
    display_cols = ["id", "name", "hazard_type", "severity", "description", "latitude", "longitude"]
    st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("ID", width="small"),
            "name": "Hazard",
            "hazard_type": "Type",
            "severity": "Severity",
            "description": "Details",
            "latitude": st.column_config.NumberColumn("Lat", format="%.4f"),
            "longitude": st.column_config.NumberColumn("Lon", format="%.4f"),
        },
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — Analytics
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_analytics:
    st.markdown("### Area Analytics")

    a1, a2 = st.columns(2)

    # Hazards by severity
    with a1:
        st.markdown("#### Hazards by Severity")
        sev_data = summary.get("by_severity", {})
        if sev_data:
            sev_df = pd.DataFrame(
                {"Severity": list(sev_data.keys()), "Count": list(sev_data.values())}
            )
            sev_order = ["low", "medium", "high", "critical"]
            sev_df["sort"] = sev_df["Severity"].apply(lambda s: sev_order.index(s) if s in sev_order else 99)
            sev_df = sev_df.sort_values("sort").drop(columns="sort")
            st.bar_chart(sev_df.set_index("Severity"))

    # Hazards by type
    with a2:
        st.markdown("#### Hazards by Type")
        type_data = summary.get("by_type", {})
        if type_data:
            type_df = pd.DataFrame(
                {"Type": list(type_data.keys()), "Count": list(type_data.values())}
            )
            st.bar_chart(type_df.set_index("Type"))

    st.markdown("---")

    # Route comparison
    st.markdown("#### Route Comparison")
    route_comp = pd.DataFrame(
        {
            "Route": [r.name for r in routes],
            "Distance (km)": [r.distance_km for r in routes],
            "Time (min)": [r.estimated_time_min for r in routes],
            "Hazards Nearby": [r.hazard_count for r in routes],
            "Risk Score (%)": [r.risk_score for r in routes],
            "Avg Speed (km/h)": [r.avg_speed_kmh for r in routes],
        }
    )
    st.dataframe(route_comp, use_container_width=True, hide_index=True)

    # Risk gauge visualisation
    st.markdown("---")
    st.markdown("#### Overall Area Risk Level")
    risk_label = (
        "🟢 Low" if risk_score < 25 else "🟡 Moderate" if risk_score < 50 else "🟠 High" if risk_score < 75 else "🔴 Critical"
    )
    st.progress(min(risk_score / 100, 1.0), text=f"Area Risk: {risk_score}% — {risk_label}")

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888; font-size:0.85rem;'>"
    "Smart Mobility Dashboard · Built with Streamlit & Folium · "
    f"{datetime.now().year}</p>",
    unsafe_allow_html=True,
)
