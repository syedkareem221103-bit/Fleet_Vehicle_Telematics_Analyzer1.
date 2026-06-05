import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------------------------
# BASIC STREAMLIT MAP
# ---------------------------------------------------

def show_vehicle_map(df):

    """
    Display GPS points using Streamlit map.
    """

    if len(df) > 0:

        map_df = df.rename(
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

        st.warning(
            "No GPS data available."
        )


# ---------------------------------------------------
# IDLING HOTSPOT MAP
# ---------------------------------------------------

def show_idling_hotspots(df):
def show_idling_hotspots(df):

    """
    Show locations where idling occurs.
    """

    idle_df = df[
        df["Is_Idling"] == True
    ]

    if len(idle_df) > 0:

        map_df = idle_df.rename(
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
            "No idling hotspots detected."
        )


# ---------------------------------------------------
# VEHICLE ROUTE MAP
# ---------------------------------------------------

def route_map(df, vehicle_id):

    """
    Show GPS route for one vehicle.
    """

    route_df = df[
        df["Vehicle_ID"]
        == vehicle_id
    ]

    if len(route_df) == 0:

        st.warning(
            "No route data found."
        )

        return

    map_df = route_df.rename(
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


# ---------------------------------------------------
# PLOTLY GPS SCATTER MAP
# ---------------------------------------------------

def scatter_geo_map(df):

    """
    Interactive GPS scatter map.
    """

    fig = px.scatter_mapbox(
        df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        hover_name="Vehicle_ID",
        zoom=3,
        height=600
    )

    fig.update_layout(
        mapbox_style="open-street-map"
    )

    return fig


# ---------------------------------------------------
# ROUTE VISUALIZATION
# ---------------------------------------------------

def plot_route_path(df):

    """
    Draw route path lines.
    """

    fig = go.Figure()

    for vehicle in df["Vehicle_ID"].unique():

        vehicle_df = df[
            df["Vehicle_ID"]
            == vehicle
        ]

        fig.add_trace(
            go.Scattermapbox(
                lat=vehicle_df[
                    "vehicle_gps_latitude"
                ],
                lon=vehicle_df[
                    "vehicle_gps_longitude"
                ],
                mode="lines+markers",
                name=vehicle
            )
        )

    fig.update_layout(
        mapbox_style="open-street-map",
        height=700,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )
    )

    return fig


# ---------------------------------------------------
# HOTSPOT ANALYSIS
# ---------------------------------------------------

def hotspot_map(df):

    """
    Display high fuel waste hotspots.
    """

    if "Fuel_Wasted" not in df.columns:

        return None

    hotspot_df = df[
        df["Fuel_Wasted"] > 0
    ]

    if len(hotspot_df) == 0:

        return None

    fig = px.scatter_mapbox(
        hotspot_df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        size="Fuel_Wasted",
        color="Fuel_Wasted",
        hover_name="Vehicle_ID",
        zoom=3,
        height=600
    )

    fig.update_layout(
        mapbox_style="open-street-map"
    )

    return fig


# ---------------------------------------------------
# SPEED MAP
# ---------------------------------------------------

def speed_heatmap(df):

    """
    Visualize speed levels.
    """

    fig = px.scatter_mapbox(
        df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        color="Speed_KMH",
        size="Speed_KMH",
        hover_name="Vehicle_ID",
        zoom=3,
        height=600
    )

    fig.update_layout(
        mapbox_style="carto-positron"
    )

    return fig


# ---------------------------------------------------
# RISK MAP
# ---------------------------------------------------

def risk_map(df):

    """
    Plot risk score locations.
    """

    fig = px.scatter_mapbox(
        df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        color="risk_score",
        size="risk_score",
        hover_name="Vehicle_ID",
        zoom=3,
        height=600
    )

    fig.update_layout(
        mapbox_style="open-street-map"
    )

    return fig


# ---------------------------------------------------
# FUEL MAP
# ---------------------------------------------------

def fuel_consumption_map(df):

    """
    Plot fuel consumption locations.
    """

    fig = px.scatter_mapbox(
        df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        color="fuel_consumption_rate",
        size="fuel_consumption_rate",
        hover_name="Vehicle_ID",
        zoom=3,
        height=600
    )

    fig.update_layout(
        mapbox_style="carto-positron"
    )

    return fig


# ---------------------------------------------------
# DRIVER PERFORMANCE MAP
# ---------------------------------------------------

def performance_map(df):

    """
    Driver behavior score map.
    """

    fig = px.scatter_mapbox(
        df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        color="driver_behavior_score",
        size="driver_behavior_score",
        hover_name="Vehicle_ID",
        zoom=3,
        height=600
    )

    fig.update_layout(
        mapbox_style="open-street-map"
    )

    return fig


# ---------------------------------------------------
# ANOMALY MAP
# ---------------------------------------------------

def anomaly_map(df):

    """
    Show route anomalies.
    """

    if "Route_Deviation" not in df.columns:

        return None

    anomaly_df = df[
        df["Route_Deviation"]
        == "High"
    ]

    if len(anomaly_df) == 0:

        return None

    fig = px.scatter_mapbox(
        anomaly_df,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        color="Route_Deviation",
        hover_name="Vehicle_ID",
        zoom=4,
        height=600
    )

    fig.update_layout(
        mapbox_style="open-street-map"
    )

    return fig


# ---------------------------------------------------
# VEHICLE LOCATION SUMMARY
# ---------------------------------------------------

def latest_vehicle_locations(df):

    """
    Get latest location of each vehicle.
    """

    latest = (
        df.sort_values("timestamp")
        .groupby("Vehicle_ID")
        .tail(1)
    )

    return latest[
        [
            "Vehicle_ID",
            "vehicle_gps_latitude",
            "vehicle_gps_longitude"
        ]
    ]


# ---------------------------------------------------
# LIVE FLEET MAP
# ---------------------------------------------------

def live_fleet_map(df):

    """
    Display latest vehicle positions.
    """

    latest = latest_vehicle_locations(df)

    fig = px.scatter_mapbox(
        latest,
        lat="vehicle_gps_latitude",
        lon="vehicle_gps_longitude",
        hover_name="Vehicle_ID",
        zoom=4,
        height=650
    )

    fig.update_layout(
        mapbox_style="open-street-map"
    )

    return fig


# ---------------------------------------------------
# MAP DASHBOARD SUMMARY
# ---------------------------------------------------

def map_summary(df):

    """
    Map statistics.
    """

    return {
        "Total_Vehicles":
            df["Vehicle_ID"].nunique(),

        "GPS_Records":
            len(df),

        "Latitude_Min":
            round(
                df[
                    "vehicle_gps_latitude"
                ].min(),
                4
            ),

        "Latitude_Max":
            round(
                df[
                    "vehicle_gps_latitude"
                ].max(),
                4
            ),

        "Longitude_Min":
            round(
                df[
                    "vehicle_gps_longitude"
                ].min(),
                4
            ),

        "Longitude_Max":
            round(
                df[
                    "vehicle_gps_longitude"
                ].max(),
                4
            )
    }
