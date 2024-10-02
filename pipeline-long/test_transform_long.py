from transform import transform_data_to_csv


class TestTransformDataToCSV:

    def test_basic_functionality(self):
        data = [
            {"id": 1, "name": "Plant A", "moisture": 30.5},
            {"id": 2, "name": "Plant B", "moisture": 45.0}
        ]

        expected_output = "id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.getvalue() == expected_output

    def test_empty_input(self):
        data = []
        expected_output = "id,name,moisture\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.getvalue() == expected_output

    def test_single_record(self):
        data = [{"id": 1, "name": "Plant A", "moisture": 30.5}]
        expected_output = "id,name,moisture\n1,Plant A,30.5\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.getvalue() == expected_output

    def test_multiple_records(self):
        data = [
            {'id': 1, 'name': 'Plant A', 'moisture': 30.5},
            {'id': 2, 'name': 'Plant B', 'moisture': 45.0},
            {'id': 3, 'name': 'Plant C', 'moisture': 25.0},
        ]

        expected_output = "id,name,moisture\n1,Plant A,30.5\n2,Plant B,45.0\n3,Plant C,25.0\n"
        csv_file_like = transform_data_to_csv(data)
        assert csv_file_like.getvalue() == expected_output

    def test_missing_fields(self):
        data = [
            {'id': 1, 'name': 'Plant A'},
            {'id': 2, 'moisture': 45.0},
        ]

        expected_output = "id,name,moisture\n1,Plant A,\n2,,45.0\n"
        csv_file_like = transform_data_to_csv(data)

        assert csv_file_like.getvalue() == expected_output
