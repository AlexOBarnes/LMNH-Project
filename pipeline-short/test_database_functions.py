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
