from unittest.mock import patch, MagicMock
from pipeline_long import lambda_handler


class TestPipeline:

    @patch("pipeline_long.extract_plant_data")
    @patch("pipeline_long.transform_data_to_csv")
    @patch("pipeline_long.upload_csv_to_s3")
    @patch("pipeline_long.send_email")
    @patch.dict("os.environ", {"S3_BUCKET_NAME": "test-bucket", "S3_FOLDER_PATH": "test-folder"})
    def test_lambda_handler_success(self, mock_send_email, mock_upload_csv_to_s3, mock_transform_data_to_csv, mock_extract_plant_data):

        mock_extract_plant_data.return_value.empty = False
        mock_transform_data_to_csv.return_value = MagicMock()

        response = lambda_handler({}, {})

        assert response["status_code"] == 200
        assert response["body"] == "CSV uploaded successfully and email sent."

        assert mock_send_email.call_count == 2

        calls = mock_send_email.call_args_list

        assert calls[0][1]["is_start"] is True
        assert isinstance(calls[0][1]["date"], str)

        assert calls[1][1]["is_start"] is False
        assert isinstance(calls[1][1]["date"], str)

    @patch("pipeline_long.extract_plant_data")
    @patch("pipeline_long.send_email")
    @patch.dict("os.environ", {"S3_BUCKET_NAME": "test-bucket", "S3_FOLDER_PATH": "test-folder"})
    def test_lambda_handler_no_data(self, mock_send_email, mock_extract_plant_data):

        mock_extract_plant_data.return_value.empty = True

        response = lambda_handler({}, {})
        assert response["status_code"] == 204
        assert response["message"] == "No new data to process."

        mock_send_email.assert_called_once()

        first_call_kwargs = mock_send_email.call_args[1]
        assert first_call_kwargs["is_start"] is True
        assert isinstance(first_call_kwargs["date"], str)

    @patch("pipeline_long.extract_plant_data")
    @patch("pipeline_long.transform_data_to_csv")
    @patch("pipeline_long.upload_csv_to_s3")
    @patch("pipeline_long.send_email")
    @patch.dict("os.environ", {"S3_BUCKET_NAME": "test-bucket", "S3_FOLDER_PATH": "test-folder"})
    def test_lambda_handler_upload_failure(self, mock_send_email, mock_upload_csv_to_s3, mock_transform_data_to_csv, mock_extract_plant_data):

        mock_extract_plant_data.return_value.empty = False
        mock_transform_data_to_csv.return_value = MagicMock()
        mock_upload_csv_to_s3.side_effect = Exception("Upload failed")

        response = lambda_handler({}, {})
        assert response["status_code"] == 500
        assert "Failed to upload CSV to S3" in response["body"]
