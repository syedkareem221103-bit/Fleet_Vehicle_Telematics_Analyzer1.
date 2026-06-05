import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from geopy.distance import geodesic

st.set_page_config(
    page_title="Route Efficiency Analysis",
    page_icon="🛣️",
    layout="wide"
)

st.title("🛣️ Route Efficiency & Optimization Dashboard")
st.markdown(
    "Analyze route performance, travel efficiency, route deviations, and fleet movement patterns."
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
    "data/dynamic_supply_chain_logistics_dataset.csv"
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # Create Vehicle IDs

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

    # Time Difference

    df["Time_Delta_Hours"] = (
        df.groupby("Vehicle_ID")
        ["timestamp"]
        .diff()
        .dt.total_seconds()
        / 3600
    )

    # Distance Calculation

    def calculate_distance(row):

        try:

            return geodesic(
                (
                    row["Prev_Lat"],
                    row["Prev_Lon"]
                ),
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

    # Speed

    df["Speed_KMH"] = (
        df["Distance_KM"]
        /
        df["Time_Delta_Hours"]
    )

    df["Speed_KMH"] = (
        df["Speed_KMH"]
        .replace(
            [np.inf, -np.inf],
            0
        )
        .fillna(0)
    )

    return df


df = load_data()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("⚙️ Route Controls")

vehicle = st.sidebar.selectbox(
    "Select Vehicle",
    ["All Vehicles"] +
    sorted(df["Vehicle_ID"].unique())
)

deviation_threshold = st.sidebar.slider(
    "Route Deviation Threshold (KM)",
    min_value=1,
    max_value=50,
    value=10
)

if vehicle != "All Vehicles":

    filtered_df = df[
        df["Vehicle_ID"] == vehicle
    ]

else:

    filtered_df = df.copy()

# ---------------------------------------------------
# ROUTE EFFICIENCY CALCULATION
# ---------------------------------------------------

route_summary = (
    filtered_df.groupby("Vehicle_ID")
    .agg(
        Total_Distance=(
            "Distance_KM",
            "sum"
        ),
        Avg_Speed=(
            "Speed_KMH",
            "mean"
        ),
        Fuel_Used=(
            "fuel_consumption_rate",
            "sum"
        )
    )
    .reset_index()
)

route_summary["Route_Efficiency"] = (
    route_summary["Total_Distance"]
    /
    (
        route_summary["Fuel_Used"] + 1
    )
) * 100

route_summary["Route_Efficiency"] = (
    route_summary["Route_Efficiency"]
    .round(2)
)

# ---------------------------------------------------
# ROUTE DEVIATION DETECTION
# ---------------------------------------------------

average_distance = (
    route_summary["Total_Distance"]
    .mean()
)

route_summary["Route_Deviation"] = np.where(
    route_summary["Total_Distance"]
    >
    (
        average_distance +
        deviation_threshold
    ),
    "High",
    "Normal"
)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_distance = round(
    filtered_df["Distance_KM"].sum(),
    2
)

avg_speed = round(
    filtered_df["Speed_KMH"].mean(),
    2
)

fuel_used = round(
    filtered_df[
        "fuel_consumption_rate"
    ].sum(),
    2
)

avg_efficiency = round(
    route_summary[
        "Route_Efficiency"
    ].mean(),
    2
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🛣 Total Distance",
    f"{total_distance:.2f} KM"
)

c2.metric(
    "⚡ Avg Speed",
    f"{avg_speed:.2f} KM/H"
)

c3.metric(
    "⛽ Fuel Used",
    f"{fuel_used:.2f} L"
)

c4.metric(
    "🎯 Avg Efficiency",
    avg_efficiency
)

st.divider()

# ---------------------------------------------------
# ROUTE MAP
# ---------------------------------------------------

st.subheader("🗺️ Fleet Route Tracking")

st.map(
    filtered_df[
        [
            "vehicle_gps_latitude",
            "vehicle_gps_longitude"
        ]
    ]
)

# ---------------------------------------------------
# DISTANCE LEADERBOARD
# ---------------------------------------------------

st.subheader("🏆 Distance Travelled Ranking")

distance_rank = (
    route_summary.sort_values(
        "Total_Distance",
        ascending=False
    )
)

st.dataframe(
    distance_rank,
    use_container_width=True
)

# ---------------------------------------------------
# ROUTE EFFICIENCY BAR CHART
# ---------------------------------------------------

st.subheader("📊 Route Efficiency Ranking")

fig1 = px.bar(
    route_summary,
    x="Vehicle_ID",
    y="Route_Efficiency",
    color="Route_Efficiency",
    title="Vehicle Route Efficiency"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ---------------------------------------------------
# DISTANCE ANALYSIS
# ---------------------------------------------------

st.subheader("🛣 Distance Covered")

fig2 = px.bar(
    route_summary,
    x="Vehicle_ID",
    y="Total_Distance",
    color="Total_Distance"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ---------------------------------------------------
# SPEED ANALYSIS
# ---------------------------------------------------

st.subheader("⚡ Speed Trend")

fig3 = px.line(
    filtered_df,
    x="timestamp",
    y="Speed_KMH",
    color="Vehicle_ID"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ---------------------------------------------------
# FUEL ANALYSIS
# ---------------------------------------------------

st.subheader("⛽ Fuel Usage Analysis")

fig4 = px.line(
    filtered_df,
    x="timestamp",
    y="fuel_consumption_rate",
    color="Vehicle_ID"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# ---------------------------------------------------
# SCATTER ANALYSIS
# ---------------------------------------------------

st.subheader("📈 Fuel vs Distance")

fig5 = px.scatter(
    route_summary,
    x="Fuel_Used",
    y="Total_Distance",
    size="Route_Efficiency",
    color="Route_Efficiency",
    hover_name="Vehicle_ID"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# ---------------------------------------------------
# DEVIATION ANALYSIS
# ---------------------------------------------------

st.subheader("🚨 Route Deviation Detection")

deviation_df = route_summary[
    route_summary["Route_Deviation"]
    == "High"
]

if len(deviation_df) > 0:

    st.dataframe(
        deviation_df,
        use_container_width=True
    )

else:

    st.success(
        "No route anomalies detected."
    )

# ---------------------------------------------------
# PIE CHART
# ---------------------------------------------------

st.subheader("🥧 Route Efficiency Distribution")

top10 = route_summary.head(10)

fig6 = px.pie(
    top10,
    names="Vehicle_ID",
    values="Route_Efficiency"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# ---------------------------------------------------
# HEATMAP TABLE
# ---------------------------------------------------

st.subheader("🔥 Best Performing Routes")

best_routes = (
    route_summary
    .sort_values(
        "Route_Efficiency",
        ascending=False
    )
)

st.dataframe(
    best_routes.head(20),
    use_container_width=True
)

# ---------------------------------------------------
# TOP & BOTTOM VEHICLES
# ---------------------------------------------------

st.subheader("🏆 Fleet Route Leaderboard")

top_vehicle = (
    route_summary
    .sort_values(
        "Route_Efficiency",
        ascending=False
    )
    .iloc[0]
)

bottom_vehicle = (
    route_summary
    .sort_values(
        "Route_Efficiency",
        ascending=True
    )
    .iloc[0]
)

col1, col2 = st.columns(2)

with col1:

    st.success(
        f"""
        🏆 Best Route

        Vehicle: {top_vehicle['Vehicle_ID']}

        Efficiency: {top_vehicle['Route_Efficiency']:.2f}
        """
    )

with col2:

    st.error(
        f"""
        🚨 Lowest Efficiency

        Vehicle: {bottom_vehicle['Vehicle_ID']}

        Efficiency: {bottom_vehicle['Route_Efficiency']:.2f}
        """
    )

# ---------------------------------------------------
# TIMELINE ANALYSIS
# ---------------------------------------------------

st.subheader("📅 Route Activity Timeline")

timeline = (
    filtered_df
    .groupby(
        filtered_df["timestamp"].dt.date
    )
    ["Distance_KM"]
    .sum()
    .reset_index()
)

timeline.columns = [
    "Date",
    "Distance_KM"
]

fig7 = px.line(
    timeline,
    x="Date",
    y="Distance_KM",
    markers=True
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

# ---------------------------------------------------
# AI INSIGHTS
# ---------------------------------------------------

st.subheader("🤖 Route Intelligence Insights")

st.info(
    f"""
    Average Route Efficiency : {avg_efficiency:.2f}

    Total Distance Covered : {total_distance:.2f} KM

    Average Fleet Speed : {avg_speed:.2f} KM/H

    Total Fuel Consumed : {fuel_used:.2f} Liters
    """
)

if avg_efficiency < 20:

    st.error(
        "Fleet route efficiency is below recommended levels."
    )

elif avg_efficiency < 50:

    st.warning(
        "Moderate route efficiency detected."
    )

else:

    st.success(
        "Fleet routes are operating efficiently."
    )

st.markdown("---")

st.markdown("""
### Recommendations

✅ Optimize delivery schedules

✅ Minimize route deviations

✅ Reduce unnecessary detours

✅ Improve GPS route planning

✅ Monitor inefficient vehicles

✅ Use predictive route optimization

✅ Reduce idle and waiting time

✅ Improve fuel-efficient driving practices
""")
