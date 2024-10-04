import pytest
from unittest.mock import MagicMock
from database_functions import (get_all_plant_ids, map_plant_id_to_most_recent_botanist,
                                map_botanist_details_to_id, map_town_name_to_id,
                                map_species_names_to_species_id, map_country_code_to_id,
                                map_longitude_and_latitude_to_location_id,
                                map_continent_name_to_id, get_max_location_id)


def test_get_all_plant_ids():
    cursor = MagicMock()
    cursor.fetchall.return_value = [(1,), (2,), (3,)]

    plant_ids = get_all_plant_ids(cursor)

    cursor.execute.assert_called_once_with("SELECT plant_id from gamma.plants")
    assert plant_ids == [1, 2, 3]


def test_map_plant_id_to_most_recent_botanist():
    cursor = MagicMock()
    cursor.fetchall.return_value = [(1, 101), (2, 102), (3, 103)]

    result = map_plant_id_to_most_recent_botanist(cursor)

    cursor.execute.assert_called_once()
    assert result == {1: 101, 2: 102, 3: 103}


def test_map_botanist_details_to_id():
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        (1, "john@example.com", "John", "Doe"),
        (2, "jane@example.com", "Jane", "Doe")
    ]

    result = map_botanist_details_to_id(cursor)

    cursor.execute.assert_called_once_with(
        "SELECT botanist_id, email, first_name, last_name FROM gamma.botanists"
    )
    assert result == {
        ("john@example.com", "John", "Doe"): 1,
        ("jane@example.com", "Jane", "Doe"): 2
    }


def test_map_town_name_to_id():
    cursor = MagicMock()
    cursor.fetchall.return_value = [("TownA", 1), ("TownB", 2)]

    result = map_town_name_to_id(cursor)

    cursor.execute.assert_called_once_with(
        "SELECT town_name, town_id FROM gamma.regions")
    assert result == {"TownA": 1, "TownB": 2}


def test_map_species_names_to_species_id():
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        (1, "Species One", "Common One"),
        (2, "Species Two", "Common Two")
    ]

    result = map_species_names_to_species_id(cursor)

    cursor.execute.assert_called_once_with(
        "SELECT plant_species_id, scientific_name, common_name FROM gamma.plant_species"
    )
    assert result == {
        "scientific_name": {
            "Species One": 1,
            "Species Two": 2
        },
        "common_name": {
            "Common One": 1,
            "Common Two": 2
        }
    }
