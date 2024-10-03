'''Transfroms the extracted data'''
import logging
from datetime import datetime as dt
from os import environ as ENV


import pyodbc

from dotenv import load_dotenv

from logger import logger_setup

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


def get_current_plant_properties(curr, plant_id: int) -> dict | None:
    """Returns the current data for a given plant_id or None if not found."""

    try:
        curr.execute(
            "SELECT location_id, last_watering,plant_species_id FROM gamma.plants WHERE plant_id = ?", (plant_id,))

        result = curr.fetchone()

    except Exception as err:
        LOGGER.error(err)
        return None

    return result


def map_plant_to_most_recent_botanist(cursor):
    '''Returns a mapping of all plants to the most recent botanist'''

    query = """SELECT r.plant_id, r.botanist_id
    FROM gamma.recordings r
    JOIN (
        SELECT plant_id, MAX(time_taken) AS max_time
        FROM gamma.recordings
        GROUP BY plant_id
    ) recent ON r.plant_id = recent.plant_id AND r.time_taken = recent.max_time
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    return {row[0].plant_id: row[1].botanist_id for row in rows if row}


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
    country_name = origin_location[4]

    if (not validate_latitude(lat)) or (not validate_longitude(lon)) or not all(
            isinstance(x, str) for x in [town, country_code, country_name]):
        return None

    return {
        "longitude": float(lon),
        "latitude": float(lat),
        "town": town.strip(),
        "country_code": country_code.upper().strip(),
        "country_name": country_name.split("/")[0].strip()
    }


def map_town_name_to_id(cursor) -> dict:
    '''Return a dictionary mapping country codes to country_id'''
    cursor.execute("SELECT town_name, town_id FROM gamma.regions")
    rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows if row}


def map_country_code_to_id(cursor) -> dict:
    '''Return a dictionary mapping country codes to country_id'''
    cursor.execute("SELECT country_code, country_id FROM gamma.countries")
    rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows if row}


def get_botanist_id(cursor, botanist_data: dict) -> int | None:
    '''Given information about a botanist, retrieve the botanist id from the dataframe. 
    If the botanist is not currently in the database, return None'''

    email = botanist_data["botanist_email"]

    if email:
        cursor.execute(
            "SELECT botanist_id FROM gamma.botanists WHERE email = ?", (email,)
        )
    else:
        cursor.execute(
            "SELECT botanist_id FROM gamma.botanists WHERE first_name = ? AND last_name = ?",
            (botanist_data["botanist_first_name"],
             botanist_data["botanist_last_name"])
        )

    result = cursor.fetchone()

    LOGGER.info("Botanist identified as %s", result)
    return result[0] if result else None


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    botanist = get_botanist_data(
        {'email': 'carl.linnaeus@lnhm.co.uk', 'name': 'Carl Linnaeus', 'phone': '(146)994-1635x35992'})

    with get_connection() as conn:

        conn_cursor = conn.cursor()
        map_country_code_to_id(conn_cursor)
        get_botanist_id(conn_cursor, botanist)

        conn_cursor.close()
