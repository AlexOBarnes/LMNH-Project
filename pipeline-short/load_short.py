'''Script for loading'''
import logging

from datetime import datetime as dt

from dotenv import load_dotenv

from transform_short import transform_plant_data, get_connection

from logger import logger_setup

from extract_short import extract

LOGGER = logging.getLogger(__name__)


def load():
    with get_connection() as conn:
        extracted_data = extract()
        plants_to_insert, locations_to_insert, readings_to_insert = transform_plant_data(
            conn, extracted_data)
        cur = conn.cursor()
        insert_into_locations_table(cur, locations_to_insert)
        conn.commit()
        insert_new_recordings(cur, readings_to_insert)
        conn.commit()
        insert_new_plants(cur, plants_to_insert)
        conn.commit()

        cur.close()


def insert_new_recordings(cursor, recordings: list[tuple]):
    '''Given a list of tuples of the form
      (time_taken, soil_moisture, temperature, plant_id, botanist_id)
      insert the new recordings into the database.'''

    cursor.executemany("""
     INSERT INTO gamma.recordings
        (time_taken, soil_moisture,temperature,plant_id,botanist_id)
     VALUES
        (?,?,?,?,?)
     """, recordings)


def insert_into_locations_table(cursor, locations: list[tuple]) -> int:
    '''Bulk inserts into the locations table'''

    query_insert = """
    INSERT INTO gamma.origins (longitude, latitude, town_id)
    OUTPUT inserted.location_id
    VALUES (?, ?, ?);
    """

    cursor.executemany(query_insert, locations)


def insert_new_plants(cursor, plant_data_to_insert: list[tuple]):
    '''Using a list of tuples containing (plant_id, location_id, plant_species_id,last_watering), inserts many new plants.'''

    cursor.executemany(
        """
            INSERT INTO gamma.plants (plant_id, location_id, plant_species_id,last_watering)
            VALUES (?, ?, ?, ?)
        """,
        plant_data_to_insert
    )


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")
    load()
