"""File to test the function in load.py"""

from unittest.mock import patch, MagicMock
from datetime import datetime
from load_long import upload_csv_to_s3


class TestUploadCSVtoS3:
    """Test suite for the upload_csv_to_s3 function."""

    @patch("boto3.client")
    def test_basic_functionality(self, mock_boto_client):
        """Tests that a CSV file is uploaded to the S3 bucket with the 
        correct filename and content."""

        csv_content = b"id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        bucket_name = "test-bucket"
        folder_path = "test_folder/"
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        upload_csv_to_s3(csv_content, bucket_name, folder_path)

        current_date = datetime.now().strftime("%d-%m-%Y")
        expected_filename = f"{folder_path}{current_date}.csv"
        mock_s3.put_object.assert_called_once_with(
            Bucket=bucket_name,
            Key=expected_filename,
            Body=csv_content
        )

    @patch("boto3.client")
    def test_empty_csv(self, mock_boto_client):
        """Tests that uploading an empty CSV buffer works correctly."""

        csv_content = b""
        bucket_name = "test-bucket"
        folder_path = "test_folder/"
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        upload_csv_to_s3(csv_content, bucket_name, folder_path)

        current_date = datetime.now().strftime("%d-%m-%Y")
        expected_filename = f"{folder_path}{current_date}.csv"
        mock_s3.put_object.assert_called_once_with(
            Bucket=bucket_name,
            Key=expected_filename,
            Body=csv_content
        )

    @patch("boto3.client")
    def test_invalid_bucket_name(self, mock_boto_client):
        """Test how the function handles an invalid S3 bucket name."""

        csv_content = b"id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        bucket_name = "invalid-bucket"
        folder_path = "test_folder/"
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = Exception("Bucket does not exist")
        mock_boto_client.return_value = mock_s3

        try:
            upload_csv_to_s3(csv_content, bucket_name, folder_path)
        except Exception as e:
            assert str(e) == "Bucket does not exist"
        mock_s3.put_object.assert_called_once()

    @patch("boto3.client")
    def test_filename_correctness(self, mock_boto_client):
        """Test that the CSV filename is correctly generated based on the 
        current date."""

        csv_content = b"id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        bucket_name = "test-bucket"
        folder_path = "test_folder/"
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        upload_csv_to_s3(csv_content, bucket_name, folder_path)

        current_date = datetime.now().strftime("%d-%m-%Y")
        expected_filename = f"{folder_path}{current_date}.csv"
        mock_s3.put_object.assert_called_once_with(
            Bucket=bucket_name,
            Key=expected_filename,
            Body=csv_content
        )

    @patch("boto3.client")
    def test_s3_exception_handling(self, mock_boto_client):
        """Test how the function behaves when boto3 throws an exception."""

        csv_content = b"id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        bucket_name = "test-bucket"
        folder_path = "test_folder/"
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = Exception("S3 error occurred")
        mock_boto_client.return_value = mock_s3

        try:
            upload_csv_to_s3(csv_content, bucket_name, folder_path)
        except Exception as e:
            assert str(e) == "S3 error occurred"
        mock_s3.put_object.assert_called_once()
