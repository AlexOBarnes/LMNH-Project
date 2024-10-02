'''Transfroms the extracted data'''
import logging
from datetime import datetime as dt
from os import environ as ENV

import pyodbc

from dotenv import load_dotenv

from logger import logger_setup

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

    except Exception as err:
        LOGGER.error(f"Error connecting to RDS %s: ", err)
        raise err


def upsert_plants(curr, plant_data: list[dict]) -> None:
    """Inserts new plants into the database or updates existing ones."""

    plant_to_botanist = map_plant_to_botanist()

    plant_to_recording = map_plant_to_recording()

    for plant in plant_data:

        try:
            plant_id = plant["plant_id"]
        except:
            continue

        upsert_plant_table(curr, plant, plant_id)

        try:
            botanist = plant["botanist"]
        except:
            continue

        try:
            temp = plant["temperature"]
            moisture = plant['soil_moisture']

        except:
            continue

        recording_taken = plant.get("recording_taken")

        recording_taken = dt.strptime(
            recording_taken, '%Y-%m-%d %H:%M:%S') if recording_taken else dt.now()

        recording_id = plant_to_recording[plant]
        botanist_id = plant_to_botanist[plant]

        if not botanist_id:
            insert_botanist(curr, plant)

        if not recording_id:
            insert_recording(curr, plant)

        botanist_data = get_botanist_data(botanist)

        # TODO: process botanist


def upsert_plant_table(curr, plant, plant_id) -> None:
    '''Updates or inserts into the plant table'''

    last_watered = plant.get("last_watered")

    last_watered = dt.strptime(
        last_watered, '%a, %d %b %Y %H:%M:%S %Z') if last_watered else dt.now()

    current_plant = get_current_plant_properties(curr, plant_id)

    if not current_plant:
        insert_new_plant(curr, plant)

    curr_last_watered = current_plant["last_watering"]

    if not curr_last_watered and not last_watered:
        return

    if last_watered:
        update_plant_watered(curr, plant_id, last_watered)


def upsert_recordings_table(curr, plant, plant_id, plant_to_recordings, plant_to_botanists):
    '''Update or insert into the recordings table'''


def insert_recording(cursor, plant_data):
    '''Insert a new recording'''


def insert_botanist(cursor, plant_data):
    '''Insert a new recording'''


def update_recording(cursor, plant_id, recording_id)


def update_plant_watered(cursor, plant_id_to_update, new_last_watered):
    '''Update a plant's last_watering entry'''

    cursor.execute(
        """
            UPDATE gamma.plants
            SET last_watering = ?
            WHERE plant_id = ?
            """,
        (new_last_watered, plant_id_to_update)
    )


def insert_new_plant(cursor, plant_dict):
    '''Using a plant dictionary, inserts a new plant.'''
    cursor.execute(
        """
            INSERT INTO gamma.plants (plant_id, name, last_watering)
            VALUES (?, ?, ?)
            """,
        (plant_dict['plant_id'], plant_dict['name'],
         plant_dict.get('last_watered'))
    )


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


def get_current_botanist_properties(curr, botanist_id: int) -> dict | None:
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


def upsert_botanist(botanist: dict) -> dict | None:
    '''Given an extracted botanist, '''


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    with get_connection() as conn:
        curr = conn.cursor()
        for i in range(0, 50):
            get_current_plant_properties(curr, i)
        curr.close()
