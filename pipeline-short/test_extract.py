"""A file to test the functions in extract.py"""

from unittest.mock import patch
import pytest

from extract import get_url

MOCK_BASE_URL = "https://api.example.com"

@patch("extract.BASE_URL", MOCK_BASE_URL)
def test_get_url_with_valid_id():
    id = 23
    expected_url = f"{MOCK_BASE_URL}/plants/{id}"
    
    assert get_url(id) == expected_url