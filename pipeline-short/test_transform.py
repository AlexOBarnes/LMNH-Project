# pylint: skip-file
import pytest
from unittest.mock import patch
from transform_short import split_name, validate_latitude, validate_longitude, get_botanist_id


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
