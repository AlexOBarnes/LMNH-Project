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
         
The data is collected every minute and visualised to help museum staff monitor plant conditions in real-time.
         
Choose the plants to observe from the menu on the sidebar.
""")

s3 = client('s3',
            aws_access_key_id=ENV["AWS_ACCESS_KEY"],
            aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

bucket_name = 'c13-wshao-lmnh-long-term-storage'


def list_csv_files():
    """List all CSV files in the S3 bucket."""
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="recordings/")
    files = [obj['Key'] for obj in response.get(
        'Contents', []) if obj['Key'].endswith('.csv')]
    return files


def read_historical_data_from_s3(file_key):
    """Reads historical data from S3."""
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])


def load_historical_data(selected_plants, plant_name_map):
    """Loads and combines historical data from multiple CSV files for selected plants."""
    files = list_csv_files()
    relevant_files = [file for file in files if 'recordings/' in file]
    print(plant_name_map)
    data_frames = []
    for file in relevant_files:
        df = read_historical_data_from_s3(file)
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(
            df['timestamp'])
        # Append to list of dataframes
        data_frames.append(df)

    combined_df = pd.concat(data_frames, ignore_index=True)

    # Filter for selected plants
    plant_ids = [id for id, name in plant_name_map.items()
                 if name in selected_plants]
    filtered_df = combined_df[combined_df['plant_id'].isin(plant_ids)]

    return filtered_df


def plot_moisture_chart(df, plant_name_map):
    """Plots Altair chart for soil moisture."""
    # Resample to hourly average
    hourly_avg = df.resample('H', on='timestamp').mean().reset_index()

    # Map plant_id to names for coloring
    hourly_avg['plant_name'] = hourly_avg['plant_id'].map(plant_name_map)

    chart = alt.Chart(hourly_avg).mark_line().encode(
        x='timestamp:T',
        y='moisture:Q',
        color='plant_name:N'  # Use plant names for color encoding
    ).properties(
        title="Historical Soil Moisture",
        width=600,
        height=400
    ).configure_legend(
        title=None
    )
    return chart


def plot_temperature_chart(df, plant_name_map):
    """Plots Altair chart for soil temperature."""
    # Resample to hourly average
    hourly_avg = df.resample('H', on='timestamp').mean().reset_index()

    # Map plant_id to names for coloring
    hourly_avg['plant_name'] = hourly_avg['plant_id'].map(plant_name_map)

    chart = alt.Chart(hourly_avg).mark_line().encode(
        x='timestamp:T',
        y='temperature:Q',
        color='plant_name:N'  # Use plant names for color encoding
    ).properties(
        title="Historical Soil Temperature",
        width=600,
        height=400
    ).configure_legend(
        title=None
    )
    return chart


# Sidebar for plant selection
plants = get_plant_names()  # Fetch plant names from the database
selected_plants = st.sidebar.multiselect(
    'Select plant(s):',
    plants, default=plants[:]
)

# Create a mapping of plant names to IDs
plant_name_map = {id: name for id, name in enumerate(
    plants)}

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

# Load historical data for selected plants
historical_data = load_historical_data(selected_plants, plant_name_map)

col1, col2 = st.columns(2)

# Display historical Soil Moisture data
with col1:
    st.subheader("Historical Soil Moisture")
    if not historical_data.empty:
        st.altair_chart(plot_moisture_chart(historical_data,
                        plant_name_map), use_container_width=True)
    else:
        st.write("No historical data available for selected plants.")

# Display historical Temperature data
with col2:
    st.subheader("Historical Soil Temperature")
    if not historical_data.empty:
        st.altair_chart(plot_temperature_chart(historical_data,
                        plant_name_map), use_container_width=True)
    else:
        st.write("No historical data available for selected plants.")
