"""A file for extracting data older than 24 hours from the RDS
into a CSV to be stored in an S3 bucket."""
# pylint: disable=E0611

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


def extract_plant_data() -> pd.DataFrame:
    """Extracts plant data older than 24 from the RDS and truncates the
    recordings table."""

    extract_query = (
        "SELECT recording_id, time_taken, soil_moisture, temperature, plant_id, botanist_id "
        "FROM gamma.recordings;"
    ).strip()

    truncate_query = "TRUNCATE TABLE gamma.recordings;"

    with connect_to_rds() as conn:
        try:
            df = pd.read_sql(extract_query, conn)
        except Exception:
            return pd.DataFrame(columns=["recording_id", "timestamp", "soil_moisture", "temperature", "plant_id", "botanist_id"])

        with conn.cursor() as cur:
            cur.execute(truncate_query)
            conn.commit()

    return df.rename(columns={"time_taken": "timestamp"})


if __name__ == "__main__":

    load_dotenv()

    plant_data = extract_plant_data()

    if not plant_data.empty:
        for i in range(len(plant_data)):
            print(plant_data.iloc[i])

    else:
        print("No data extracted.")
