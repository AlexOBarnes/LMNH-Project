# pylint: skip-file
import pytest
from unittest.mock import patch
from transform_short import split_name, validate_latitude, validate_longitude, get_botanist_id, get_species_id, validate_plant


@patch("transform_short.is_valid_email", return_value=True)
@patch("transform_short.validate_origin_data", return_value=True)
def test_validate_plant_valid_new_plant_with_origin(mock_is_valid_email, mock_validate_origin_data):
    plant = {
        "botanist": {
            "name": "Jane Doe",
            "phone": "987654321",
            "email": "jane.doe@botany.com"
        },
        "name": "Tulip",
        "plant_id": 5,
        "soil_moisture": 45,
        "temperature": 20,
        "last_watered": "2023-10-02",
        "recording_taken": "2023-10-03",
        "origin_data": {
            "latitude": 34.05,
            "longitude": -118.25
        }
    }

    all_plant_ids = [1, 2, 3]

    assert validate_plant(plant, all_plant_ids) is True


def test_validate_plant_missing_required_keys():

    plant = {
        "botanist": {
            "name": "John Doe",
            "phone": "123456789"
        },
        "plant_id": 1
    }

    all_plant_ids = [1, 2, 3]

    assert validate_plant(plant, all_plant_ids) is False


def test_get_species_id_found_by_scientific_name():
    '''Tests retrieval fo species ID froma  matching scientific name'''
    plant_data = {
        "name": "roses",
        "scientific_name": ["Rosa"]
    }

    all_names = {
        "scientific_name": {
            "Rosa": 1
        },
        "common_name": {
            "Rose": 2
        }
    }

    assert get_species_id(plant_data, all_names) == 1


def test_get_species_id_found_by_common_name():
    '''Tests retrieval fo species ID froma  matching common name'''
    plant_data = {
        "name": "rose"
    }

    all_names = {
        "scientific_name": {},
        "common_name": {
            "Rose": 2
        }
    }
    assert get_species_id(plant_data, all_names) == 2


def test_get_species_id_not_found():
    '''Tests that an error is raised if a species is not found.'''
    plant_data = {
        "name": "daisy",
        "scientific_name": ["Bellis"]
    }

    all_names = {
        "scientific_name": {
            "Rosa": 1
        },
        "common_name": {
            "Rose": 2
        }
    }

    with pytest.raises(ValueError, match="Species not available"):
        get_species_id(plant_data, all_names)


@patch("transform_short.split_name", return_value=("John", "Doe"))
def test_get_botanist_id_found(mock_split_name):

    botanist_data = {
        "email": "test@bot.com",
        "phone": "1234567890",
        "name": "John Doe"
    }

    all_botanists = {
        ("test@bot.com", "John", "Doe"): 42
    }

    botanist_id = get_botanist_id(botanist_data, all_botanists)

    assert botanist_id == 42


@patch("transform_short.split_name", return_value=("John", "Noe"))
def test_get_botanist_id_not_found(mock_split_name):

    botanist_data = {
        "email": "test@bot.com",
        "phone": "1234567890",
        "name": "John Noe"
    }

    all_botanists = {
        ("test@bot.com", "John", "Doe"): 42
    }

    with pytest.raises(ValueError, match="Botanist not available."):
        get_botanist_id(botanist_data, all_botanists)


def test_validate_longitude():
    assert validate_longitude("0") == True
    assert validate_longitude("-180") == True
    assert validate_longitude("180") == True
    assert validate_longitude("200") == False
    assert validate_longitude("-181") == False
    assert validate_longitude("abc") == False


def test_validate_latitude():
    assert validate_latitude("0") == True
    assert validate_latitude("-90") == True
    assert validate_latitude("90") == True
    assert validate_latitude("100") == False
    assert validate_latitude("-91") == False
    assert validate_latitude("xyz") == False


def test_split_name_standard():
    """Test for a standard first and last name."""
    assert split_name("John Doe") == ["John", "Doe"]


def test_split_name_middle_name():
    """Test for a name with a middle name."""
    assert split_name("John Michael Doe") == ["John", "Michael Doe"]


def test_split_name_single_name():
    """Test for a single name."""
    assert split_name("John") == ["John", ""]


def test_split_name_extra_spaces():
    """Test for names with extra spaces."""
    assert split_name("  John   Doe  ") == [
        "John", "Doe"]


def test_split_name_empty_string():
    """Test for an empty string."""
    assert split_name("") == ["", ""]


def test_split_name_special_characters():
    """Test for a name with special characters."""
    assert split_name("John O'Neil") == ["John", "O'Neil"]


def test_split_name_hyphenated_last_name():
    """Test for a hyphenated last name."""
    assert split_name("John Smith-Jones") == ["John", "Smith-Jones"]
