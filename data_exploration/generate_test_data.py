'''This module creates test data and loads it onto the long term storage S3'''
from os import environ as ENV
import argparse
from datetime import datetime, timedelta
from io import StringIO
import random
from dotenv import load_dotenv
import pandas as pd
from pyodbc import connect
from boto3 import client

INVALID_KEYS = [1,7,10,13,15,18,23,24,27,37,40,43]

def get_connection():
    '''Returns a connection to the RDS database'''
    return connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                   f"SERVER={ENV['HOST']},{ENV['DB_PORT']};"
                   f"DATABASE={ENV['DB_NAME']};"
                   f"UID={ENV['DB_USER']};"
                   f"PWD={ENV['DB_PW']}")


def parse_arguments() -> int:
    '''Parses command line arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", "-r", type=int, default=50,
                        help="""Enter the number of rows you want the end csv file to be""")
    parser.add_argument('--database','-d',action='store_true',
                        help='Use this flag to input data into the database')
    args = parser.parse_args()
    rows = args.rows
    destination = args.database


    return rows,destination

def create_plant_dataframe(rows:int) -> pd.DataFrame:
    '''Returns a pandas dataframe containing fake data'''
    data = []
    valid_plant_ids = [i for i in range(50) if i not in INVALID_KEYS]
    last_watered = datetime.now()-timedelta(days=1)
    for i in range(1, rows+1):
        timestamp = datetime.now()+timedelta(minutes=i)
        moisture= round(random.uniform(20.0, 80.0), 3)
        temperature = round(random.uniform(0.0, 30.0), 3)
        plant = random.choice(valid_plant_ids)
        botanist = random.randint(1, 3)
        data.append([i, timestamp,
                    moisture, temperature, plant, botanist,last_watered])


    return pd.DataFrame(data, columns=['recording_id', 'timestamp',
                                       'moisture', 'temperature',
                                       'plant_id', 'botanist_id','last_watering'])

def upload_data_csv(data: pd.DataFrame) -> None:
    '''Uploads data to S3 as a CSV'''
    aws_client = client(service_name="s3",
                        aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                        aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

    date = datetime.now().strftime('%d-%m-%Y')

    csv_file = StringIO()
    data.to_csv(csv_file, index=False)
    encoded_csv = csv_file.getvalue().encode('UTF-8')

    aws_client.put_object(Bucket=ENV["BUCKET"],
                          Key=f'recordings/{date}.csv', Body=encoded_csv)

def upload_data_db(data: pd.DataFrame) -> None:
    '''Uploads data to the RDS database'''
    q = '''INSERT INTO gamma.recordings
    (soil_moisture,temperature,plant_id,botanist_id,last_watering)
    VALUES (?,?,?,?,?)'''
    plant_data = data.drop(columns=['recording_id','timestamp']).values.tolist()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(q,plant_data)
            conn.commit()



if __name__ == '__main__':
    load_dotenv()
    iterations,database = parse_arguments()
    plant_df = create_plant_dataframe(iterations)
    if database:
        upload_data_db(plant_df)
    else:
        upload_data_csv(plant_df)
