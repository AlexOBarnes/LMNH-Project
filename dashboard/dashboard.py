# pylint: disable=E0401
"""Main dashboard script."""

# Standard library imports
from os import environ as ENV

# Third-party imports
import streamlit as st
import pandas as pd
import altair as alt
from boto3 import client

# Local imports
from sl_queries import get_today_data, get_plant_ids, fetch_plant_species_data

# Page configuration
st.set_page_config(layout="wide")

# AWS S3 client setup
s3 = client('s3',
            aws_access_key_id=ENV["AWS_ACCESS_KEY"],
            aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

BUCKET_NAME = 'c13-wshao-lmnh-long-term-storage'

# Helper functions


@st.cache_data
def list_csv_files():
    """List all CSV files in the S3 bucket."""
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="recordings/")
    files = [obj['Key'] for obj in response.get(
        'Contents', []) if obj['Key'].endswith('.csv')]
    return files


@st.cache_data
def read_historical_data_from_s3(file_key):
    """Reads historical data from S3."""
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
    return pd.read_csv(obj['Body'])


@st.cache_data
def load_historical_data(selected_plant, plant_name_map):
    """Loads and combines historical data from multiple CSV files for selected plants."""
    files = list_csv_files()
    relevant_files = [file for file in files if 'recordings/' in file]
    data_frames = []
    for file in relevant_files:
        df = read_historical_data_from_s3(file)
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        data_frames.append(df)

    combined_df = pd.concat(data_frames, ignore_index=True)

    # Get the plant ID for the selected plant and filter data
    plant_id = plant_name_map[selected_plant]
    filtered_df = combined_df[combined_df['plant_id'] == plant_id]

    return filtered_df


# Plotting functions
def plot_moisture_chart(df, plant_name_map):
    """Plots Altair chart for historical soil moisture."""
    if not df.empty:
        df = df[['timestamp', 'moisture', 'plant_id']]
        hourly_avg = df.resample('H', on='timestamp').mean().reset_index()
        hourly_avg['plant_id'] = hourly_avg['plant_id'].map(plant_name_map)
    else:
        hourly_avg = pd.DataFrame(
            columns=['timestamp', 'moisture', 'plant_id'])

    chart = alt.Chart(hourly_avg).mark_line().encode(
        x='timestamp:T',
        y='moisture:Q',
    ).properties(
        title="Historical Soil Moisture",
        width=600,
        height=400
    )
    return chart


def plot_temperature_chart(df, plant_name_map):
    """Plots Altair chart for historical soil temperature."""
    if not df.empty:
        df = df[['timestamp', 'temperature', 'plant_id']]
        hourly_avg = df.resample('H', on='timestamp').mean().reset_index()
        hourly_avg['plant_id'] = hourly_avg['plant_id'].map(plant_name_map)
    else:
        hourly_avg = pd.DataFrame(
            columns=['timestamp', 'temperature', 'plant_id'])

    chart = alt.Chart(hourly_avg).mark_line(color="#e3298c").encode(
        x='timestamp:T',
        y='temperature:Q',
    ).properties(
        title="Historical Soil Temperature",
        width=600,
        height=400
    )
    return chart


def plot_today_moisture_chart(df):
    """Plots Altair chart for today's soil moisture."""
    if not df.empty:
        df['time'] = pd.to_datetime(df['time'])
    else:
        df = pd.DataFrame(columns=['time', 'soil_moisture'])

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('time:T', title='Time'),
        y=alt.Y('soil_moisture:Q', title='Soil Moisture')
    ).properties(
        title="Today's Soil Moisture",
        width=600,
        height=400
    )
    return chart


def plot_today_temperature_chart(df):
    """Plots Altair chart for today's soil temperature."""
    if not df.empty:
        df['time'] = pd.to_datetime(df['time'])
    else:
        df = pd.DataFrame(columns=['time', 'temperature'])

    chart = alt.Chart(df).mark_line(color='#e3298c').encode(
        x=alt.X('time:T', title='Time'),
        y=alt.Y('temperature:Q', title='Soil Temperature')
    ).properties(
        title="Today's Soil Temperature",
        width=600,
        height=400
    )
    return chart


# Page layout and content
# Title and introduction
st.markdown("<h1 style='color: #e3298c;'>🌱 Monitoring Plant Health Metrics 🌱</h1>",
            unsafe_allow_html=True)

# Sidebar for plant selection
plant_ids = get_plant_ids()  # Fetch plant names from the database
selected_plant = st.sidebar.selectbox(
    'Select plant:', plant_ids)  # List of plant names
plant_name_map = {name: id for id, name in enumerate(plant_ids)}

col1, spacer, col2 = st.columns([5, 0.25, 4])

with col1:
    st.write("This page provides an overview of the health metrics recorded for the plants in the conservatory, including soil moisture and temperature.")
    st.write("The data is collected every minute and visualised to help museum staff monitor plant conditions in real-time.")
    st.write("Choose a plant to observe from the menu on the sidebar.")

with col2:
    # Fetch and display plant species data
    species_data = fetch_plant_species_data(selected_plant)
    # Check if the DataFrame has data
    if not species_data.empty and species_data.shape[1] == 5:
        species_data.columns = ["Plant ID", "Species ID", "Scientific Name", "Common Name", "Last Watered"]
    else:
        st.error("The species_data DataFrame is either empty or does not have 5 columns.")

    st.subheader("Plant Species Information")
    st.dataframe(species_data, hide_index=True)


# Layout for today's data
st.subheader("Today's Data")
col1, col2 = st.columns(2)

# Display today's Soil Moisture data
with col1:
    if selected_plant:
        today_soil_moisture = get_today_data(selected_plant, 'soil_moisture')
        st.altair_chart(plot_today_moisture_chart(
            today_soil_moisture), use_container_width=True)

# Display today's Temperature data
with col2:
    if selected_plant:
        today_temperature = get_today_data(selected_plant, 'temperature')
        st.altair_chart(plot_today_temperature_chart(
            today_temperature), use_container_width=True)


# Load and display historical data
historical_data = load_historical_data(selected_plant, plant_name_map)

st.subheader("Historical Data")
col1, col2 = st.columns(2)

# Display historical Soil Moisture data
with col1:
    st.altair_chart(plot_moisture_chart(historical_data,
                    plant_name_map), use_container_width=True)

# Display historical Temperature data
with col2:
    st.altair_chart(plot_temperature_chart(historical_data,
                    plant_name_map), use_container_width=True)
