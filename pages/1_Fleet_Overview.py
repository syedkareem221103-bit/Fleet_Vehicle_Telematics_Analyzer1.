import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from geopy.distance import geodesic

st.set_page_config(
    page_title="Fleet Overview",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Fleet Overview Dashboard")
st.markdown("Comprehensive monitoring of fleet operations, fuel usage, routes, and vehicle performance.")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/logistics_dataset.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Generate Vehicle IDs
    df["Vehicle_ID"] = (
        "TRUCK_" +
        ((df.index % 25) + 1).astype(str)
    )

    df = df.sort_values(
        ["Vehicle_ID", "timestamp"]
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

    # Time Delta
    df["Time_Delta_Hours"] = (
        df.groupby("Vehicle_ID")
        ["timestamp"]
        .diff()
        .dt.total_seconds()
        .div(3600)
    )

    # Distance Calculation
    def calculate_distance(row):
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
        calculate_distance,
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

    return df


df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("⚙ Fleet Filters")

vehicle_list = sorted(
    df["Vehicle_ID"].unique()
)

selected_vehicle = st.sidebar.selectbox(
    "Select Vehicle",
    ["All Vehicles"] + vehicle_list
)

if selected_vehicle != "All Vehicles":
    filtered_df = df[
        df["Vehicle_ID"] == selected_vehicle
    ]
else:
    filtered_df = df.copy()

# -----------------------------
# KPI SECTION
# -----------------------------
total_vehicles = df["Vehicle_ID"].nunique()

total_distance = round(
    filtered_df["Distance_KM"].sum(),
    2
)

avg_speed = round(
    filtered_df["Speed_KMH"].mean(),
    2
)

fuel_used = round(
    filtered_df["fuel_consumption_rate"].sum(),
    2
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🚚 Vehicles",
    total_vehicles
)

col2.metric(
    "🛣 Distance (KM)",
    total_distance
)

col3.metric(
    "⚡ Avg Speed",
    avg_speed
)

col4.metric(
    "⛽ Fuel Usage",
    fuel_used
)

st.divider()

# -----------------------------
# ROUTE MAP
# -----------------------------
st.subheader("🗺 Fleet GPS Route Tracking")

st.map(
    filtered_df[
        [
            "vehicle_gps_latitude",
            "vehicle_gps_longitude"
        ]
    ]
)

# -----------------------------
# VEHICLE DISTRIBUTION
# -----------------------------
st.subheader("🚛 Vehicle Activity Distribution")

vehicle_counts = (
    df["Vehicle_ID"]
    .value_counts()
    .reset_index()
)

vehicle_counts.columns = [
    "Vehicle",
    "Records"
]

fig_vehicle = px.bar(
    vehicle_counts,
    x="Vehicle",
    y="Records",
    title="Telemetry Records per Vehicle"
)

st.plotly_chart(
    fig_vehicle,
    use_container_width=True
)

# -----------------------------
# SPEED ANALYSIS
# -----------------------------
st.subheader("📈 Speed Trend Analysis")

speed_fig = px.line(
    filtered_df,
    x="timestamp",
    y="Speed_KMH",
    color="Vehicle_ID",
    title="Vehicle Speed Over Time"
)

st.plotly_chart(
    speed_fig,
    use_container_width=True
)

# -----------------------------
# FUEL CONSUMPTION
# -----------------------------
st.subheader("⛽ Fuel Consumption Trend")

fuel_fig = px.line(
    filtered_df,
    x="timestamp",
    y="fuel_consumption_rate",
    color="Vehicle_ID",
    title="Fuel Consumption Over Time"
)

st.plotly_chart(
    fuel_fig,
    use_container_width=True
)

# -----------------------------
# DISTANCE COVERED
# -----------------------------
st.subheader("🛣 Distance Covered by Vehicles")

distance_df = (
    df.groupby("Vehicle_ID")
    ["Distance_KM"]
    .sum()
    .reset_index()
)

distance_fig = px.bar(
    distance_df,
    x="Vehicle_ID",
    y="Distance_KM",
    color="Distance_KM",
    title="Distance Travelled by Vehicle"
)

st.plotly_chart(
    distance_fig,
    use_container_width=True
)

# -----------------------------
# DRIVER PERFORMANCE
# -----------------------------
st.subheader("🏆 Driver Performance Ranking")

driver_rank = (
    df.groupby("Vehicle_ID")
    .agg(
        Avg_Speed=("Speed_KMH", "mean"),
        Fuel_Usage=("fuel_consumption_rate", "sum"),
        Driver_Score=("driver_behavior_score", "mean")
    )
    .reset_index()
)

driver_rank = driver_rank.sort_values(
    "Driver_Score",
    ascending=False
)

st.dataframe(
    driver_rank,
    use_container_width=True
)

# -----------------------------
# RISK ANALYSIS
# -----------------------------
st.subheader("⚠ Risk Score Distribution")

risk_fig = px.histogram(
    df,
    x="risk_score",
    nbins=30,
    title="Risk Score Distribution"
)

st.plotly_chart(
    risk_fig,
    use_container_width=True
)

# -----------------------------
# TOP PERFORMING VEHICLES
# -----------------------------
st.subheader("🥇 Top Performing Vehicles")

top_vehicles = (
    driver_rank
    .sort_values(
        "Driver_Score",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    top_vehicles,
    use_container_width=True
)

# -----------------------------
# INSIGHTS SECTION
# -----------------------------
st.subheader("🤖 Fleet Insights")

highest_distance_vehicle = (
    distance_df.sort_values(
        "Distance_KM",
        ascending=False
    )
    .iloc[0]
)

highest_fuel_vehicle = (
    driver_rank.sort_values(
        "Fuel_Usage",
        ascending=False
    )
    .iloc[0]
)

st.success(
    f"🚛 Most Active Vehicle: {highest_distance_vehicle['Vehicle_ID']} "
    f"covered {highest_distance_vehicle['Distance_KM']:.2f} KM."
)

st.warning(
    f"⛽ Highest Fuel Consumption: {highest_fuel_vehicle['Vehicle_ID']} "
    f"used {highest_fuel_vehicle['Fuel_Usage']:.2f} liters."
)

st.info(
    f"""
    Fleet Summary:

    • Total Vehicles: {total_vehicles}

    • Total Distance Covered: {total_distance:.2f} KM

    • Average Fleet Speed: {avg_speed:.2f} KM/H

    • Total Fuel Usage: {fuel_used:.2f} Liters

    • Dashboard Status: Operational ✅
    """
)
