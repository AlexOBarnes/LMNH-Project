"""File to test the function in load.py"""

from unittest.mock import patch, MagicMock
from datetime import datetime
from load import upload_to_csv


class TestUploadCSVtoS3:
    """Test suite for the upload_csv_to_s3 function."""

    @patch("boto3.client")
    def test_basic_functionality(self, mock_boto_client):
        """Tests that a CSV file is uploaded to the S3 bucket with the 
        correct filename and content."""

        csv_content = "id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        bucket_name = "test-bucket"
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        upload_to_csv(csv_content, bucket_name)

        current_date = datetime.now().strftime("%Y-%m-%d")
        expected_filename = f"plant_sensor_data_{current_date}.csv"
        mock_s3.put_object.assert_called_once_with(
            Bucket=bucket_name,
            Key=expected_filename,
            Body=csv_content
        )
