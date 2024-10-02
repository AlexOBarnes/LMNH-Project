'''Transfroms the extracted data'''
import logging
from datetime import datetime as dt
from os import environ as ENV


import pyodbc

from dotenv import load_dotenv

from logger import logger_setup
from extract import extract

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


def upsert_plants(curr, plant_data: list[dict]) -> None:
    """Inserts new plants into the database or updates existing ones with 
    a new watering time. 

    If a plant has a new recording, this is added."""

    plant_to_botanist = map_plant_to_most_recent_botanist(curr)

    recordings_to_insert = []
    for plant in plant_data:

        try:
            plant_id = plant["plant_id"]
        except:
            continue

        upsert_plant_table(curr, plant, plant_id)

        if not (
                plant.get('soil_moisture') or plant.get("temperature")
        ) or not plant.get("botanist"):
            LOGGER.info(
                "Not enough information to insert a new recording.")
            continue

        last_botanist = plant_to_botanist.get(plant_id)

        recordings_to_insert.append(get_new_recording_table_entry(
            curr, plant_id, plant, last_botanist))

    insert_new_recordings(curr, recordings_to_insert)


def insert_new_recordings(cursor, recordings: list[tuple]):
    '''Given a list of tuples of the form
      (time, soil_moisture, temperature, plant_id, botanist_id)
      insert the new recordings into the database.'''

    cursor.execute_many("""
    INSERT INTO gamma.recordings
        (time, soil_moisture,temperature,plant_id,botanist_id)
    VALUES 
        (?,?,?,?,?)
    """, recordings)
    cursor.commit()


def upsert_plant_table(curr, plant, plant_id) -> None:
    '''Updates or inserts into the plant table'''

    last_watered = plant.get("last_watered")

    last_watered = dt.strptime(
        last_watered, '%a, %d %b %Y %H:%M:%S %Z') if last_watered else None

    current_plant = get_current_plant_properties(curr, plant_id)

    if not current_plant:
        insert_new_plant(curr, plant)

    curr_last_watered = current_plant["last_watering"]

    if not curr_last_watered and not last_watered:
        return

    if last_watered:
        update_plant_watered(curr, plant_id, last_watered)


def get_new_recording_table_entry(cursor, plant_id: int, plant_data: dict, last_botanist_id: int) -> tuple:
    '''Returns the details needed to update the recording table.'''

    recording_taken = plant_data.get("recording_taken")

    recording_taken = dt.strptime(
        recording_taken, '%Y-%m-%d %H:%M:%S') if recording_taken else dt.now()

    botanist_details = get_botanist_data(plant_data["botanist"])

    existing_id = get_botanist_id(botanist_details, botanist_details)

    if botanist_details is None and last_botanist_id is not None:

        botanist_id = last_botanist_id

    elif existing_id:
        botanist_id = existing_id
    else:
        botanist_id = insert_new_botanist(cursor, botanist_details)

    return (recording_taken, plant_data["soil_moisture"], plant_data["temperature"], plant_id, botanist_id)


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
        SELECT plant_id, MAX(time) AS max_time
        FROM gamma.recordings
        GROUP BY plant_id
    ) recent ON r.plant_id = recent.plant_id AND r.time = recent.max_time
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    return {row[0].plant_id: row[1].botanist_id for row in rows}


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
    return result[0] if result else None


def insert_new_botanist(cursor, botanist_data: dict) -> int:
    '''Given information about a botanist, insert a new botanist and return the new ID. '''
    query = """
    INSERT INTO gamma.botanists (first_name, last_name, email, phone)
    VALUES (?, ?, ?, ?);
    
    SELECT SCOPE_IDENTITY();
    """
    cursor.execute(
        query, (botanist_data['botanist_first_name'], botanist_data['botanist_last_name'], botanist_data['botanist_email'], botanist_data['botanist_phone']))

    cursor.commit()
    return cursor.fetchone()[0]


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    data = extract()

    with get_connection() as conn:

        conn_cursor = conn.cursor()
        upsert_plants(conn_cursor, data)

        conn_cursor.close()
