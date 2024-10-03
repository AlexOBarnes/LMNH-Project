"""Pipeline file for extracting data from RDS, transforming to CSV,
and uploading to S3."""

from os import environ as ENV
from dotenv import load_dotenv

from extract_long import connect_to_rds, extract_plant_data
from transform_long import transform_data_to_csv
from load_long import upload_csv_to_s3


def lambda_handler(event, context):
    """AWS Lambda handler function for running the ETL pipeline."""

    db_host = ENV["DB_HOST"]
    db_user = ENV["DB_USER"]
    db_password = ENV["DB_PASSWORD"]
    db_name = ENV["DB_NAME"]
    bucket_name = ENV["S3_BUCKET_NAME"]
    bucket_folder_name = ENV["S3_FOLDER_PATH"]

    conn = connect_to_rds(db_host, db_user, db_password, db_name)
    if conn is None:
        return {"status_code": 500, "message": "Failed to connect to RDS"}

    plant_data = extract_plant_data(conn)
    if not plant_data:
        return {"status_code": 204, "message": "No new data to process."}

    csv_buffer = transform_data_to_csv(plant_data)

    try:
        upload_csv_to_s3(csv_buffer, bucket_name, bucket_folder_name)
        return {"status_code": 200, "body": "CSV uploaded successfully."}
    except Exception as e:
        return {"status_code": 500, "body": f"Failed tp upload CSV to S3: {e}"}


if __name__ == "__main__":

    load_dotenv()

    result = lambda_handler({}, {})
    print(result)
