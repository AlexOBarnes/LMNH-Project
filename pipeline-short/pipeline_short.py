'''Short term pipeline'''
import pymssql
from transform_short import get_connection, transform_plant_data
from extract_short import extract
from load_short import load


def lambda_handler(event=None, context=None):
    '''Lambda handler. Connects to the database, extracts 
    information from the API, '''
    try:
        with get_connection() as conn:
            extracted_data = extract()
            plants, locations, readings = transform_plant_data(
                conn, extracted_data)
            load(conn, plants, locations, readings)
    except Exception as err:
        return {"statusCode": 400, 'body': f"Failure. Could not extract data, {err}"}
    return {'statusCode': 200, "body": "Success."}


if __name__ == "__main__":
    lambda_handler(None, None)
