from unittest.mock import patch, MagicMock
import pandas as pd
from extract_long import connect_to_rds, extract_plant_data


class TestConnectToRDS:
    """Test suite for the connect_to_rds function, which establishes a
    connection to an RDS instance using pyodbc."""

    @patch("extract_long.connect")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_connect_to_rds_success(self, mock_connect):
        """Tests successful connection to the RDS using the connect_to_rds
        function."""

        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        connection = connect_to_rds()

        mock_connect.assert_called_once_with(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=test_host,1433;"
            "DATABASE=test_db;"
            "UID=test_user;"
            "PWD=test_password"
        )

        assert connection is not None


class TestExtractPlantData:
    """Test suite for the extract_plant_data function, which queries and 
    extracts plant data older than 24 hours from the database."""

    @patch("extract_long.connect_to_rds")
    @patch("pandas.read_sql")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_query_execution(self, mock_read_sql, mock_connect):
        """Test that the correct SQL query is executed in extract_plant_data."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        extract_plant_data()

        expected_extract_query = (
            "SELECT recording_id, time_taken, soil_moisture, temperature, plant_id, botanist_id "
            "FROM gamma.recordings;"
        ).strip()

        expected_truncate_query = "TRUNCATE TABLE gamma.recordings;"

        mock_cursor.execute.assert_called_once_with(
            expected_truncate_query)

        actual_query_call = mock_read_sql.call_args[0][0].strip()

        assert actual_query_call == expected_extract_query

    @patch("extract_long.connect_to_rds")
    @patch("pandas.read_sql")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_success(self, mock_read_sql, mock_connect):
        """Tests successful data extraction from the database, specifically
        verifying that the returned data matches the expected result."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection

        mock_read_sql.return_value = pd.DataFrame({
            "recording_id": [1, 2],
            "time_taken": ["2024-10-01 12:00:00", "2024-10-01 10:00:00"],
            "soil_moisture": [30.5, 35.1],
            "temperature": [25.2, 24.7],
            "plant_id": [101, 102],
            "botanist_id": [202, 203]
        })

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
    @patch("pandas.read_sql")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_empty(self, mock_read_sql, mock_connect):
        """Tests the behaviour of extract_plant_data when no data is 
        extracted i.e. returns an empty result."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection

        mock_read_sql.return_value = pd.DataFrame(
            columns=["recording_id", "timestamp", "soil_moisture", "temperature", "plant_id", "botanist_id"])

        data = extract_plant_data()

        assert data.empty

    @patch("extract_long.connect_to_rds")
    @patch("pandas.read_sql")
    @patch.dict("os.environ", {
        "DB_HOST": "test_host",
        "DB_PORT": "1433",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password"
    })
    def test_extract_plant_data_query_failure(self, mock_read_sql, mock_connect):
        """Tests that extract_plant_data behaves correctly when the SQL 
        query execution fails i.e. that it returns an empty result."""

        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection

        mock_read_sql.side_effect = Exception("Query failed.")

        data = extract_plant_data()

        assert data.empty
