'''Transfroms the extracted data'''
import logging
from datetime import datetime as dt
from os import environ as ENV


import pyodbc

from dotenv import load_dotenv

from logger import logger_setup
from database_functions import map_botanist_details_to_id, map_common_name_to_species_id, map_continent_name_to_id, map_country_code_to_id, map_longitude_and_latitude_to_location_id, map_plant_id_to_most_recent_botanist, map_scientific_name_to_species_id, map_town_name_to_id

LOGGER = logging.getLogger(__name__)


def get_connection():
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

    except Exception as err:
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

    return [name, ""]


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


def validate_longitude(longitude: str) -> bool:
    '''Return True if a longitude string is valid'''
    try:
        lon = float(longitude)
        return -180 <= lon <= 180
    except ValueError:
        return False


def validate_latitude(latitude: str) -> bool:
    '''Return True if a latitude string is valid'''
    try:
        lat = float(latitude)
        return -90 <= lat <= 90
    except ValueError:
        return False


def get_origin_data(origin_location: list) -> dict | None:
    '''Formats the extracted json to get available origin data. 
    Returns None if a required field is missing or invalid'''

    if not len(origin_location) == 5:
        return None

    lon, lat = origin_location[0], origin_location[1]
    town = origin_location[2]
    country_code = origin_location[3]
    continent_name = origin_location[4]

    if (not validate_latitude(lat)) or (not validate_longitude(lon)) or not all(
            isinstance(x, str) for x in [town, country_code, continent_name]):
        return None

    return {
        "longitude": float(lon),
        "latitude": float(lat),
        "town": town.strip(),
        "country_code": country_code.upper().strip(),
        "continent_name": continent_name.split("/")[0].strip()
    }


def transform_plant_data(extracted_data: list[dict]):
    '''Transforms the extracted plant data'''


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    botanist = get_botanist_data(
        {'email': 'carl.linnaeus@lnhm.co.uk', 'name': 'Carl Linnaeus', 'phone': '(146)994-1635x35992'})

    with get_connection() as conn:

        conn_cursor = conn.cursor()

        conn_cursor.close()
