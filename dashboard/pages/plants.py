"""Dashboard page for a table of all plants in the database."""

import streamlit as st
import pandas as pd
from pyodbc import connect
from dotenv import load_dotenv
from os import environ as ENV

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
    query = "SELECT common_name, scientific_name FROM gamma.plant_species"
    with get_connection() as conn:
        return pd.read_sql(query, conn)


def run():
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='color: #e3298c;'>Available Plants</h1>",
                unsafe_allow_html=True)

    # Fetch plant data
    plant_data = fetch_plant_data()

    # Rename columns
    plant_data.rename(columns={
        "common_name": "Common Name",
        "scientific_name": "Scientific Name"
    }, inplace=True)

    # Display the plant data as a table
    # Using st.table for full display without scrollbars
    st.table(plant_data)


if __name__ == "__main__":
    run()
