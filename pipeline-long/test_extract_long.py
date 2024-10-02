from unittest.mock import patch, MagicMock
import pyodbc
from extract import connect_to_rds, extract_plant_data


class TestConnectToRDS:
    """Test suite for the connect_to_rds function, which establishes a
    connection to an RDS instance using pyodbc."""

    @patch("pyodbc.connect")
    def test_connect_to_rds_success(self, mock_connect):
        """Tests successful connection to the RDS using the connect_to_rds
        function."""

        mock_connect.return_value = MagicMock()
        connection = connect_to_rds(
            "db_host", "db_user", "db_password", "db_name")

        mock_connect.assert_called_once_with(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=db_host;"
            "DATABASE=db_name;"
            "UID=db_user;"
            "PWD=db_password"
        )

        assert connection is not None


class TestExtractPlantData:
    """Test suite for the extract_plant_data function, which queries and 
    extracts plant data older than 24 hours from the database."""

    @patch("pyodbc.connect")
    def test_extract_plant_data_query_execution(self, mock_connect):
        """Test that the correct SQL query is executed in extract_plant_data."""

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        extract_plant_data(mock_connection)

        expected_query = (
            """
            SELECT recording_id, time_taken, soil_moisture, temperature, plant_id, botanist_id
            FROM gamma.recordings
            WHERE time_taken < DATEADD(HOUR, -24, GETDATE());
            """
        )

        normalised_expected_query = " ".join(expected_query.split())
        actual_query = " ".join(mock_cursor.execute.call_args[0][0].split())

        assert actual_query == normalised_expected_query

    @patch("pyodbc.connect")
    def test_extract_plant_data_success(self, mock_connect):
        """Tests successful data extraction from the database, specifically
        verifying that the returned data matches the expected result."""

        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchall.return_value = [
            (1, "2024-10-01 12:00:00", 30.5, 25.2, 101, 202),
            (2, "2024-10-01 10:00:00", 35.1, 24.7, 102, 203),
        ]
        mock_cursor.description = [
            ("recording_id",), ("time_taken",), ("soil_moisture",
                                                 ), ("temperature",), ("plant_id",), ("botanist_id",)
        ]
        mock_connection.cursor.return_value = mock_cursor

        data = extract_plant_data(mock_connection)

        expected_data = [
            {
                "recording_id": 1,
                "time_taken": "2024-10-01 12:00:00",
                "soil_moisture": 30.5,
                "temperature": 25.2,
                "plant_id": 101,
                "botanist_id": 202,
            },
            {
                "recording_id": 2,
                "time_taken": "2024-10-01 10:00:00",
                "soil_moisture": 35.1,
                "temperature": 24.7,
                "plant_id": 102,
                "botanist_id": 203,
            },
        ]

        assert data == expected_data

    def test_extract_plant_data_no_connection(self):
        """Tests that extract_plant_data behaves correctly when no database
        connection is provided i.e. that it returns an empty list."""

        data = extract_plant_data(None)

        assert data == []

    def test_extract_plant_data_query_failure(self):
        """Tests that extract_plant_data behaves correctly when the SQL 
        query execution fails i.e. that it returns an empty list."""

        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.execute.side_effect = pyodbc.Error("Query failed.")
        mock_connection.cursor.return_value = mock_cursor

        data = extract_plant_data(mock_connection)

        assert data == []
        mock_connection.close.assert_called_once()
