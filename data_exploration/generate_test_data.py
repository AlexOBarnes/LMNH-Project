'''This module creates test data and loads it onto the long term storage S3'''
from os import environ as ENV
import argparse
from datetime import datetime as dt
from io import StringIO
import random
from dotenv import load_dotenv
import pandas as pd
from boto3 import client



def parse_arguments() -> int:
    '''Parses command line arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", "-r", type=int, default=50,
                        help="""Enter the number of rows you want the end csv file to be""")
    args = parser.parse_args()
    rows = args.rows


    return rows

def create_plant_dataframe(rows:int) -> pd.DataFrame:
    '''Returns a pandas dataframe containing fake data'''
    data = []
    for i in range(1, rows+1):
        timestamp = dt.now()
        moisture= round(random.uniform(0.0, 100.0), 3)
        temperature = round(random.uniform(0.0, 40.0), 3)
        plant = random.randint(1, 3)
        botanist = random.randint(1, 3)
        data.append([i, timestamp.strftime('%y-%m-%d %H:%M:%S'),
                    moisture, temperature, plant, botanist])


    return pd.DataFrame(data, columns=['recording_id', 'timestamp',
                                       'moisture', 'temperature',
                                       'plant_id', 'botanist_id'])

def upload_data(data: pd.DataFrame) -> None:
    '''Uploads data to S3 as a CSV'''
    aws_client = client(service_name="s3",
                        aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                        aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

    date = dt.now().strftime('%d-%m-%Y')

    csv_file = StringIO()
    data.to_csv(csv_file, index=False)
    encoded_csv = csv_file.getvalue().encode('UTF-8')

    aws_client.put_object(Bucket=ENV["BUCKET"],
                          Key=f'recordings/{date}.csv', Body=encoded_csv)




if __name__ == '__main__':
    load_dotenv()
    iterations = parse_arguments()
    plant_df = create_plant_dataframe(iterations)
    upload_data(plant_df)
