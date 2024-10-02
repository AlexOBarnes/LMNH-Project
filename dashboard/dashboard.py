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
st.markdown("<h1 style='color: #e3298c;'>🌱 Monitoring Plant Health Metrics 🌱</h1>",
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


def list_csv_files():
    """List all CSV files in the S3 bucket."""
    response = s3.list_objects_v2(Bucket=bucket_name)
    files = [obj['Key'] for obj in response.get(
        'Contents', []) if obj['Key'].endswith('.csv')]
    return files


def read_historical_data_from_s3(file_key):
    """Reads historical data from S3."""
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])


def load_and_combine_historical_data(selected_plant, metric):
    """Loads and combines historical data from multiple CSV files."""
    files = list_csv_files()

    # Filter the files to match the selected plant and metric
    relevant_files = [
        file for file in files if selected_plant in file and metric in file]

    # Load and combine data from relevant files
    data_frames = [read_historical_data_from_s3(
        file) for file in relevant_files]
    combined_df = pd.concat(data_frames, ignore_index=True)

    # Convert time_taken to datetime and set it as index
    combined_df['time_taken'] = pd.to_datetime(combined_df['time_taken'])
    combined_df.set_index('time_taken', inplace=True)

    # Resample to hourly average
    hourly_avg = combined_df.resample('H').mean().reset_index()

    return hourly_avg


def plot_chart(df, title, y_column):
    """Plots Altair charts."""
    chart = alt.Chart(df).mark_line().encode(
        x='time_taken:T',
        y=alt.Y(y_column, title=y_column)
    ).properties(
        title=title,
        width=600,
        height=400
    )
    return chart


# Sidebar for plant selection
plants = get_plant_names()  # Fetch plant names from the database
selected_plants = st.sidebar.multiselect(
    'Select plant(s):',
    plants,  # Use plant names for selection
    default=plants[:2]  # Preselect first two plants for visualization
)

# Layout for today's data
col1, col2 = st.columns(2)

# Display today's Soil Moisture data
with col1:
    st.subheader("Today's Soil Moisture")
    if selected_plants:
        for plant in selected_plants:
            today_soil_moisture = get_today_data([plant], 'soil_moisture')
            st.line_chart(
                today_soil_moisture['soil_moisture'], use_container_width=True)

# Display today's Temperature data
with col2:
    st.subheader("Today's Soil Temperature")
    if selected_plants:
        for plant in selected_plants:
            today_temperature = get_today_data([plant], 'temperature')
            st.line_chart(
                today_temperature['temperature'], use_container_width=True)

col1, col2 = st.columns(2)

# Display historical Soil Moisture data
with col1:
    st.subheader("Historical Soil Moisture")
    if selected_plants:
        for plant in selected_plants:
            historical_soil_moisture = load_and_combine_historical_data(
                plant, 'soil_moisture')
            st.altair_chart(plot_chart(historical_soil_moisture,
                            f"Historical Soil Moisture - {plant}", 'soil_moisture'))

# Display historical Temperature data
with col2:
    st.subheader("Historical Soil Temperature")
    if selected_plants:
        for plant in selected_plants:
            historical_temperature = load_and_combine_historical_data(
                plant, 'temperature')
            st.altair_chart(plot_chart(
                historical_temperature, f"Historical Soil Temperature - {plant}", 'temperature'))
