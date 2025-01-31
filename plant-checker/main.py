'''Checks and alerts whether the plant conditions are optimal'''
#pylint: disable=E0611,W0613,W0612
from os import environ as ENV
import logging
from datetime import datetime as dt
from dotenv import load_dotenv
from pymssql import connect
from boto3 import client

def get_date() -> str:
    '''Returns current time'''
    return dt.now().strftime('%A %d %B %Y @ %H:%M:%S ')

def get_connection():
    '''Returns a pyodbc connections'''
    return connect(server=ENV["DB_HOST"],
                   port=ENV["DB_PORT"],
                   user=ENV["DB_USER"],
                   password=ENV["DB_PASSWORD"],
                   database=ENV["DB_NAME"],
                   as_dict=True)

def get_affected_plants() -> list[int]:
    '''Returns a list of plants that require attention'''
    q = '''WITH LastThreeRecordings AS (
        SELECT plant_id, soil_moisture, temperature, 
        ROW_NUMBER() OVER (PARTITION BY plant_id ORDER BY time_taken DESC) AS row_num
        FROM gamma.recordings)
        SELECT plant_id FROM LastThreeRecordings
        WHERE row_num <= 3
        GROUP BY plant_id
        HAVING COUNT(*) = 3
        AND SUM(
        CASE WHEN (soil_moisture > 70 OR soil_moisture < 15
        OR temperature > 35 OR temperature < 15)
           THEN 1 ELSE 0 
        END) = 3;'''
    with get_connection() as conn:
        logging.info('Connection established.')
        with conn.cursor() as cur:
            cur.execute(q)
            logging.info('Query executed.')
            plants = [plant['plant_id'] for plant in cur.fetchall()]
            logging.info('Plants identified:%s',plants)
    return plants


def send_emergency_email(plants: list[int]) -> None:
    '''Sends an email using SES to a specified email address'''
    ses = client("ses", aws_access_key_id=ENV["MY_AWS_ACCESS_KEY"],
                 aws_secret_access_key=ENV["MY_AWS_SECRET_KEY"],
                 region_name="eu-west-2")
    logging.info('SES client connection established.')

    text = "LMNH BOTANICAL WARNING SYSTEM TRIGGERED\n"
    subject = f"WARNING: Plant Danger Detected {get_date()}."
    for plant in plants:
        logging.info('Inserted plant %s into email',plant)
        text += f'WARNING: Abnormal abiotic conditions have been detected for Plant ID: {plant}.\n'
    text+='\n This is an automated email. Please do not reply to this address.'
    logging.info('Email constructed.')

    ses.send_email(Source=ENV['FROM'],
                   Destination={'ToAddresses': [ENV['TO']]},
                   Message={'Subject': {'Data': subject},
                            'Body': {'Text': {'Data': text}}})
    logging.info('Email sent.')

def config_logs() -> logging.Logger:
    '''Configures the logging to log information'''
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    return logger

def handler(event, context) -> None:
    '''Calls functions to get plant data and assess plant health'''
    log = config_logs()
    logging.info('Log Configured.')
    load_dotenv()
    logging.info('Environment loaded.')
    plant_ids = get_affected_plants()
    if plant_ids:
        send_emergency_email(plant_ids)
    else:
        logging.info('No plants identified')

if __name__ == '__main__':
    handler({},{})
