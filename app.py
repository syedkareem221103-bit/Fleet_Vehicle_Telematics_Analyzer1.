import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Fleet Vehicle Telematics Analyzer",
    page_icon="🚛",
    layout="wide"
)

# ---------------------------------------------------
# DATA LOADING
# ---------------------------------------------------

@st.cache_data
def load_data():

    # Absolute path (works locally and on Streamlit Cloud)
    DATA_PATH = (
        Path(__file__).resolve().parent
        / "data"
        / "dynamic_supply_chain_logistics_dataset.csv"
    )

    if not DATA_PATH.exists():

        st.error(
            f"Dataset not found:\n{DATA_PATH}"
        )
        st.stop()

    df = pd.read_csv(DATA_PATH)

    return df


df = load_data()

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("🚛 Fleet Vehicle Telematics Analyzer")

st.markdown("""
### Smart Fleet Monitoring Dashboard

This solution provides:

- 🚚 Fleet Overview
- ⛽ Fuel Consumption Analytics
- 🛑 Idling Detection
- 🏆 Driver Scorecards
- 🛣️ Route Efficiency Analysis
- 📍 GPS Tracking
- 📈 Operational Insights
- ⚠️ Risk Monitoring
""")

st.divider()

# ---------------------------------------------------
# DATASET INFO
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Records",
        len(df)
    )

with col2:
    st.metric(
        "Total Columns",
        len(df.columns)
    )

with col3:
    st.metric(
        "Dataset Size",
        f"{round(df.memory_usage().sum()/1024/1024,2)} MB"
    )

# ---------------------------------------------------
# PREVIEW
# ---------------------------------------------------

st.subheader("📄 Dataset Preview")

st.dataframe(
    df.head(20),
    use_container_width=True
)

# ---------------------------------------------------
# COLUMN INFO
# ---------------------------------------------------

st.subheader("📊 Dataset Columns")

st.write(list(df.columns))

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.success(
    "Select a dashboard page from the sidebar."
)

st.sidebar.markdown("""
### Available Dashboards

🚛 Fleet Overview

⛽ Idling Analysis

🏆 Driver Scorecard

🛣️ Route Efficiency
""")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.info(
    "Fleet Vehicle Telematics Analyzer | Streamlit Dashboard"
)
