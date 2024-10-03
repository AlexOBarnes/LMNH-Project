import logging
import pyodbc

LOGGER = logging.getLogger(__name__)


def map_plant_id_to_most_recent_botanist(cursor):
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

    return {row[0]: row[1] for row in rows if row}


def map_botanist_details_to_id(cursor) -> dict:
    '''Maps (botanist_email,first_name,last_name): botanist_id'''

    cursor.execute(
        "SELECT botanist_id, email, first_name, last_name FROM gamma.botanists"
    )

    result = cursor.fetchall()

    return {(row[1], row[2], row[3]): row[0] for row in result if row}


def map_town_name_to_id(cursor) -> dict:
    '''Return a dictionary mapping country codes to country_id'''
    cursor.execute("SELECT town_name, town_id FROM gamma.regions")
    rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows if row}


def map_species_names_to_species_id(cursor) -> dict:
    '''Return a dictionary mapping scientific_name to species_id'''

    cursor.execute(
        "SELECT plant_species_id, scientific_name, common_name FROM gamma.plant_species")

    rows = cursor.fetchall()

    return {
        "scientific_name": {row[1].strip().title(): row[0] for row in rows if row},
        "common_name": {row[2].strip().title(): row[0] for row in rows if row}
    }


def map_country_code_to_id(cursor) -> dict:
    '''Return a dictionary mapping country codes to country_id'''
    cursor.execute("SELECT country_code, country_id FROM gamma.countries")
    rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows if row}


def map_longitude_and_latitude_to_location_id(cursor) -> dict:
    '''Return a dictionary mapping (longitude, latitude) tuples to origin_id'''
    cursor.execute("SELECT longitude,latitude,location_id FROM gamma.origins")
    rows = cursor.fetchall()
    return {(row[0], row[1]): row[2] for row in rows}


def map_continent_name_to_id(cursor) -> dict:
    '''Return a dictionary mapping continent_names to continent_ids'''
    cursor.execute("SELECT continent_name, continent_id FROM gamma.continents")
    rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows if row}
