from pyaiml21.stdlib.sets import IS_NUMBER


def test_number():
    assert "1" in IS_NUMBER
    assert "nothing" not in IS_NUMBER
    assert "" not in IS_NUMBER
