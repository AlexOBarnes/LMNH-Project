# pylint: disable=E0611
# """Dashboard page for a table of all plants in the database."""

# from os import environ as ENV
# import streamlit as st
# import pandas as pd
# from pyodbc import connect
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()


# def get_connection():
#     '''Returns a connection to the RDS database'''
#     return connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#                    f"SERVER={ENV['DB_HOST']},{ENV['DB_PORT']};"
#                    f"DATABASE={ENV['DB_NAME']};"
#                    f"UID={ENV['DB_USER']};"
#                    f"PWD={ENV['DB_PASSWORD']}")


# def fetch_plant_data():
#     '''Fetches plant species data from the database'''
#     query = """
#     SELECT p.plant_id, ps.common_name, ps.scientific_name
#     FROM gamma.plants p
#     JOIN gamma.plant_species ps ON p.plant_species_id = ps.plant_species_id;
#     """
#     with get_connection() as conn:
#         return pd.read_sql(query, conn)


# st.set_page_config(layout="wide")
# st.markdown("<h1 style='color: #e3298c;'>🌱 Available Plants 🌱</h1>",
#             unsafe_allow_html=True)

# # Fetch plant data
# plant_data = fetch_plant_data()

# # Rename columns
# plant_data.rename(columns={
#     "plant_id": "Plant ID",
#     "common_name": "Common Name",
#     "scientific_name": "Scientific Name"
# }, inplace=True)

# # Display the plant data as a table without the index
# st.table(plant_data)
# st.markdown("<style>th.row_heading, th.blank {display:None}</style>", unsafe_allow_html=True)

# pylint: disable=E0611
"""Dashboard page for a table of all plants in the database."""

from os import environ as ENV
import streamlit as st
import pandas as pd
from pyodbc import connect
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Add your Unsplash access key in .env
US_ACCESS_KEY = ENV['US_ACCESS_KEY']


def get_connection():
    '''Returns a connection to the RDS database'''
    return connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                   f"SERVER={ENV['DB_HOST']},{ENV['DB_PORT']};"
                   f"DATABASE={ENV['DB_NAME']};"
                   f"UID={ENV['DB_USER']};"
                   f"PWD={ENV['DB_PASSWORD']}")


def fetch_plant_data():
    '''Fetches plant species data from the database'''
    query = """
    SELECT p.plant_id, ps.common_name, ps.scientific_name
    FROM gamma.plants p
    JOIN gamma.plant_species ps ON p.plant_species_id = ps.plant_species_id;
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)


def fetch_plant_image(common_name):
    '''Fetches an image URL from Unsplash based on the common name of the plant'''
    url = f"https://api.unsplash.com/search/photos?query={common_name}&client_id={US_ACCESS_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            # Returns the URL of the first result
            return data['results'][0]['urls']['regular']
    return None  # Return None if no image is found


st.set_page_config(layout="wide")
st.markdown("<h1 style='color: #e3298c;'>🌱 Available Plants 🌱</h1>",
            unsafe_allow_html=True)

# Fetch plant data
plant_data = fetch_plant_data()

# Rename columns
plant_data.rename(columns={
    "plant_id": "Plant ID",
    "common_name": "Common Name",
    "scientific_name": "Scientific Name"
}, inplace=True)

# Create a container to hold the plant cards
plant_container = st.container()

# Display the plant data in a card-like layout
for _, row in plant_data.iterrows():
    plant_id = row['Plant ID']
    common_name = row['Common Name']
    scientific_name = row['Scientific Name']
    image_url = fetch_plant_image(common_name)

    # Create a card layout for each plant
    with plant_container:
        cols = st.columns(3)  # Create two columns for layout

        # First column for the plant information
        with cols[0]:
            st.subheader(f"Plant ID: {plant_id}")  # Display plant ID
            st.write(f"**Common Name:** {common_name}")
            st.write(f"**Scientific Name:** {scientific_name}")

        # Second column for the image
        with cols[1]:
            if image_url:
                st.image(image_url, width=250)
            else:
                st.write("Image not found.")

        # Third empty column
        with cols[2]:
            st.write("")  # Leave this column empty

        st.markdown("---")  # Add a separator between plants
