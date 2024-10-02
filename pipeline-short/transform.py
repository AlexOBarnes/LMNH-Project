'''Transfroms the extracted data'''
import re
import logging
import pyodbc
from logger import logger_setup
from os import environ as ENV
from datetime import datetime as dt
import pandas as pd


from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)


def get_connection() -> pyodbc.Connection | None:
    """Connects to an RDS database using pyodbc."""

    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={ENV["DB_HOST"]};"
            f"DATABASE={ENV["DB_NAME"]};"
            f"UID={ENV["DB_USER"]};"
            f"PWD={ENV["DB_PASSWORD"]}"
        )

        connection = pyodbc.connect(connection_string)
        LOGGER.info("Connection established to RDS")
        return connection

    except pyodbc.Error as err:
        LOGGER.error(f"Error connecting to RDS %s: ", err)
        raise err


def is_valid_email(email: str) -> bool:
    '''Returns True if an email is valid'''
    return (isinstance(email, str)) and ("@" in email)


def split_name(name: str) -> list[str]:
    '''Return the first and last name'''

    names = name.strip().split(" ")
    if len(names) > 1:
        return [names[0].strip(), " ".join(names[1:]).strip()]
    else:
        return [name, ""]


def get_plant_data_query(curr, plant_dict: dict) -> dict | None:
    '''Gets the query for updating or inserting the plant.'''
    plant_id = plant_dict.get("plant_id")
    name = plant_dict.get("name")


def get_current_plant_properties(curr, plant_id: int) -> dict | None:
    """Returns the current data for a given plant_id or None if not found."""

    try:
        curr.execute(
            "SELECT location_id, last_watering,plant_species_id FROM gamma.plants WHERE plant_id = ?", (plant_id,))
        result = curr.fetchone()

    except Exception as err:
        LOGGER.error(err)
        return None

    LOGGER.info(f'Plant {plant_id} has current state {result}')

    return result


def map_plant_to_recording(curr):
    '''Returns a mapping of all plants to botanists'''
    query = """
        SELECT r.plant_id, r.recording_id, r.time, r.soil_moisture, r.temperature, r.botanist_id
        FROM gamma.recordings r
        JOIN gamma.plants p ON r.plant_id = p.plant_id
    """
    curr.execute(query)
    rows = curr.fetchall()
    return {row.plant_id: row.recording_id for row in rows}


def map_plant_to_botanist(curr):
    '''Returns a mapping of all plants to botanists'''
    query = curr.execute("""
        SELECT DISTINCT plant_id, botanist_id
        FROM gamma.recordings
    """)
    curr.execute(query)
    rows = curr.fetchall()
    return {row.plant_id: row.botanist_id for row in rows}


def get_current_botanist_properties(cursor, botanist_id: int) -> dict | None:
    """Returns the current data for a given plant_id or None if not found."""

    try:
        curr.execute(
            "SELECT * FROM gamma.botanist WHERE botanist_id = ?", (botanist_id,))
        result = curr.fetchone()

    except Exception as err:
        LOGGER.error(err)
        return None

    LOGGER.info(f'Botanist {botanist_id} has current state {result}')

    return result


def get_botanist_data(botanist_data: dict) -> dict | None:
    '''Formats the extracted json into botanist data. Returns None if a required field is missing.'''
    email = botanist_data.get("email", None)
    full_name = botanist_data.get("name", None)
    if not full_name:
        return None

    names = split_name(full_name)

    return {
        "botanist_email": email if is_valid_email(email) else None,
        "botanist_first_name": names[0],
        "botanist_last_name": names[1],
        "botanist_phone": botanist_data.get("phone", None)
    }


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    with get_connection() as conn:
        curr = conn.cursor()
        for i in range(0, 50):
            get_current_plant_properties(curr, i)
        curr.close()
