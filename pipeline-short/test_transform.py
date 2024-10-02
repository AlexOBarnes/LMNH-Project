# pylint: skip-file
import pytest
from transform import split_name


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
