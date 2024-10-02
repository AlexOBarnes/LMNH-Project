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


def split_data(plant_data: dict) -> dict[dict]:
    '''Splits the plant data into dictionaries for different tables'''
    return {"botanist": get_botanist_data(plant_data["botanist"]), "plant": get_plant_data(plant_data)}


def get_plant_data(plant_dict: dict):
    '''Gets plant data, including validation.'''


def get_current_last_watered(cursor, plant_id: int, last_watered_entry: str | None) -> None:
    """Returns the current last_watering entry"""

    try:
        curr.execute(
            "SELECT last_watering FROM gamma.plants WHERE plant_id = ?", (plant_id,))
        result = curr.fetchone()
    except Exception as err:
        LOGGER.error(err)
        return

    LOGGER.info(f'Plant {plant_id} has last_watering {result}')

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


def load_data_into_df(data: list[dict]):
    '''Loads the data into a dataframe'''


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    with get_connection() as conn:
        curr = conn.cursor()
        for i in range(0, 50):
            get_current_last_watered(curr, i, last_watered_entry=None)
        curr.close()
