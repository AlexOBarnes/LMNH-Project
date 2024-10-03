"""A file for extracting data older than 24 hours from the RDS
into a CSV to be stored in an S3 bucket."""

from os import environ as ENV
import pyodbc
from dotenv import load_dotenv


def connect_to_rds(db_host: str, db_user: str, db_password: str, db_name: str) -> pyodbc.Connection | None:
    """Connects to an RDS database using pyodbc."""

    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={db_host};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password}"
        )
        
        connection = pyodbc.connect(connection_string)
        return connection
    
    except pyodbc.Error as e:
        print(f"Error connecting to RDS: {e}")
        return None
    

def extract_plant_data(connection: pyodbc.Connection | None) -> list[dict[str, any]]:
    """Extracts plant data older than 24 from the RDS."""
    
    if connection is None:
        return []
    
    query = """
    SELECT recording_id, time_taken, soil_moisture, temperature, plant_id, botanist_id
    FROM gamma.recordings
    WHERE time_taken < DATEADD(HOUR, -24, GETDATE());
    """

    try:
        cur = connection.cursor()
        cur.execute(query)
        result = cur.fetchall()

        columns = [column[0] for column in cur.description]
        data = [dict(zip(columns, row)) for row in result]

    except pyodbc.Error as e:
        print(f"Error querying data: {e}")
        return []
    
    finally:
        connection.close()

    return data


if __name__ == "__main__":

    load_dotenv()

    DB_HOST = ENV["DB_HOST"]
    DB_USER = ENV["DB_USER"]
    DB_PASSWORD = ENV["DB_PASSWORD"]
    DB_NAME = ENV["DB_NAME"]

    conn = connect_to_rds(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    plant_data = extract_plant_data(conn)

    if plant_data:
        for row in plant_data[:5]:
            print(row)

    else:
        print("No data extracted.")
