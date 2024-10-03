"""A file to load the CSV file into a specified S3 bucket."""

from datetime import datetime
from os import environ as ENV
import sys
import boto3


def upload_csv_to_s3(csv_buffer: str, bucket_name: str, folder_path: str):
    """Uploads the CSV file to the specified S3 bucket."""

    current_date = datetime.now().strftime("%d-%m-%Y")
    filename = f"{folder_path}{current_date}.csv"

    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=bucket_name, Key=filename, Body=csv_buffer)


if __name__ == "__main__":

    csv_buff = sys.stdin.read()

    s3_bucket = ENV["S3_BUCKET_NAME"]
    bucket_folder = ENV["S3_FOLDER_PATH"]
    upload_csv_to_s3(csv_buff, s3_bucket, bucket_folder)
