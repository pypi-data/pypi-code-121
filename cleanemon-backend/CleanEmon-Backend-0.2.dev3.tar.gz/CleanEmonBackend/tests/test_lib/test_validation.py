from CleanEmonBackend.lib.validation import is_valid_date
from CleanEmonBackend.lib.validation import is_valid_date_range


def test_is_valid_date():
    assert is_valid_date("2022-01-01")
    assert is_valid_date("2522-01-01")

    assert not is_valid_date("2022")
    assert not is_valid_date("2022-10")
    assert not is_valid_date("2022-13-01")
    assert not is_valid_date("")


def test_is_valid_date_range():
    assert is_valid_date_range("2022-01-01", "2022-01-01")
    assert is_valid_date_range("2022-01-01", "2022-01-02")
    assert is_valid_date_range("2022-01-01", "2022-12-01")
    assert is_valid_date_range("2022-01-01", "2025-01-01")

    assert not is_valid_date_range("2022-01-02", "2022-01-01")
    assert not is_valid_date_range("2022-01-01", "2022")
    assert not is_valid_date_range("2022", "2022-01-01")

