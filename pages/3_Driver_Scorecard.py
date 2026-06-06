import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from geopy.distance import geodesic

st.set_page_config(
    page_title="Driver Scorecard",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Driver Performance Scorecard")
st.markdown(
    "Analyze driver efficiency, safety, fuel economy, and operational performance."
)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
    "data/dynamic_supply_chain_logistics_dataset.csv"
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

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

    # Time Delta

    df["Time_Delta_Hours"] = (
        df.groupby("Vehicle_ID")
        ["timestamp"]
        .diff()
        .dt.total_seconds()
        / 3600
    )

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

# ------------------------------------------------
# DRIVER SCORE GENERATION
# ------------------------------------------------

driver_df = (
    df.groupby("Vehicle_ID")
    .agg(
        Total_Distance=(
            "Distance_KM",
            "sum"
        ),
        Avg_Speed=(
            "Speed_KMH",
            "mean"
        ),
        Fuel_Usage=(
            "fuel_consumption_rate",
            "sum"
        )
    )
    .reset_index()
)

# Create synthetic scores

driver_df["Driver_Behavior"] = (
    driver_df["Avg_Speed"] / driver_df["Avg_Speed"].max()
) * 100

driver_df["Risk_Score"] = (
    driver_df["Fuel_Usage"] / driver_df["Fuel_Usage"].max()
) * 100

# ------------------------------------------------
# CALCULATED SCORES
# ------------------------------------------------

driver_df["Fuel_Efficiency_Score"] = (
    100 -
    (
        driver_df["Fuel_Usage"]
        /
        driver_df["Fuel_Usage"].max()
    ) * 100
)

driver_df["Safety_Score"] = (
    100 -
    (
        driver_df["Risk_Score"]
        /
        driver_df["Risk_Score"].max()
    ) * 100
)

driver_df["Performance_Score"] = (
      driver_df["Driver_Behavior"] * 0.40
    + driver_df["Fuel_Efficiency_Score"] * 0.30
    + driver_df["Safety_Score"] * 0.30
)

driver_df["Performance_Score"] = (
    driver_df["Performance_Score"]
    .round(2)
)

driver_df["Rank"] = (
    driver_df["Performance_Score"]
    .rank(
        ascending=False,
        method="dense"
    )
    .astype(int)
)

driver_df = driver_df.sort_values(
    "Performance_Score",
    ascending=False
)

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

st.sidebar.header("⚙ Driver Selection")

selected_driver = st.sidebar.selectbox(
    "Choose Driver / Vehicle",
    ["All Drivers"] +
    list(driver_df["Vehicle_ID"])
)

if selected_driver != "All Drivers":

    selected_data = driver_df[
        driver_df["Vehicle_ID"]
        == selected_driver
    ]

else:

    selected_data = driver_df

# ------------------------------------------------
# KPI CARDS
# ------------------------------------------------

best_driver = driver_df.iloc[0]

avg_score = round(
    driver_df["Performance_Score"].mean(),
    2
)

avg_safety = round(
    driver_df["Safety_Score"].mean(),
    2
)

avg_fuel_efficiency = round(
    driver_df["Fuel_Efficiency_Score"].mean(),
    2
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🏆 Top Driver",
    best_driver["Vehicle_ID"]
)

c2.metric(
    "⭐ Avg Score",
    avg_score
)

c3.metric(
    "🛡 Avg Safety",
    avg_safety
)

c4.metric(
    "⛽ Avg Fuel Efficiency",
    avg_fuel_efficiency
)

st.divider()

# ------------------------------------------------
# LEADERBOARD
# ------------------------------------------------

st.subheader("🏆 Driver Leaderboard")

leaderboard = driver_df[
    [
        "Rank",
        "Vehicle_ID",
        "Performance_Score",
        "Safety_Score",
        "Fuel_Efficiency_Score",
        "Driver_Behavior"
    ]
]

st.dataframe(
    leaderboard,
    use_container_width=True
)

# ------------------------------------------------
# PERFORMANCE BAR CHART
# ------------------------------------------------

st.subheader("📊 Driver Performance Scores")

fig1 = px.bar(
    driver_df,
    x="Vehicle_ID",
    y="Performance_Score",
    color="Performance_Score",
    text="Rank"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ------------------------------------------------
# SAFETY ANALYSIS
# ------------------------------------------------

st.subheader("🛡 Safety Score Analysis")

fig2 = px.bar(
    driver_df,
    x="Vehicle_ID",
    y="Safety_Score",
    color="Safety_Score"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ------------------------------------------------
# FUEL EFFICIENCY ANALYSIS
# ------------------------------------------------

st.subheader("⛽ Fuel Efficiency Ranking")

fig3 = px.bar(
    driver_df,
    x="Vehicle_ID",
    y="Fuel_Efficiency_Score",
    color="Fuel_Efficiency_Score"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ------------------------------------------------
# RISK SCORE
# ------------------------------------------------

st.subheader("⚠ Risk Score Distribution")

fig4 = px.histogram(
    driver_df,
    x="Risk_Score",
    nbins=20
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# ------------------------------------------------
# SCATTER ANALYSIS
# ------------------------------------------------

st.subheader("📈 Fuel Usage vs Safety")

fig5 = px.scatter(
    driver_df,
    x="Fuel_Usage",
    y="Safety_Score",
    size="Performance_Score",
    color="Performance_Score",
    hover_name="Vehicle_ID"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# ------------------------------------------------
# RADAR CHART
# ------------------------------------------------

st.subheader("🎯 Driver Comparison")

compare_driver = st.selectbox(
    "Compare Driver",
    driver_df["Vehicle_ID"]
)

compare_data = driver_df[
    driver_df["Vehicle_ID"]
    == compare_driver
]

radar_df = pd.DataFrame({
    "Metric": [
        "Performance",
        "Safety",
        "Fuel Efficiency",
        "Behavior"
    ],
    "Score": [
        compare_data[
            "Performance_Score"
        ].values[0],
        compare_data[
            "Safety_Score"
        ].values[0],
        compare_data[
            "Fuel_Efficiency_Score"
        ].values[0],
        compare_data[
            "Driver_Behavior"
        ].values[0]
    ]
})

fig6 = px.line_polar(
    radar_df,
    r="Score",
    theta="Metric",
    line_close=True
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# ------------------------------------------------
# TOP 10 DRIVERS
# ------------------------------------------------

st.subheader("🥇 Top 10 Drivers")

top10 = driver_df.head(10)

st.dataframe(
    top10[
        [
            "Rank",
            "Vehicle_ID",
            "Performance_Score",
            "Safety_Score"
        ]
    ],
    use_container_width=True
)

# ------------------------------------------------
# LOWEST PERFORMERS
# ------------------------------------------------

st.subheader("🚨 Drivers Requiring Attention")

bottom5 = driver_df.tail(5)

st.dataframe(
    bottom5[
        [
            "Rank",
            "Vehicle_ID",
            "Performance_Score",
            "Risk_Score"
        ]
    ],
    use_container_width=True
)

# ------------------------------------------------
# SCORE DISTRIBUTION
# ------------------------------------------------

st.subheader("📉 Performance Score Distribution")

fig7 = px.histogram(
    driver_df,
    x="Performance_Score",
    nbins=20
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

# ------------------------------------------------
# AI INSIGHTS
# ------------------------------------------------

st.subheader("🤖 Driver Insights")

top_driver = driver_df.iloc[0]
worst_driver = driver_df.iloc[-1]

st.success(
    f"""
    🏆 Best Driver: {top_driver['Vehicle_ID']}

    Performance Score: {top_driver['Performance_Score']:.2f}

    Safety Score: {top_driver['Safety_Score']:.2f}
    """
)

st.error(
    f"""
    🚨 Driver Requiring Coaching: {worst_driver['Vehicle_ID']}

    Performance Score: {worst_driver['Performance_Score']:.2f}

    Risk Score: {worst_driver['Risk_Score']:.2f}
    """
)

st.info(
    f"""
    Fleet Average Performance Score : {avg_score}

    Fleet Average Safety Score : {avg_safety}

    Fleet Average Fuel Efficiency : {avg_fuel_efficiency}

    Total Drivers Evaluated : {len(driver_df)}
    """
)

st.markdown("---")

st.markdown(
"""
### Recommendations

✅ Reward top-performing drivers.

✅ Provide coaching to high-risk drivers.

✅ Reduce harsh driving behavior.

✅ Improve route planning.

✅ Monitor fuel consumption trends.

✅ Conduct monthly driver performance reviews.
"""
)
