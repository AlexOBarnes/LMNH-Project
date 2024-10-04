from unittest.mock import patch, MagicMock
import pandas as pd
from extract_long import extract_plant_data


class TestExtractPlantData:
    """Test suite for the extract_plant_data function, which queries and 
    extracts plant data older than 24 hours from the database."""

    @patch("extract_long.connect_to_rds")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_query_execution(self, mock_connect):
        """Test that the correct SQL query is executed in extract_plant_data."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        extract_plant_data()

        expected_extract_query = (
            "SELECT * FROM gamma.recordings;"
        ).strip()

        expected_truncate_query = "TRUNCATE TABLE gamma.recordings;"

        mock_cursor.execute.assert_any_call(expected_extract_query)
        mock_cursor.execute.assert_any_call(expected_truncate_query)

    @patch("extract_long.connect_to_rds")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_success(self, mock_connect):
        """Tests successful data extraction from the database, specifically
        verifying that the returned data matches the expected result."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, "2024-10-01 12:00:00", 30.5, 25.2, 101, 202),
            (2, "2024-10-01 10:00:00", 35.1, 24.7, 102, 203),
        ]

        mock_cursor.description = [
            ("recording_id",), ("time_taken",), ("soil_moisture",
                                                 ), ("temperature",), ("plant_id",), ("botanist_id",)
        ]

        data = extract_plant_data()

        expected_data = pd.DataFrame({
            "recording_id": [1, 2],
            "timestamp": ["2024-10-01 12:00:00", "2024-10-01 10:00:00"],
            "soil_moisture": [30.5, 35.1],
            "temperature": [25.2, 24.7],
            "plant_id": [101, 102],
            "botanist_id": [202, 203]
        })

        pd.testing.assert_frame_equal(data, expected_data)

    @patch("extract_long.connect_to_rds")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_empty(self, mock_connect):
        """Tests the behaviour of extract_plant_data when no data is 
        extracted i.e. returns an empty result."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        mock_cursor.description = [
            ("recording_id",), ("time_taken",), ("soil_moisture",
                                                 ), ("temperature",), ("plant_id",), ("botanist_id",)
        ]

        data = extract_plant_data()

        assert data.empty

    @patch("extract_long.connect_to_rds")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_query_failure(self, mock_connect):
        """Tests that extract_plant_data behaves correctly when the SQL 
        query execution fails i.e. that it returns an empty result."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Query failed.")

        data = extract_plant_data()

        assert data.empty
