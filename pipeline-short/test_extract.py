# pylint: skip-file
"""A file to test the functions in extract.py"""

from unittest.mock import patch
import pytest

from extract import get_url, validate_response, get_num_plants


MOCK_BASE_URL = "https://api.example.com"


@patch("extract.BASE_URL", MOCK_BASE_URL)
def test_get_url_with_valid_id():
    """Tests get_url function with a valid plant ID."""

    id = 23
    expected_url = f"{MOCK_BASE_URL}/plants/{id}"
    assert get_url(id) == expected_url


def test_validate_response_invalid():
    """Test for an invalid response."""
    response = {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3",
    }
    assert validate_response(response) is False


def test_validate_response():
    """Test for a response that's valid."""
    response = {
        "botanist": "value1",
        "plant_id": "value3",
    }
    assert validate_response(response) is True


@patch("extract.requests.get")
@patch("extract.BASE_URL", MOCK_BASE_URL)
def test_get_num_plants_success(mock_get):
    """Tests get_num_plants with a successful API response."""

    mock_get.return_value.json.return_value = {
        "success": True,
        "plants_on_display": 49
    }

    num_plants = get_num_plants()

    assert num_plants == 49
