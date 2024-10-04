"""A file for extracting data older than 24 hours from the RDS
into a CSV to be stored in an S3 bucket."""

from os import environ as ENV
import logging
from pymssql import connect
from dotenv import load_dotenv
import pandas as pd
from logging_long import logger_setup


LOGGER = logging.getLogger(__name__)


def connect_to_rds():
    """Connects to an RDS database using pyodbc."""

    conn = connect(server=ENV["DB_HOST"],
                   port=ENV["DB_PORT"],
                   user=ENV["DB_USER"],
                   password=ENV["DB_PASSWORD"],
                   database=ENV["DB_NAME"],
                   as_dict=True)

    LOGGER.info("Successfully connected to the RDS.")
    return conn


def extract_plant_data() -> pd.DataFrame:
    """Extracts plant data older than 24 from the RDS and truncates the
    recordings table."""

    extract_query = (
        "SELECT * FROM gamma.recordings; "
    ).strip()

    truncate_query = "TRUNCATE TABLE gamma.recordings;"

    with connect_to_rds() as conn:
        try:
            LOGGER.info("Executing extract query.")
            with conn.cursor() as cur:
                cur.execute(extract_query)
                result = cur.fetchall()
                LOGGER.info("Data extraction successful.")

            df = pd.DataFrame(result, columns=[
                              'recording_id', 'timestamp', 'soil_moisture', 'temperature', 'plant_id', 'botanist_id'])

        except Exception as e:
            LOGGER.error("Error during data extraction: %s", e)
            return pd.DataFrame(columns=["recording_id", "timestamp", "soil_moisture", "temperature", "plant_id", "botanist_id"])

        LOGGER.info("Executing truncate query.")
        with conn.cursor() as cur:
            cur.execute(truncate_query)
            conn.commit()
            LOGGER.info("Recordings table truncated successfully.")

    return df.rename(columns={"time_taken": "timestamp"})


if __name__ == "__main__":

    logger_setup("extract_long_log.log", "logs")
    load_dotenv()
    LOGGER.info("Loading environment variables from .env file.")

    plant_data = extract_plant_data()

    if not plant_data.empty:
        LOGGER.info("Extracted %s records", len(plant_data))
        for i in range(len(plant_data)):
            print(plant_data.iloc[i])

    else:
        LOGGER.info("No data extracted.")
