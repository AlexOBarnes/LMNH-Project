'''Transfroms the extracted data'''
import logging
from datetime import datetime as dt
from os import environ as ENV


import pyodbc

from dotenv import load_dotenv

from logger import logger_setup
from database_functions import map_botanist_details_to_id, map_longitude_and_latitude_to_location_id, map_species_names_to_species_id, map_town_name_to_id, get_all_plant_ids, get_max_location_id

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
        return [names[0].strip().title(), " ".join(names[1:]).strip().title()]

    return [name, ""]


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


def validate_origin_data(origin_data: list) -> bool:
    '''Validates origin data extracted from the API'''
    lon, lat = origin_data[0], origin_data[1]
    return (len(origin_data) == 5) and (not validate_latitude(lat)) and (not validate_longitude(lon))


def get_botanist_id(botanist_data: dict, all_botanists: dict) -> int:
    '''Formats the extracted json into botanist data.'''

    email = botanist_data["email"]
    phone = botanist_data["phone"]
    names = split_name(botanist_data["name"])

    if (email, names[0], names[1]) in all_botanists:
        return all_botanists[(email, names[0], names[1])]

    raise ValueError("Botanist not available.")


def get_species_id(plant_data: dict, all_names: dict) -> int:
    '''Formats the extracted json into species data.'''

    common_name = plant_data["name"].strip().title()
    scientific_names = [i.strip().title()
                        for i in plant_data.get('scientific_name', [])]

    for name in [common_name, *scientific_names]:
        if name in all_names["scientific_name"].keys():
            return all_names["scientific_name"][name]
        if name in all_names["common_name"].keys():
            return all_names["common_name"][name]

    raise ValueError("Species not available")


def validate_plant(plant: dict, all_plant_ids: list[int]) -> bool:
    '''Validates a plant extracted from the API'''
    valid_keys = {"botanist", "name", "plant_id",
                  "soil_moisture", "temperature", "last_watered", "recording_taken"}

    if not valid_keys:
        return False

    botanist = plant.get("botanist", dict())
    valid_email = is_valid_email(botanist.get("email", ""))
    valid_botanist = {"name", "phone", "email"} in botanist.keys()

    if plant["plant_id"] in all_plant_ids:
        return valid_email and valid_botanist

    origin_data = plant.get("origin_data")
    if not origin_data:
        return False

    valid_location = validate_origin_data(origin_data)

    return valid_email and valid_botanist and valid_location


def clean_plants(plants: list[dict], existing_ids: list[int]):
    return list(filter(lambda x: validate_plant(x, existing_ids), plants))


def transform_plant_data(conn, extracted_data: list[dict]):
    '''Transforms the extracted plant data. Returns lists containing the data that needs to be bulk inserted into the database.
    '''
    curr = conn.cursor()

    locations_to_insert = []
    plants_to_insert = []
    readings_to_insert = []

    all_ids = get_all_plant_ids(curr)

    plants = clean_plants(extracted_data, all_ids)

    botanists = map_botanist_details_to_id(curr)
    towns = map_town_name_to_id(curr)
    species = map_species_names_to_species_id(curr)
    coord_map = map_longitude_and_latitude_to_location_id(curr)

    next_location_id = get_max_location_id(curr) + 1
    for p in plants:
        p_id = p["plant_id"]
        try:
            botanist_id = get_botanist_id(p["botanist"], botanists)
        except KeyError:
            continue

        recording_taken = dt.strptime(
            p["recording_taken"], '%Y-%m-%d %H:%M:%S')

        readings_to_insert += [(recording_taken,
                                p["soil_moisture"], p["temperature"], botanist_id)]

        if p not in all_ids:
            try:
                species_id = get_species_id(p, species)
            except KeyError:
                continue

            origin_location = p["origin_location"]
            lon, lat = origin_location[0], origin_location[1]
            town = origin_location[2]

            try:
                location_id = coord_map[(lon, lat)]
                plants_to_insert += [(p_id, location_id, species_id)]
            except KeyError:
                town_id = towns.get(town)
                if not town_id:
                    continue
                locations_to_insert += [(lon, lat, town_id)]
                location_id = next_location_id

                next_location_id += 1
            plants_to_insert += [(location_id, species_id)]
    return plants_to_insert, locations_to_insert, readings_to_insert


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    with get_connection() as conn:

        conn_cursor = conn.cursor()

        conn_cursor.close()
