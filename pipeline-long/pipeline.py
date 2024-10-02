"""Pipeline file for extracting data from RDS, transforming to CSV,
and uploading to S3."""

from os import environ as ENV
from dotenv import load_dotenv

from extract import connect_to_rds, extract_plant_data
from transform import transform_data_to_csv
from load import upload_csv_to_s3


def lambda_handler(event, context):
    """AWS Lambda handler function for running the ETL pipeline."""

    DB_HOST = ENV["DB_HOST"]
    DB_USER = ENV["DB_USER"]
    DB_PASSWORD = ENV["DB_PASSWORD"]
    DB_NAME = ENV["DB_NAME"]
    S3_BUCKET_NAME = ENV["S3_BUCKET_NAME"]

    conn = connect_to_rds(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    if conn is None:
        return {"status_code": 500, "message": "Failed to connect to RDS"}

    plant_data = extract_plant_data(conn)
    if not plant_data:
        return {"status_code": 204, "message": "No new data to process."}

    csv_buffer = transform_data_to_csv(plant_data)

    try:
        upload_csv_to_s3(csv_buffer, S3_BUCKET_NAME)
        return {"status_code": 200, "body": "CSV uploaded successfully."}
    except Exception as e:
        return {"status_code": 500, "body": f"Failed tp upload CSV to S3: {e}"}


if __name__ == "__main__":

    load_dotenv()

    result = lambda_handler({}, {})
    print(result)
