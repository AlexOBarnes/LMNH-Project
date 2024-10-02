"""A file to load the CSV file into a specified S3 bucket."""

from datetime import datetime
import boto3


def upload_csv_to_s3(csv_buffer: str, bucket_name: str):
    """Uploads the CSV file to the specified S3 bucket."""

    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"plant_sensor_data_{current_date}.csv"

    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=bucket_name, Key=filename, Body=csv_buffer)
