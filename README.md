# 🚛 Fleet Vehicle Telematics Analyzer

### Transforming Raw GPS Data into Actionable Fleet Intelligence

## 📌 Project Overview

**Fleet Vehicle Telematics Analyzer** is a Python and Streamlit-based analytics application designed to monitor and analyze fleet vehicle operations using GPS and telemetry data.

The system processes vehicle location, fuel consumption, driver behavior, and risk-related information to generate meaningful insights through interactive dashboards and visualizations.

The main goal is to help fleet managers identify fuel wastage, detect excessive vehicle idling, evaluate driver performance, and understand route efficiency.

## 🎯 Project Objectives

- Analyze vehicle GPS and telemetry data.
- Monitor vehicle locations and movement.
- Identify vehicle idling and unnecessary fuel consumption.
- Analyze driver behavior and performance.
- Evaluate vehicle route efficiency.
- Visualize fleet performance through interactive dashboards.
- Support better, data-driven fleet management decisions.

## ✨ Key Features

### 1. Fleet Overview
- Overview of fleet operations.
- Vehicle location visualization.
- Fleet activity and telemetry insights.
- Key operational performance indicators.

### 2. Idling Analysis
- Detects vehicles that remain idle based on configured speed and fuel thresholds.
- Estimates fuel wasted during idling.
- Identifies idling hotspots.
- Displays vehicle-wise idling analysis and comparisons.

### 3. Driver Scorecard
- Analyzes driver behavior scores.
- Evaluates vehicle and driver risk information.
- Compares driver performance.
- Provides performance rankings and insights.

### 4. Route Efficiency
- Analyzes GPS-based vehicle movement.
- Calculates distance using geographical coordinates.
- Examines vehicle speed and route performance.
- Helps identify potentially inefficient routes.

### 5. Interactive Dashboard
- Interactive charts and graphs.
- GPS-based map visualizations.
- Vehicle selection and analysis.
- Data-driven operational insights.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data processing and manipulation |
| NumPy | Numerical calculations |
| GeoPy | Geographical distance calculations |
| Streamlit | Interactive web application |
| Plotly | Interactive charts and visualizations |
| OpenStreetMap | Map visualization |
| GitHub | Version control and project hosting |
| Streamlit Cloud | Application deployment |

## 📂 Project Structure

```text
Fleet-Vehicle-Telematics-Analyzer/
│
├── app.py
│
├── data/
│   └── dynamic_supply_chain_logistics_dataset.csv
│
├── pages/
│   ├── 1_Fleet_Overview.py
│   ├── 2_Idling_Analysis.py
│   ├── 3_Driver_Scorecard.py
│   └── 4_Route_Efficiency.py
│
├── utils/
│   ├── maps.py
│   ├── preprocessing.py
│   └── analytics.py
│
├── requirements.txt
│
└── README.md
```

## 📊 Dataset Information

**Dataset Name:** Dynamic Supply Chain Logistics Dataset

**Source:** Kaggle

The project uses logistics and vehicle telemetry information, including relevant fields such as:

- Timestamp
- Vehicle GPS Latitude
- Vehicle GPS Longitude
- Fuel Consumption Rate
- Driver Behavior Score
- Risk Score

Vehicle identifiers and additional analytical fields may be generated or calculated during preprocessing when required.

**Data Processing Workflow:**

```text
Raw Dataset
     ↓
Data Cleaning
     ↓
Data Preprocessing
     ↓
GPS Distance Calculation
     ↓
Speed Calculation
     ↓
Idling Detection
     ↓
Fuel Consumption Analysis
     ↓
Driver Performance Analysis
     ↓
Interactive Dashboard
```

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/Fleet-Vehicle-Telematics-Analyzer.git
```

### Step 2: Navigate to the Project Folder

```bash
cd Fleet-Vehicle-Telematics-Analyzer
```

### Step 3: Create a Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Add the Dataset

Download the Dynamic Supply Chain Logistics Dataset from Kaggle and place the required CSV file inside the `data` folder.

Expected file path:

```text
data/dynamic_supply_chain_logistics_dataset.csv
```

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📈 Expected Results

The system provides:

- Interactive fleet monitoring.
- Vehicle GPS location visualization.
- Automatic idling identification based on configured thresholds.
- Fuel wastage analysis.
- Driver performance comparisons.
- Vehicle risk analysis.
- Route efficiency insights.
- Visual reports to support fleet management.

## 🚀 Future Enhancements

The project can be extended with:

- Real-time GPS tracking using IoT devices.
- Machine learning-based driver behavior prediction.
- Predictive vehicle maintenance.
- Real-time fuel consumption monitoring.
- Advanced route optimization.
- Mobile application integration.
- Automated alerts for unusual vehicle activity.
- Accident and anomaly detection.

## 👨‍💻 Project Team

**Project Title:** Fleet Vehicle Telematics Analyzer

**Team Members:**
1. Kareem Sab
2. Syeda Fariha Fathima
3. Naveeka Lohith
4. Prajwal A S

**Project Guide:** Sri Sateesha Ambesange

**Department:** Computer Science

**Institution:** Vidya Vikas Institute of Engineering and Technology, Mysore

**Academic Year:** 2025–2026

## 🎓 Project Domain

**Smart Transportation & Fleet Analytics**

## 📝 Conclusion

Fleet Vehicle Telematics Analyzer transforms raw vehicle telemetry data into meaningful operational insights through data processing, geographical analysis, and interactive visualizations.

By analyzing GPS movement, fuel consumption, idling behavior, driver performance, and route efficiency, the application supports more efficient and informed fleet management.

---

⭐ **If you find this project useful, consider giving this repository a star!**

**Developed as an academic project – 2025–2026.**
