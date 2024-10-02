# pylint: skip-file
"""A file to test the functions in extract.py"""

from unittest.mock import patch
import pytest

from extract import get_url, validate_response

MOCK_BASE_URL = "https://api.example.com"


@patch("extract.BASE_URL", MOCK_BASE_URL)
def test_get_url_with_valid_id():
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


def test_validate_response_():
    """Test for a response that's valid."""
    response = {
        "botanist": "value1",
        "plant_id": "value3",
    }
    assert validate_response(response) is True
