from pyaiml21.stdlib.maps import PLURAL, SINGULAR, PREDECESSOR, SUCCESSOR


def test_plural():
    assert PLURAL["dog"] == "dogs"
    assert PLURAL["apple"] == "apples"
    assert PLURAL["die"] == "dice"
    assert PLURAL["tooth"] == "teeth"
    assert PLURAL["man"] == "men"


def test_singular():
    assert SINGULAR["cats"] == "cat"
    assert SINGULAR["feet"] == "foot"
    assert SINGULAR["ponnies"] == "ponny"


def test_predecessor():
    assert PREDECESSOR["2"] == "1"
    assert PREDECESSOR["1"] == "0"
    assert PREDECESSOR["-3"] == "-4"
    assert PREDECESSOR["7841581"] == "7841580"


def test_successor():
    assert SUCCESSOR["0"] == "1"
    assert SUCCESSOR["5"] == "6"


def test_invariants():
    RANDOM_WORDS = ["car", "peach", "mammut", "city", "hall"]
    RANDOM_NUMBERS = map(str, [1, 2, 78, 5158418, 4151458848548])

    for w in RANDOM_WORDS:
        assert SINGULAR[PLURAL[w]] == w
    for n in RANDOM_NUMBERS:
        assert PREDECESSOR[SUCCESSOR[n]] == n
        assert SUCCESSOR[PREDECESSOR[n]] == n
