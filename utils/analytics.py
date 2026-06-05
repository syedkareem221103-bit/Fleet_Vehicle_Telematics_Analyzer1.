import pandas as pd
import numpy as np


# ---------------------------------------------------
# FLEET KPIs
# ---------------------------------------------------

def fleet_kpis(df):

    """
    Generate overall fleet KPIs.
    """

    total_vehicles = df["Vehicle_ID"].nunique()

    total_distance = round(
        df["Distance_KM"].sum(),
        2
    )

    average_speed = round(
        df["Speed_KMH"].mean(),
        2
    )

    total_fuel = round(
        df["fuel_consumption_rate"].sum(),
        2
    )

    total_idling = int(
        df["Is_Idling"].sum()
    )

    return {
        "Total_Vehicles": total_vehicles,
        "Total_Distance": total_distance,
        "Average_Speed": average_speed,
        "Total_Fuel": total_fuel,
        "Total_Idling": total_idling
    }


# ---------------------------------------------------
# VEHICLE SUMMARY
# ---------------------------------------------------

def vehicle_summary(df):

    """
    Vehicle level analytics.
    """

    summary = (
        df.groupby("Vehicle_ID")
        .agg(
            Total_Distance=(
                "Distance_KM",
                "sum"
            ),
            Average_Speed=(
                "Speed_KMH",
                "mean"
            ),
            Fuel_Used=(
                "fuel_consumption_rate",
                "sum"
            ),
            Idling_Events=(
                "Is_Idling",
                "sum"
            )
        )
        .reset_index()
    )

    return summary


# ---------------------------------------------------
# DRIVER SCORECARD
# ---------------------------------------------------

def driver_scorecard(df):

    """
    Driver ranking analysis.
    """

    driver_df = (
        df.groupby("Vehicle_ID")
        .agg(
            Total_Distance=(
                "Distance_KM",
                "sum"
            ),
            Fuel_Usage=(
                "fuel_consumption_rate",
                "sum"
            ),
            Driver_Behavior=(
                "driver_behavior_score",
                "mean"
            ),
            Risk_Score=(
                "risk_score",
                "mean"
            )
        )
        .reset_index()
    )

    driver_df["Fuel_Efficiency"] = (
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
        + driver_df["Fuel_Efficiency"] * 0.30
        + driver_df["Safety_Score"] * 0.30
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

    return driver_df


# ---------------------------------------------------
# IDLING ANALYSIS
# ---------------------------------------------------

def idling_analysis(df):

    """
    Analyze idling behavior.
    """

    idle_df = (
        df.groupby("Vehicle_ID")
        .agg(
            Total_Idling=(
                "Is_Idling",
                "sum"
            ),
            Fuel_Wasted=(
                "Fuel_Wasted",
                "sum"
            ),
            Avg_Speed=(
                "Speed_KMH",
                "mean"
            )
        )
        .reset_index()
    )

    idle_df = idle_df.sort_values(
        "Fuel_Wasted",
        ascending=False
    )

    return idle_df


# ---------------------------------------------------
# ROUTE EFFICIENCY
# ---------------------------------------------------

def route_efficiency(df):

    """
    Route efficiency metrics.
    """

    route_df = (
        df.groupby("Vehicle_ID")
        .agg(
            Total_Distance=(
                "Distance_KM",
                "sum"
            ),
            Fuel_Used=(
                "fuel_consumption_rate",
                "sum"
            ),
            Avg_Speed=(
                "Speed_KMH",
                "mean"
            )
        )
        .reset_index()
    )

    route_df["Route_Efficiency"] = (
        route_df["Total_Distance"]
        /
        (
            route_df["Fuel_Used"]
            + 1
        )
    ) * 100

    route_df = route_df.sort_values(
        "Route_Efficiency",
        ascending=False
    )

    return route_df


# ---------------------------------------------------
# ROUTE ANOMALIES
# ---------------------------------------------------

def route_anomalies(
    route_df,
    threshold=10
):

    """
    Detect unusual route distances.
    """

    avg_distance = (
        route_df["Total_Distance"]
        .mean()
    )

    route_df["Anomaly"] = np.where(
        route_df["Total_Distance"]
        >
        (
            avg_distance +
            threshold
        ),
        "High",
        "Normal"
    )

    return route_df


# ---------------------------------------------------
# FUEL ANALYTICS
# ---------------------------------------------------

def fuel_analytics(df):

    """
    Fuel consumption metrics.
    """

    fuel_df = (
        df.groupby("Vehicle_ID")
        .agg(
            Fuel_Used=(
                "fuel_consumption_rate",
                "sum"
            ),
            Avg_Fuel_Consumption=(
                "fuel_consumption_rate",
                "mean"
            )
        )
        .reset_index()
    )

    fuel_df = fuel_df.sort_values(
        "Fuel_Used",
        ascending=False
    )

    return fuel_df


# ---------------------------------------------------
# RISK ANALYTICS
# ---------------------------------------------------

def risk_analytics(df):

    """
    Risk score analytics.
    """

    risk_df = (
        df.groupby("Vehicle_ID")
        .agg(
            Avg_Risk=(
                "risk_score",
                "mean"
            ),
            Max_Risk=(
                "risk_score",
                "max"
            ),
            Min_Risk=(
                "risk_score",
                "min"
            )
        )
        .reset_index()
    )

    return risk_df


# ---------------------------------------------------
# TOP PERFORMERS
# ---------------------------------------------------

def top_performers(
    driver_df,
    top_n=10
):

    """
    Best performing drivers.
    """

    return driver_df.head(top_n)


# ---------------------------------------------------
# LOW PERFORMERS
# ---------------------------------------------------

def low_performers(
    driver_df,
    count=5
):

    """
    Lowest performing drivers.
    """

    return driver_df.tail(count)


# ---------------------------------------------------
# HOTSPOT LOCATIONS
# ---------------------------------------------------

def idling_hotspots(df):

    """
    Extract GPS locations
    where idling occurred.
    """

    hotspots = df[
        df["Is_Idling"] == True
    ]

    return hotspots[
        [
            "Vehicle_ID",
            "vehicle_gps_latitude",
            "vehicle_gps_longitude",
            "Fuel_Wasted"
        ]
    ]


# ---------------------------------------------------
# EXECUTIVE SUMMARY
# ---------------------------------------------------

def executive_summary(df):

    """
    Generate dashboard summary.
    """

    fleet = fleet_kpis(df)

    return {
        "Fleet_Size":
            fleet["Total_Vehicles"],

        "Distance":
            fleet["Total_Distance"],

        "Fuel":
            fleet["Total_Fuel"],

        "Average_Speed":
            fleet["Average_Speed"],

        "Idling":
            fleet["Total_Idling"]
    }


# ---------------------------------------------------
# AI INSIGHTS
# ---------------------------------------------------

def ai_insights(df):

    """
    Generate rule-based insights.
    """

    insights = []

    avg_speed = df["Speed_KMH"].mean()

    total_idle = df["Is_Idling"].sum()

    total_fuel = (
        df["fuel_consumption_rate"]
        .sum()
    )

    if avg_speed < 20:

        insights.append(
            "Low fleet speed detected."
        )

    if total_idle > 100:

        insights.append(
            "Excessive idling observed."
        )

    if total_fuel > 1000:

        insights.append(
            "High fuel consumption detected."
        )

    if len(insights) == 0:

        insights.append(
            "Fleet operating efficiently."
        )

    return insights


# ---------------------------------------------------
# EXPORT REPORT
# ---------------------------------------------------

def export_summary(df):

    """
    Export analytics report.
    """

    report = {
        "Total Vehicles":
            df["Vehicle_ID"].nunique(),

        "Total Distance":
            round(
                df["Distance_KM"].sum(),
                2
            ),

        "Total Fuel":
            round(
                df["fuel_consumption_rate"].sum(),
                2
            ),

        "Average Speed":
            round(
                df["Speed_KMH"].mean(),
                2
            ),

        "Idling Events":
            int(
                df["Is_Idling"].sum()
            )
    }

    return pd.DataFrame(
        report.items(),
        columns=["Metric", "Value"]
    )
