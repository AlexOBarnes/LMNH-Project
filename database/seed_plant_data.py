'''This script seeds the RDS SQL server database with plant data'''
from os import environ as ENV
import requests as req
from pyodbc import connect
from dotenv import load_dotenv
import pandas as pd

BASE_URL = "https://data-eng-plants-api.herokuapp.com/plants/"

def get_connection() -> connect.Connection:
    '''Returns a connection to the RDS database'''
    return connect(f"DRIVER={{SQL Server}};"
                   f"SERVER={ENV['HOST']},{ENV['DB_PORT']};"
                   f"DATABASE={ENV['DB_NAME']};"
                   f"UID={ENV['DB_USER']};"
                   f"PWD={ENV['DB_PW']}")


def get_plant_data() -> pd.DataFrame:
    '''Extracts data from endpoints'''
    pass

def insert_data() -> None:
    '''Inserts plant data from endpoints'''
    pass

def transform(plants:pd.DataFrame) -> pd.DataFrame:
    '''Extracts key data and formats data ready for insertion'''
    pass

def pipeline() -> None:
    '''Runs the ETL pipeline for the plant data'''
    pass

if __name__ == '__main__':
    pipeline()
