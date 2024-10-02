"""Main dashboard script."""

from os import environ as ENV
import streamlit as st
import pandas as pd
import altair as alt
from sl_queries import get_today_data, get_plant_names
from boto3 import client

# Page configuration
st.set_page_config(layout="wide")

# Title and Introduction
st.markdown("<h1 style='color: #e3298c;'>Monitoring Plant Health Metrics</h1>",
            unsafe_allow_html=True)

st.write("""
This page provides an overview of the health metrics recorded for the plants in the conservatory, including soil moisture and temperature.
         
The data is collected every minute and visualized to help museum staff monitor plant conditions in real-time.
         
Choose the plants to observe from the menu on the sidebar.
""")

s3 = client('s3',
            aws_access_key_id=ENV["AWS_ACCESS_KEY"],
            aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
bucket_name = 'c13-wshao-lmnh-long-term-storage'


def read_historical_data_from_s3(file_key):
    """Reads historical data from S3."""
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])


def plot_chart(df, title, y_column):
    """Plots Altair charts."""
    chart = alt.Chart(df).mark_line().encode(
        x='time:T',
        y=alt.Y(y_column, title=y_column)
    ).properties(
        title=title
    )
    return chart


# Sidebar for plant selection
plant = get_plant_names()  # Fetch plant names from the database
selected_plants = st.sidebar.multiselect(
    'Select plant(s):',
    plant  # Use plant names for selection
)

# Layout for today's data
col1, col2 = st.columns(2)

# Today's Soil Moisture
with col1:
    st.subheader("Today's Soil Moisture")
    for plant in selected_plants:
        today_soil_moisture = get_today_data(selected_plants, 'soil_moisture')
        st.line_chart(
            today_soil_moisture['soil_moisture'], use_container_width=True)

# Today's Temperature
with col2:
    st.subheader("Today's Soil Temperature")
    for plant in selected_plants:
        today_temperature = get_today_data(selected_plants, 'temperature')
        st.line_chart(
            today_temperature['temperature'], use_container_width=True)

# Historical Data
with col1:
    st.subheader("Historical Soil Moisture")
    historical_file_key = f'{plant}_soil_moisture.csv'  # Adjust based on your file naming convention
    historical_soil_moisture = read_historical_data_from_s3(historical_file_key)
    st.altair_chart(plot_chart(historical_soil_moisture, "Historical Soil Moisture", 'soil_moisture'))

with col2:
    st.subheader("Historical Soil Temperature")
    historical_temperature_file_key = f'{plant}_temperature.csv'  # Adjust based on your file naming convention
    historical_temperature = read_historical_data_from_s3(historical_temperature_file_key)
    st.altair_chart(plot_chart(historical_temperature, "Historical Soil Temperature", 'temperature'))