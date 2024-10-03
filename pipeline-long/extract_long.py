"""A file for extracting data older than 24 hours from the RDS
into a CSV to be stored in an S3 bucket."""

from os import environ as ENV
from pyodbc import connect
from dotenv import load_dotenv
import pandas as pd


def connect_to_rds():
    """Connects to an RDS database using pyodbc."""

    return connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                   f"SERVER={ENV['DB_HOST']},{ENV['DB_PORT']};"
                   f"DATABASE={ENV['DB_NAME']};"
                   f"UID={ENV['DB_USER']};"
                   f"PWD={ENV['DB_PASSWORD']}")


def extract_plant_data() -> list[dict[str, any]]:
    """Extracts plant data older than 24 from the RDS."""

    query = """
    SELECT recording_id, time_taken, soil_moisture, temperature, plant_id, botanist_id
    FROM gamma.recordings;
    """

    with connect_to_rds() as conn:
        df = pd.read_sql(query, conn)
        data = df.to_dict(orient='records')

    return data


if __name__ == "__main__":

    load_dotenv()

    plant_data = extract_plant_data()

    if plant_data:
        for row in plant_data[:5]:
            print(row)

    else:
        print("No data extracted.")
