"""Main dashboard script."""

from os import environ as ENV
import streamlit as st
import pandas as pd
import altair as alt
from sl_queries import get_today_data, get_plant_ids, fetch_plant_species_data
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
    data_frames = []
    for file in relevant_files:
        df = read_historical_data_from_s3(file)
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(
            df['timestamp'])
        # Append to list of dataframes
        data_frames.append(df)

    combined_df = pd.concat(data_frames, ignore_index=True)

    # Filter for the selected plant
    # Get the plant ID for the selected plant
    plant_id = plant_name_map[selected_plant]
    filtered_df = combined_df[combined_df['plant_id']
                              == plant_id]  # Filter for selected plant ID

    return filtered_df


def plot_moisture_chart(df, plant_name_map):
    """Plots Altair chart for soil moisture."""
    hourly_avg = pd.DataFrame(["timestamp", "moisture", "plant_id"])
    if not df.empty:
        # Resample to hourly average
        hourly_avg = df.resample('H', on='timestamp').mean().reset_index()
        # Map plant_id to names for coloring
        hourly_avg['plant_id'] = hourly_avg['plant_id'].map(plant_name_map)

    chart = alt.Chart(hourly_avg).mark_line().encode(
        x='time:T',
        y='moisture:Q',
    ).properties(
        title="Historical Soil Moisture",
        width=600,
        height=400
    )
    return chart


def plot_temperature_chart(df, plant_name_map):
    """Plots Altair chart for soil temperature."""
    hourly_avg = pd.DataFrame(["timestamp", "temperature", "plant_id"])
    if not df.empty:
        # Resample to hourly average
        hourly_avg = df.resample('H', on='timestamp').mean().reset_index()
        # Map plant_id to names for coloring
        hourly_avg['plant_id'] = hourly_avg['plant_id'].map(plant_name_map)

    chart = alt.Chart(hourly_avg).mark_line(color="#e3298c").encode(
        x='time:T',
        y='temperature:Q',
    ).properties(
        title="Historical Soil Temperature",
        width=600,
        height=400
    )
    return chart


# Sidebar for plant selection
plant_ids = get_plant_ids()  # Fetch plant names from the database
selected_plant = st.sidebar.selectbox(
    'Select plant:',
    plant_ids  # List of plant names
)

# Create a mapping of plant names to IDs
plant_name_map = {name: id for id, name in enumerate(plant_ids)}

# Fetch plant species data for the selected plant
species_data = fetch_plant_species_data(selected_plant)

# Rename the columns for better readability
species_data.columns = [
    "Plant ID",
    "Species ID",
    "Common Name",
    "Scientific Name",
    "Last Watered"
]

# Display the species data as a table
st.subheader("Plant Species Information")
st.table(species_data)

# Layout for today's data
st.subheader("Today's Data")
col1, col2 = st.columns(2)

# Display today's Soil Moisture data
with col1:
    if selected_plant:
        today_soil_moisture = get_today_data(selected_plant, 'soil_moisture')

        # Prepare the data for Altair
        today_soil_moisture['time'] = pd.to_datetime(
            # Ensure timestamp is in datetime format
            today_soil_moisture['time'])

        # Create an Altair chart for today's soil moisture
        chart = alt.Chart(today_soil_moisture).mark_line().encode(  # Set the line color (change 'blue' as needed)
            x='time:T',
            y='moisture:Q'
        ).properties(
            title="Today's Soil Moisture",
            width=600,
            height=400
        )

        # Display the Altair chart in Streamlit
        st.altair_chart(chart, use_container_width=True)

# Display today's Temperature data
with col2:
    if selected_plant:
        today_temperature = get_today_data(selected_plant, 'temperature')

        # Prepare the data for Altair
        today_temperature['time'] = pd.to_datetime(
            # Ensure timestamp is in datetime format
            today_temperature['time'])

        # Create an Altair chart for today's temperature
        chart = alt.Chart(today_temperature).mark_line(color='#e3298c').encode(
            x='time:T',
            y='temperature:Q'
        ).properties(
            title="Today's Soil Temperature",
            width=600,
            height=400
        )

        # Display the Altair chart in Streamlit
        st.altair_chart(chart, use_container_width=True)

# Load historical data for selected plants
historical_data = load_historical_data(selected_plant, plant_name_map)

st.subheader("Historical Data")
col1, col2 = st.columns(2)

# Display historical Soil Moisture data
with col1:
    st.altair_chart(plot_moisture_chart(historical_data, plant_name_map), use_container_width=True)


# Display historical Temperature data
with col2:
    st.altair_chart(plot_temperature_chart(historical_data, plant_name_map), use_container_width=True)
