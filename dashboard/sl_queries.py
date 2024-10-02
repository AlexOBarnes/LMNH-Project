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


def fetch_today_data(plant_id):
    '''Fetches today's data for a specific plant.'''
    query = f"""
    SELECT time_taken, soil_moisture, temperature
    FROM gamma.recordings
    WHERE plant_id = {plant_id}
      AND CAST(time_taken AS DATE) = CAST(GETDATE() AS DATE)
    ORDER BY time_taken;
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)


def fetch_historical_data(plant_id):
    '''Fetches historical data from S3.'''
    # Simulate reading from S3 for now. Replace with actual S3 reading logic.
    historical_data = pd.read_csv(
        f"s3://your-bucket-name/historical_plant_{plant_id}.csv")
    return historical_data
