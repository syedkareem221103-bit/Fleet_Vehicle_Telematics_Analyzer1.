import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from geopy.distance import geodesic

st.set_page_config(
    page_title="Idling Analysis",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Fleet Idling Analysis Dashboard")
st.markdown(
    "Identify fuel waste caused by engine idling and analyze vehicle efficiency."
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
    "data/dynamic_supply_chain_logistics_dataset.csv"
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Generate Vehicle IDs
    df["Vehicle_ID"] = (
        "TRUCK_" +
        ((df.index % 25) + 1).astype(str)
    )

    df = df.sort_values(
        ["Vehicle_ID", "timestamp"]
    )

    # Previous GPS Coordinates
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

    # Speed Calculation
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

st.sidebar.header("⚙️ Idling Controls")

vehicle = st.sidebar.selectbox(
    "Select Vehicle",
    ["All Vehicles"] +
    sorted(df["Vehicle_ID"].unique())
)

idling_threshold = st.sidebar.slider(
    "Fuel Consumption Threshold",
    min_value=0.1,
    max_value=5.0,
    value=0.5,
    step=0.1
)

speed_limit = st.sidebar.slider(
    "Idling Speed Limit (KM/H)",
    min_value=0,
    max_value=10,
    value=5
)

if vehicle != "All Vehicles":

    filtered_df = df[
        df["Vehicle_ID"] == vehicle
    ]

else:

    filtered_df = df.copy()

# ---------------------------------------------------
# IDLING DETECTION
# ---------------------------------------------------

filtered_df["Is_Idling"] = (
    (filtered_df["Speed_KMH"] <= speed_limit)
    &
    (
        filtered_df[
            "fuel_consumption_rate"
        ]
        > idling_threshold
    )
)

# ---------------------------------------------------
# FUEL WASTE
# ---------------------------------------------------

filtered_df["Fuel_Wasted"] = np.where(
    filtered_df["Is_Idling"],
    filtered_df["fuel_consumption_rate"],
    0
)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_idling_events = int(
    filtered_df["Is_Idling"].sum()
)

total_fuel_wasted = round(
    filtered_df["Fuel_Wasted"].sum(),
    2
)

avg_speed = round(
    filtered_df["Speed_KMH"].mean(),
    2
)

max_idle_vehicle = "N/A"

if vehicle == "All Vehicles":

    idle_vehicle_df = (
        filtered_df.groupby("Vehicle_ID")
        ["Fuel_Wasted"]
        .sum()
        .reset_index()
    )

    max_idle_vehicle = (
        idle_vehicle_df
        .sort_values(
            "Fuel_Wasted",
            ascending=False
        )
        .iloc[0]["Vehicle_ID"]
    )

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🛑 Idling Events",
    total_idling_events
)

c2.metric(
    "⛽ Fuel Wasted",
    f"{total_fuel_wasted:.2f} L"
)

c3.metric(
    "⚡ Avg Speed",
    f"{avg_speed:.2f} KM/H"
)

c4.metric(
    "🚛 Worst Vehicle",
    max_idle_vehicle
)

st.divider()

# ---------------------------------------------------
# IDLING MAP
# ---------------------------------------------------

st.subheader("🗺️ Idling Hotspots")

idle_locations = filtered_df[
    filtered_df["Is_Idling"] == True
]

if len(idle_locations) > 0:

    map_df = idle_locations.rename(
    columns={
        "vehicle_gps_latitude": "lat",
        "vehicle_gps_longitude": "lon"
    }
)

st.map(
    map_df[
        ["lat", "lon"]
    ]
)

else:

    st.success(
        "No idling locations detected."
    )

# ---------------------------------------------------
# IDLING TIMELINE
# ---------------------------------------------------

st.subheader("📈 Idling Events Over Time")

idle_time_fig = px.scatter(
    idle_locations,
    x="timestamp",
    y="fuel_consumption_rate",
    color="Vehicle_ID",
    size="fuel_consumption_rate",
    title="Fuel Waste During Idling"
)

st.plotly_chart(
    idle_time_fig,
    use_container_width=True
)

# ---------------------------------------------------
# IDLING VEHICLE RANKING
# ---------------------------------------------------

st.subheader("🏆 Vehicle Fuel Waste Ranking")

ranking_df = (
    filtered_df.groupby("Vehicle_ID")
    .agg(
        Total_Fuel_Wasted=(
            "Fuel_Wasted",
            "sum"
        ),
        Total_Idling_Events=(
            "Is_Idling",
            "sum"
        ),
        Avg_Speed=(
            "Speed_KMH",
            "mean"
        )
    )
    .reset_index()
)

ranking_df = ranking_df.sort_values(
    "Total_Fuel_Wasted",
    ascending=False
)

st.dataframe(
    ranking_df,
    use_container_width=True
)

# ---------------------------------------------------
# BAR CHART
# ---------------------------------------------------

st.subheader("📊 Fuel Waste by Vehicle")

fuel_chart = px.bar(
    ranking_df,
    x="Vehicle_ID",
    y="Total_Fuel_Wasted",
    color="Total_Fuel_Wasted",
    title="Fuel Wasted Due To Idling"
)

st.plotly_chart(
    fuel_chart,
    use_container_width=True
)

# ---------------------------------------------------
# PIE CHART
# ---------------------------------------------------

st.subheader("🥧 Fuel Waste Distribution")

top10 = ranking_df.head(10)

pie_chart = px.pie(
    top10,
    names="Vehicle_ID",
    values="Total_Fuel_Wasted",
    title="Top Fuel-Wasting Vehicles"
)

st.plotly_chart(
    pie_chart,
    use_container_width=True
)

# ---------------------------------------------------
# SPEED VS FUEL
# ---------------------------------------------------

st.subheader("⚡ Speed vs Fuel Consumption")

scatter_fig = px.scatter(
    filtered_df,
    x="Speed_KMH",
    y="fuel_consumption_rate",
    color="Is_Idling",
    hover_data=["Vehicle_ID"],
    title="Speed vs Fuel Usage"
)

st.plotly_chart(
    scatter_fig,
    use_container_width=True
)

# ---------------------------------------------------
# HEATMAP TABLE
# ---------------------------------------------------

st.subheader("🔥 Top Idling Records")

top_idle_records = (
    idle_locations[
        [
            "Vehicle_ID",
            "timestamp",
            "Speed_KMH",
            "fuel_consumption_rate",
            "Fuel_Wasted"
        ]
    ]
    .sort_values(
        "Fuel_Wasted",
        ascending=False
    )
)

st.dataframe(
    top_idle_records.head(100),
    use_container_width=True
)

# ---------------------------------------------------
# AI INSIGHTS
# ---------------------------------------------------

st.subheader("🤖 Fleet Insights")

if total_idling_events > 100:

    st.error(
        "High idling frequency detected. Immediate intervention recommended."
    )

elif total_idling_events > 50:

    st.warning(
        "Moderate idling behavior observed."
    )

else:

    st.success(
        "Fleet idling levels are within acceptable limits."
    )

if len(ranking_df) > 0:

    worst_vehicle = ranking_df.iloc[0]

    st.info(
        f"""
        🚛 Highest Fuel Waste Vehicle: {worst_vehicle['Vehicle_ID']}

        ⛽ Fuel Wasted: {worst_vehicle['Total_Fuel_Wasted']:.2f} Liters

        🛑 Idling Events: {int(worst_vehicle['Total_Idling_Events'])}

        ⚡ Average Speed: {worst_vehicle['Avg_Speed']:.2f} KM/H
        """
    )

st.markdown("---")

st.markdown(
    """
    ### Recommendations

    ✅ Reduce unnecessary engine running.

    ✅ Enable automatic engine shutdown policies.

    ✅ Monitor drivers with excessive idle time.

    ✅ Optimize loading/unloading operations.

    ✅ Use route planning to reduce waiting time.
    """
)
