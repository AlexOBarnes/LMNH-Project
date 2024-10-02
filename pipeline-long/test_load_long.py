"""File to test the function in load.py"""

from unittest.mock import patch, MagicMock
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
