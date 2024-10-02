"""This script contains the queries for recent and historical data."""

from os import environ as ENV
import pandas as pd
from pyodbc import connect
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    '''Returns a connection to the RDS database'''
    return connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                   f"SERVER={ENV['DB_HOST']},{ENV['DB_PORT']};"
                   f"DATABASE={ENV['DB_NAME']};"
                   f"UID={ENV['DB_USER']};"
                   f"PWD={ENV['DB_PASSWORD']}")


def get_today_data(selected_plants, metric):
    """Fetches today's data for the selected plants."""
    # Create a comma-separated string of plant names for SQL query
    plants_placeholder = ', '.join(f"'{plant}'" for plant in selected_plants)

    query = f"""
    SELECT time_taken AS time, {metric}
    FROM gamma.recordings
    JOIN gamma.plants ON gamma.recordings.plant_id = gamma.plants.plant_id
    JOIN gamma.plant_species ON gamma.plants.plant_species_id = gamma.plant_species.plant_species_id
    WHERE gamma.plant_species.common_name IN ({plants_placeholder})
    AND time_taken >= CAST(GETDATE() AS DATE)
    ORDER BY time_taken;
    """

    with get_connection() as conn:
        df = pd.read_sql(query, conn)

    return df


def get_plant_names():
    """Gets stored plant names."""
    query = "SELECT common_name FROM gamma.plant_species;"
    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    return df['common_name'].tolist()
