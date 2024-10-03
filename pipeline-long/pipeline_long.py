"""Pipeline file for extracting data from RDS, transforming to CSV,
and uploading to S3."""

from os import environ as ENV
from datetime import datetime
from dotenv import load_dotenv

from extract_long import extract_plant_data
from transform_long import transform_data_to_csv
from load_long import upload_csv_to_s3
from send_email import send_email


def lambda_handler(event, context):
    """AWS Lambda handler function for running the ETL pipeline."""

    bucket_name = ENV["S3_BUCKET_NAME"]
    bucket_folder_name = ENV["S3_FOLDER_PATH"]

    current_date = datetime.now().strftime("%d-%m-%Y")

    send_email(is_start=True, date=current_date)

    plant_data = extract_plant_data()
    if plant_data.empty:
        return {"status_code": 204, "message": "No new data to process."}

    csv_buffer = transform_data_to_csv(plant_data)

    try:
        upload_csv_to_s3(csv_buffer, bucket_name, bucket_folder_name)
        send_email(is_start=False, date=current_date)
        return {"status_code": 200, "body": "CSV uploaded successfully and email sent."}
    except Exception as e:
        return {"status_code": 500, "body": f"Failed to upload CSV to S3: {e}"}


if __name__ == "__main__":

    load_dotenv()

    result = lambda_handler({}, {})
    print(result)
