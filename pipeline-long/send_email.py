"""A file for sending emails to confirm when the pipeline has started
and ended."""

from os import environ as ENV
from boto3 import client


def send_email(is_start: bool, date: str) -> None:
    """Sends an email using SES to a specified email address."""

    ses = client("ses", aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                 aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"],
                 region_name=ENV.get("AWS_REGION", "eu-west-2"))
    if is_start:
        text = "The pipeline has started. Processing of historic data has begun."
        subject = f"Pipeline Run - {date}."
    else:
        text = """Data processing has been completed,
        the clean data has been uploaded to output S3 bucket."""
        subject = f"Pipeline Complete - {date}."

    try:
        response = ses.send_email(
            Source=ENV["FROM_EMAIL"],
            Destination={"ToAddresses": [ENV["TO_EMAIL"]]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": text}}
            }
        )
        print(f"Email send successfully: {response}")

    except Exception as e:
        print(f"Error sending email: {e}")
