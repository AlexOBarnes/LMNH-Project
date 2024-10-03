'''Transfroms the extracted data'''
import logging
from datetime import datetime as dt
from os import environ as ENV


import pyodbc

from dotenv import load_dotenv

from logger import logger_setup
from database_functions import map_botanist_details_to_id, map_continent_name_to_id, map_country_code_to_id, map_longitude_and_latitude_to_location_id, map_plant_id_to_most_recent_botanist, map_species_names_to_species_id, map_town_name_to_id

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


def get_origin_data(origin_location: list, coordinate_map: dict, continent_map: dict, country_map: dict, town_map: dict) -> dict | None:
    '''Formats the extracted json to get available origin data. 
    Returns None if a required field is missing or invalid'''

    if not len(origin_location) == 5:
        return None

    lon, lat = origin_location[0], origin_location[1]
    town = origin_location[2]
    country_code = origin_location[3].upper()
    continent_name = origin_location[4]

    if (not validate_latitude(lat)) or (not validate_longitude(lon)):
        return None

    if (lon, lat) in coordinate_map.keys():
        return {"to_insert": False, "location_id": coordinate_map[(lon, lat)]}

    else:

        if town in town_map.keys():
            return {"to_insert": True,
                    "town_id": town_map[town],
                    "longitude": lon,
                    "latitude": lat}
        else:
            return {"to_insert": True,
                    "longitude": lon,
                    "latitude": lat,
                    "town_name": town,
                    "continent_id": continent_map[continent_name],
                    "country_id": country_map[country_code]
                    }


def get_botanist_data(botanist_data: dict, all_botanists: dict) -> dict | None:
    '''Formats the extracted json into botanist data.'''

    if not {"email", "phone", "name"} in set(botanist_data.keys()):
        return None

    email = botanist_data["email"]
    phone = botanist_data["phone"]
    names = split_name(botanist_data["name"])

    if (email, names[0], names[1]) in all_botanists:
        return {"to_insert": False, "botanist_id": all_botanists[(email, names[0], names[1])]}

    if not names[0] or not names[1] or not is_valid_email(email):
        return None

    return {"to_insert": True, "email": email, "phone": phone, "first_name": names[0], "last_name": names[1]}


def get_species_data(plant_data: dict, all_names: dict) -> dict | None:
    '''Formats the extracted json into species data.'''
    if not "name" in plant_data:
        return None

    common_name = plant_data["name"].strip().title()
    scientific_names = [i.strip().title()
                        for i in plant_data.get('scientific_name', [])]

    for name in [common_name, *scientific_names]:

        if name in all_names["scientific_name"].keys():
            return {"to_insert": False, "plant_species_id": all_names["scientific_name"][name]}
        if name in all_names["common_name"].keys():
            return {"to_insert": False, "plant_species_id": all_names["common_name"][name]}

    return {"to_insert": True, "common_name": common_name, "scientific_name": scientific_names[0] if scientific_names else common_name}


def transform_plant_data(extracted_data: list[dict]):
    '''Transforms the extracted plant data'''

    for plant in extracted_data:
        ...


if __name__ == "__main__":
    load_dotenv()
    logger_setup("log_transform.log", "logs")

    botanist = get_botanist_data(
        {'email': 'carl.linnaeus@lnhm.co.uk', 'name': 'Carl Linnaeus', 'phone': '(146)994-1635x35992'})

    with get_connection() as conn:

        conn_cursor = conn.cursor()

        conn_cursor.close()
