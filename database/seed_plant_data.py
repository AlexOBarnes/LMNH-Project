'''This script seeds the RDS SQL server database with plant data'''
from os import environ as ENV
import logging
from datetime import datetime as dt
import requests as req
from pyodbc import connect
from dotenv import load_dotenv
import pandas as pd

BASE_URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def get_connection():
    '''Returns a connection to the RDS database'''
    return connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                   f"SERVER={ENV['HOST']},{ENV['DB_PORT']};"
                   f"DATABASE={ENV['DB_NAME']};"
                   f"UID={ENV['DB_USER']};"
                   f"PWD={ENV['DB_PW']}")


def extract_date(timestamp: str) -> dt:
    '''Uses datetime to extract datetime object'''
    return dt.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")


def find_location_id(location_data: list) -> int:
    '''Returns the location id for a set of longitude and latitude'''
    q = '''SELECT location_id
        FROM gamma.origins
        WHERE longitude = ? AND latitude = ?'''
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (float(location_data[0]), float(location_data[1])))
            identity = cur.fetchone()

    if identity:
        logging.info('Location ID found.')
        return identity[0]

    logging.info('Location ID not found.')
    return None


def find_species_id(name: list) -> int:
    '''Returns the location id for a set of longitude and latitude'''
    q = '''SELECT plant_species_id
        FROM gamma.plant_species
        WHERE LOWER(common_name) LIKE LOWER(?)'''
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (f'%{name}%',))
            identity = cur.fetchone()
    if identity:
        logging.info('Species ID found.')
        return identity[0]

    logging.info('Species ID not found.')
    return None


def extract_plant_data(plant: dict) -> dict:
    '''Takes in the response and returns a cleaned dict'''
    return [plant.get('plant_id', None),
            extract_date(plant.get('last_watered', None)),
            find_location_id(plant.get('origin_location', None)),
            find_species_id(plant.get('name', None))]


def get_plant_data() -> pd.DataFrame:
    '''Extracts data from endpoints'''
    data = []
    for i in range(50):
        response = req.get(BASE_URL+f'{i}', timeout=10)
        logging.info('Request for endpoint: %s', i)
        if response.status_code == 200:
            data.append(extract_plant_data(response.json()))
            logging.info('Data acquired for endpoint: %s.', i)

    return data


def insert_data(plant_data) -> None:
    '''Inserts plant data from endpoints'''
    q = '''INSERT INTO gamma.plants
    (plant_id,last_watering,location_id,plant_species_id)
    VALUES (?,?,?,?)'''
    with get_connection() as conn:
        logging.info('Connection established.')
        with conn.cursor() as cur:
            logging.info('Cursor created.')
            cur.executemany(q, plant_data)
            conn.commit()
            logging.info('Insertion committed.')


def pipeline() -> None:
    '''Runs the ETL pipeline for the plant data'''
    load_dotenv()
    data = [plant for plant in get_plant_data() if None not in plant]
    logging.info('Data filtered.')
    logging.info('Data to be inserted: %s', len(data))
    insert_data(data)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    pipeline()
