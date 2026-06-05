import pandas as pd
import numpy as np
from geopy.distance import geodesic


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

def load_data(file_path):

    """
    Load logistics dataset and perform
    basic cleaning.
    """

    df = pd.read_csv(file_path)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    return df


# ---------------------------------------------------
# CREATE VEHICLE IDs
# ---------------------------------------------------

def generate_vehicle_ids(
        df,
        total_vehicles=25
):

    """
    Generate synthetic vehicle IDs.
    """

    df["Vehicle_ID"] = (
        "TRUCK_" +
        (
            (df.index % total_vehicles) + 1
        ).astype(str)
    )

    return df


# ---------------------------------------------------
# SORT DATA
# ---------------------------------------------------

def sort_data(df):

    """
    Sort by vehicle and timestamp.
    """

    return df.sort_values(
        ["Vehicle_ID", "timestamp"]
    )


# ---------------------------------------------------
# TIME DELTA
# ---------------------------------------------------

def calculate_time_delta(df):

    """
    Calculate time difference
    between GPS pings.
    """

    df["Time_Delta_Hours"] = (
        df.groupby("Vehicle_ID")
        ["timestamp"]
        .diff()
        .dt.total_seconds()
        / 3600
    )

    return df


# ---------------------------------------------------
# PREVIOUS COORDINATES
# ---------------------------------------------------

def create_previous_coordinates(df):

    """
    Create previous GPS locations.
    """

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

    return df


# ---------------------------------------------------
# DISTANCE CALCULATION
# ---------------------------------------------------

def calculate_distance(df):

    """
    Calculate distance travelled
    between GPS points.
    """

    def distance(row):

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
        distance,
        axis=1
    )

    return df


# ---------------------------------------------------
# SPEED CALCULATION
# ---------------------------------------------------

def calculate_speed(df):

    """
    Estimate vehicle speed.
    """

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


# ---------------------------------------------------
# IDLING DETECTION
# ---------------------------------------------------

def detect_idling(
        df,
        speed_threshold=5,
        fuel_threshold=0.5
):

    """
    Detect idling vehicles.
    """

    df["Is_Idling"] = (
        (
            df["Speed_KMH"]
            <= speed_threshold
        )
        &
        (
            df["fuel_consumption_rate"]
            > fuel_threshold
        )
    )

    return df


# ---------------------------------------------------
# FUEL WASTE
# ---------------------------------------------------

def calculate_fuel_waste(df):

    """
    Calculate wasted fuel during idling.
    """

    df["Fuel_Wasted"] = np.where(
        df["Is_Idling"],
        df["fuel_consumption_rate"],
        0
    )

    return df


# ---------------------------------------------------
# ROUTE EFFICIENCY
# ---------------------------------------------------

def calculate_route_efficiency(df):

    """
    Vehicle route efficiency score.
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

    return route_df


# ---------------------------------------------------
# DRIVER SCORE
# ---------------------------------------------------

def calculate_driver_score(df):

    """
    Generate driver scorecard.
    """

    score_df = (
        df.groupby("Vehicle_ID")
        .agg(
            Distance=(
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

    score_df["Fuel_Efficiency"] = (
        100 -
        (
            score_df["Fuel_Usage"]
            /
            score_df["Fuel_Usage"].max()
        ) * 100
    )

    score_df["Safety_Score"] = (
        100 -
        (
            score_df["Risk_Score"]
            /
            score_df["Risk_Score"].max()
        ) * 100
    )

    score_df["Performance_Score"] = (
          score_df["Driver_Behavior"] * 0.4
        + score_df["Fuel_Efficiency"] * 0.3
        + score_df["Safety_Score"] * 0.3
    )

    return score_df


# ---------------------------------------------------
# COMPLETE PIPELINE
# ---------------------------------------------------

def preprocess_data(file_path):

    """
    Complete preprocessing pipeline.
    """

    df = load_data(file_path)

    df = generate_vehicle_ids(df)

    df = sort_data(df)

    df = calculate_time_delta(df)

    df = create_previous_coordinates(df)

    df = calculate_distance(df)

    df = calculate_speed(df)

    df = detect_idling(df)

    df = calculate_fuel_waste(df)

    return df


# ---------------------------------------------------
# TESTING
# ---------------------------------------------------

if __name__ == "__main__":

    dataset = preprocess_data(
        "data/logistics_dataset.csv"
    )

    print(dataset.head())

    print(
        "\nDataset Shape:",
        dataset.shape
    )
