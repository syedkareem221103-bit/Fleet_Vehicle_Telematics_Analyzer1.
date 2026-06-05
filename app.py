import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from geopy.distance import geodesic

st.set_page_config(
    page_title="Fleet Vehicle Telematics Analyzer",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Fleet Vehicle Telematics Analyzer")

# Load Data
df = pd.read_csv("data/logistics_dataset.csv")

# -------------------------
# DATA PREPARATION
# -------------------------

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Create Vehicle IDs
df["Vehicle_ID"] = (
    "TRUCK_" +
    (df.index % 25 + 1).astype(str)
)

df = df.sort_values(
    ["Vehicle_ID", "timestamp"]
)

# Time Delta
df["Time_Delta_Hours"] = (
    df.groupby("Vehicle_ID")["timestamp"]
      .diff()
      .dt.total_seconds()
      .div(3600)
)

# Previous Coordinates
df["Prev_Lat"] = (
    df.groupby("Vehicle_ID")
    ["vehicle_gps_latitude"]
    .shift(1)
)

df["Prev_Lon"] = (
    df.groupby("Vehicle_ID")
    ["vehicle_gps_longitude"]
    .shift(1)
)

# Distance Calculation
def calc_distance(row):
    try:
        return geodesic(
            (row["Prev_Lat"], row["Prev_Lon"]),
            (
                row["vehicle_gps_latitude"],
                row["vehicle_gps_longitude"]
            )
        ).km
    except:
        return 0

df["Distance_KM"] = df.apply(
    calc_distance,
    axis=1
)

# Speed Estimation
df["Speed_KMH"] = (
    df["Distance_KM"] /
    df["Time_Delta_Hours"]
)

df["Speed_KMH"] = (
    df["Speed_KMH"]
    .replace([np.inf, -np.inf], 0)
    .fillna(0)
)

# Sidebar
st.sidebar.header("⚙ Fleet Controls")

vehicle = st.sidebar.selectbox(
    "Select Vehicle",
    sorted(df["Vehicle_ID"].unique())
)

idling_threshold = st.sidebar.slider(
    "Fuel Threshold",
    0.1,
    5.0,
    0.5
)

vehicle_df = df[
    df["Vehicle_ID"] == vehicle
]

# -------------------------
# IDLING DETECTION
# -------------------------

vehicle_df["Is_Idling"] = (
    (vehicle_df["Speed_KMH"] < 5)
    &
    (vehicle_df["fuel_consumption_rate"]
     > idling_threshold)
)

# KPIs

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Fuel Used",
    round(
        vehicle_df["fuel_consumption_rate"].sum(),
        2
    )
)

c2.metric(
    "Average Speed",
    round(
        vehicle_df["Speed_KMH"].mean(),
        2
    )
)

c3.metric(
    "Idling Events",
    int(
        vehicle_df["Is_Idling"].sum()
    )
)

c4.metric(
    "Route Distance",
    round(
        vehicle_df["Distance_KM"].sum(),
        2
    )
)

# -------------------------
# MAP
# -------------------------

st.subheader("🗺 Fleet Route Map")

st.map(
    vehicle_df[
        [
            "vehicle_gps_latitude",
            "vehicle_gps_longitude"
        ]
    ]
)

# -------------------------
# SPEED ANALYSIS
# -------------------------

st.subheader("📈 Speed Trend")

fig = px.line(
    vehicle_df,
    x="timestamp",
    y="Speed_KMH"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------
# FUEL ANALYSIS
# -------------------------

st.subheader("⛽ Fuel Consumption")

fuel_fig = px.histogram(
    vehicle_df,
    x="fuel_consumption_rate",
    nbins=30
)

st.plotly_chart(
    fuel_fig,
    use_container_width=True
)

# -------------------------
# DRIVER SCORECARD
# -------------------------

driver_scores = (
    df.groupby("Vehicle_ID")
    .agg(
        Fuel_Waste=(
            "fuel_consumption_rate",
            "sum"
        ),
        Avg_Speed=(
            "Speed_KMH",
            "mean"
        ),
        Driver_Score=(
            "driver_behavior_score",
            "mean"
        )
    )
    .reset_index()
)

driver_scores = (
    driver_scores
    .sort_values("Fuel_Waste")
)

st.subheader(
    "🏆 Driver Efficiency Ranking"
)

st.dataframe(
    driver_scores,
    use_container_width=True
)

# -------------------------
# INSIGHTS
# -------------------------

st.subheader("🔍 AI Insights")

fuel_waste = (
    vehicle_df["fuel_consumption_rate"]
    .sum()
)

idle_count = (
    vehicle_df["Is_Idling"]
    .sum()
)

if idle_count > 50:
    st.error(
        "High idling detected."
    )
else:
    st.success(
        "Vehicle operating efficiently."
    )

st.info(
    f"""
    Fuel Consumed : {fuel_waste:.2f}

    Idling Events : {idle_count}

    Avg Speed : {vehicle_df['Speed_KMH'].mean():.2f}
    """
)
