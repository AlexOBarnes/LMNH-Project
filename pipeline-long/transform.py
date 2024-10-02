"""A file to transform the extracted plant data from the RDS into a 
CSV file to be loaded into the S3 bucket."""

from io import StringIO
import pandas as pd


def transform_data_to_csv(data: list[dict]) -> StringIO:
    """Transform the extract plant data into a CSV file-like object."""

    csv_buffer = StringIO()

    if not data:
        return "id,name,moisture\n"

    df = pd.DataFrame(data)
    df.to_csv(csv_buffer, index=False)

    csv_buffer.seek(0)

    return csv_buffer


if __name__ == "__main__":

    sample_data = [
        {'recording_id': 1, 'time_taken': '2024-10-01 10:00:00', 'soil_moisture': 23.5,
            'temperature': 25.0, 'plant_id': 101, 'botanist_id': 1},
        {'recording_id': 2, 'time_taken': '2024-10-01 10:05:00', 'soil_moisture': 22.0,
            'temperature': 24.5, 'plant_id': 102, 'botanist_id': 2},
    ]

    csv_file_like = transform_data_to_csv(sample_data)

    print(csv_file_like.getvalue())
