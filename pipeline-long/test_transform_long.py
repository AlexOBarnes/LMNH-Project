"""Tests for the function in transform.py"""

import pandas as pd
from transform_long import transform_data_to_csv


class TestTransformDataToCSV:
    """Test suite for the transform_data_to_csv function."""

    def test_basic_functionality(self):
        """Tests the basic functionality of transforming a list of 
        dictionaries into a CSV format."""

        data = pd.DataFrame([
            {"id": 1, "name": "Plant A", "moisture": 30.5},
            {"id": 2, "name": "Plant B", "moisture": 45.0}
        ])

        expected_output = "id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.decode("UTF-8") == expected_output

    def test_empty_input(self):
        """Tests that the function behaves correctly with an empty input 
        list i.e. that it returns a CSV header with no data entries."""

        data = pd.DataFrame(columns=["id", "name", "moisture"])
        expected_output = "id,name,moisture\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.decode("UTF-8") == expected_output

    def test_single_record(self):
        """Tests the transformation of a single record into CSV format."""

        data = pd.DataFrame([{"id": 1, "name": "Plant A", "moisture": 30.5}])
        expected_output = "id,name,moisture\n1,Plant A,30.5\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.decode("UTF-8") == expected_output

    def test_multiple_records(self):
        """Tests the transformation of multiple records into CSV format."""

        data = pd.DataFrame([
            {'id': 1, 'name': 'Plant A', 'moisture': 30.5},
            {'id': 2, 'name': 'Plant B', 'moisture': 45.0},
            {'id': 3, 'name': 'Plant C', 'moisture': 25.0},
        ])

        expected_output = "id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n3,Plant C,25.0\n"
        csv_file_like = transform_data_to_csv(data)
        assert csv_file_like.decode("UTF-8") == expected_output

    def test_missing_fields(self):
        """Tests that the function behaves correctly with missing fields
        in input records i.e. that it ensures the CSV output represents
        empty values appropriately."""

        data = pd.DataFrame([
            {'id': 1, 'name': 'Plant A'},
            {'id': 2, 'moisture': 45.0},
        ])

        expected_output = "id,name,moisture\n1,Plant A,\n2,,45.0\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.decode("UTF-8") == expected_output
