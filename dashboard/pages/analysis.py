"""Analysis page for dashboard with graphs."""

import streamlit as st
import pandas as pd
import numpy as np  # Import NumPy for random number generation
import altair as alt

# Page configuration
st.set_page_config(layout="wide")

# Title and Introduction
st.title("Plant Data Analysis")
st.subheader("Monitoring Plant Health Metrics")

st.write("""
This page provides an overview of the health metrics recorded for the plants in the conservatory, including soil moisture, temperature, and other environmental factors.
The data is collected every minute and visualized to help museum staff monitor plant conditions in real-time.
""")

# Load or simulate plant data (replace with actual data source if available)
data = {
    "Timestamp": pd.date_range(start="2024-09-01", periods=100, freq="T"),
    "Soil Moisture (%)": np.random.uniform(10, 40, 100),  # Use NumPy directly
    "Temperature (°C)": np.random.uniform(15, 30, 100),    # Use NumPy directly
}

df = pd.DataFrame(data)

# Create Altair charts
# Line chart for Soil Moisture
soil_moisture_chart = (
    alt.Chart(df)
    .mark_line(color="#e3298c")
    .encode(
        x='Timestamp:T',
        y='Soil Moisture (%):Q',
        tooltip=['Timestamp:T', 'Soil Moisture (%):Q']
    )
    .properties(title="Soil Moisture Over Time")
)

# Line chart for Temperature
temperature_chart = (
    alt.Chart(df)
    .mark_line(color="#1f77b4")
    .encode(
        x='Timestamp:T',
        y='Temperature (°C):Q',
        tooltip=['Timestamp:T', 'Temperature (°C):Q']
    )
    .properties(title="Temperature Over Time")
)

# Create two columns for charts
col1, col2 = st.columns(2)

# Display the charts in columns
with col1:
    st.altair_chart(soil_moisture_chart, use_container_width=True)

with col2:
    st.altair_chart(temperature_chart, use_container_width=True)
