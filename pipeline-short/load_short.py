'''Script for loading'''
import logging

from datetime import datetime as dt

from dotenv import load_dotenv

from transform_short import map_plant_to_most_recent_botanist, get_current_plant_watering, get_botanist_data, get_botanist_id, get_connection, map_scientific_name_to_species_id, map_country_code_to_id, map_town_name_to_id, map_common_name_to_species_id, get_origin_data, map_continent_name_to_id, get_all_plant_ids, map_longitude_and_latitude_to_location_id

from logger import logger_setup

from extract_short import extract

LOGGER = logging.getLogger(__name__)


def upsert_plants(conn, curr, plant_data: list[dict]) -> None:
    """Inserts new plants into the database or updates existing ones with 
    a new watering time. 

    If a plant has a new recording, this is added."""

    plant_to_botanist = map_plant_to_most_recent_botanist(curr)

    recordings_to_insert = []
    plants_to_insert = []
    for plant in plant_data:

        if "plant_id" not in plant or not plant["plant_id"]:
            continue

        try:
            plant_id = int(plant["plant_id"])
        except:
            continue

        new_plant = upsert_plant_table(curr, plant, plant_id)

        if new_plant is not None:
            plants_to_insert.append(new_plant)

        if not (
                plant.get('soil_moisture') or plant.get("temperature")
        ) or not plant.get("botanist"):

            LOGGER.info(
                "Not enough information to insert a new recording.")

            continue

        last_botanist = plant_to_botanist.get(plant_id)

        recordings_to_insert.append(get_new_recording_table_entry(
            curr, plant_id, plant, last_botanist))

    if plants_to_insert:
        insert_new_plants(curr, plants_to_insert)
        logging.info(f"Inserting plants with id's {
            [i[0] for i in plants_to_insert]}")

        conn.commit()

    if recordings_to_insert:

        LOGGER.info(f"Inserting recordings for plants with id's {
            [i[3] for i in recordings_to_insert]}")
        insert_new_recordings(curr, recordings_to_insert)


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


def upsert_plant_table(curr, plant, plant_id: int) -> tuple | None:
    '''Decides whether to update or insert into the plant table.
    Returns the tuple to insert if a plant needs to be inserted and None otherwise.
    If a plant needs to be updated, this is handled immediately.'''

    current_plant_watering = get_current_plant_watering(curr, plant_id)

    last_watered = plant.get("last_watered", current_plant_watering)

    last_watered = dt.strptime(
        last_watered, '%a, %d %b %Y %H:%M:%S %Z') if isinstance(last_watered, str) else last_watered

    if not current_plant_watering:
        return get_new_plant_table_entry(curr, plant, plant_id, last_watered)

    if last_watered != current_plant_watering:
        update_plant_watered(curr, plant_id, last_watered)

    return None


def get_new_plant_table_entry(cursor, plant_data: dict, plant_id: int, last_watering: dt) -> tuple | None:
    '''Generates a tuple containing (plant_id, location_id, plant_species_id, last_watering).
    If any required fields are missing, None is returned'''
    scientific_name_to_species_id = map_scientific_name_to_species_id(cursor)
    country_code_to_country_id = map_country_code_to_id(cursor)
    town_name_to_region_id = map_town_name_to_id(cursor)
    common_name_to_species_id = map_common_name_to_species_id(cursor)
    continent_name_to_continent_id = map_continent_name_to_id(cursor)
    location_map = map_longitude_and_latitude_to_location_id(cursor)

    species_id = insert_into_species_table(
        cursor, plant_data, scientific_name_to_species_id, common_name_to_species_id, plant_data["name"])

    origin_data = get_origin_data(plant_data["origin_location"])
    if not origin_data:
        return None
    town_id = town_name_to_region_id.get(origin_data["town"])

    coords = (origin_data["longitude"],
              origin_data["latitude"])

    if not town_id:
        town_id = insert_into_regions_table(
            cursor, origin_data["town"], continent_name_to_continent_id[origin_data["continent_name"]], country_code_to_country_id[origin_data["country_code"]])

    if not coords in location_map.keys():
        location_id = insert_into_locations_table(
            cursor, *coords, town_id)
    else:
        location_id = location_map[coords]

    return (plant_id, location_id, species_id, last_watering)


def get_new_recording_table_entry(cursor, plant_id: int, plant_data: dict, last_botanist_id: int) -> tuple:
    '''Returns the details needed to update the recording table.'''

    recording_taken = plant_data.get("recording_taken")

    recording_taken = dt.strptime(
        recording_taken, '%Y-%m-%d %H:%M:%S') if recording_taken else dt.now()

    botanist_details = get_botanist_data(plant_data["botanist"])

    existing_id = get_botanist_id(cursor, botanist_details)

    if botanist_details is None and last_botanist_id is not None:

        botanist_id = last_botanist_id

    elif existing_id:
        botanist_id = existing_id
    else:
        botanist_id = insert_new_botanist(cursor, botanist_details)

    return (recording_taken, plant_data["soil_moisture"], plant_data["temperature"], plant_id, botanist_id)


def insert_into_species_table(cursor, plant_data: dict, scientific_names_to_id: dict, common_names_to_id: dict, common_name: str) -> int:
    '''Returns the details needed to insert information into the species_id table as a tuple and returns the new ID
    If a species already exists, return the existing species_id
    If a species does not exist, and plant_data doesn't have a scientific name, this defaults to the common name. '''
    scientific_names = list(plant_data.get('scientific_name', []))

    for name in [common_name, *scientific_names]:
        match = scientific_names_to_id.get(name.lower().strip(), False)

        match = match if match else common_names_to_id.get(
            name.lower().strip(), False)

        if match:
            return match

    query = """INSERT INTO gamma.plant_species (common_name, scientific_name)
    OUTPUT inserted.plant_species_id
    VALUES (?, ?);"""

    scientific_name = scientific_names[0].strip(
    ) if scientific_names else common_name

    cursor.execute(query, (common_name.title(), scientific_name.title()))

    species_id = cursor.fetchone()

    return species_id


def insert_into_regions_table(cursor, town: str, continent_id: int, country_id: int) -> int:
    '''Inserts into regions table and returns the new region id. 
    If a region already exists in the database, return the current region id'''
    query_insert = """
    INSERT INTO gamma.regions (town_name, continent_id, country_id)
    OUTPUT inserted.town_id
    VALUES (?, ?, ?);
    """
    cursor.execute(query_insert, (town, continent_id, country_id))
    region_id = cursor.fetchone()[0]

    return region_id


def insert_into_locations_table(cursor, longitude: float, latitude: float, town_id: int) -> int:
    '''Inserts into the locations table and returns the new origin_id'''
    query_insert = """
    INSERT INTO gamma.origins (longitude, latitude, town_id)
    OUTPUT inserted.location_id
    VALUES (?, ?, ?);
    """
    cursor.execute(query_insert, (longitude, latitude, town_id))
    new_id = cursor.fetchone()[0]

    return new_id


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


def insert_new_plants(cursor, plant_data_to_insert: list[tuple]):
    '''Using a list of tuples containing (plant_id, location_id, plant_species_id,last_watering), inserts many new plants.'''

    cursor.executemany(
        """
            INSERT INTO gamma.plants (plant_id, location_id, plant_species_id,last_watering)
            VALUES (?, ?, ?, ?)
        """,
        plant_data_to_insert
    )


def insert_new_botanist(cursor, botanist_data: dict) -> int:
    '''Given information about a botanist, insert a new botanist and return the new ID. '''
    query = """
    INSERT INTO gamma.botanists (first_name, last_name, email, phone)
    OUTPUT inserted.botanist_id
    VALUES (?, ?, ?, ?);
    """
    cursor.execute(
        query, (
            botanist_data['botanist_first_name'],
            botanist_data['botanist_last_name'],
            botanist_data['botanist_email'],
            botanist_data['botanist_phone'])
    )

    return cursor.fetchone()[0]


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")
    data = extract()

    with get_connection() as conn:

        conn_cursor = conn.cursor()
        upsert_plants(conn, conn_cursor, data)
        conn.commit()
        conn_cursor.close()
