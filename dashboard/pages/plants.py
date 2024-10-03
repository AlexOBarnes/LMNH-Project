# pylint: disable=E0611
"""Dashboard page for a table of all plants in the database."""

from os import environ as ENV
import streamlit as st
import pandas as pd
from pyodbc import connect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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

# Display the plant data as a table without the index
st.table(plant_data)
st.markdown("<style>th.row_heading, th.blank {display:None}</style>", unsafe_allow_html=True)
