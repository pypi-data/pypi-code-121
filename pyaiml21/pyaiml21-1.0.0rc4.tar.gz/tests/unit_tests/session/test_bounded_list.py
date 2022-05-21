import pytest
from pyaiml21.session.bounded_list import BoundedList


def test_finite_empty():
    s: BoundedList[int] = BoundedList(maxsize=0)
    assert not s.is_infinite
    assert s.capacity == 0
    assert s[0] is None
    assert s[5] is None

    s.add(12)
    s.add(15)
    assert s.capacity == 0
    assert s[0] is None


def test_finite():
    s: BoundedList[int] = BoundedList(maxsize=2)
    s.add(1)
    assert s[0] == 1
    assert s[1] is None
    s.add(2)
    assert s[0] == 2
    assert s[1] == 1
    s.add(3)
    assert s[0] == 3
    assert s[1] == 2
    assert s[2] is None
    assert s[-1] is s[1]
    assert s.capacity == 2


def test_infinite():
    s: BoundedList[int] = BoundedList(maxsize=None)
    assert s.is_infinite
    s.add(0)
    assert s.capacity == 1
    assert s[0] == 0
    s.add(2)
    s.add(56)
    s.add(2342)
    s.add(1)
    assert s[0] == 1
    assert s[1] == 2342
    assert s[2] == 56
    assert s[3] == 2
    assert s[4] == 0
    assert s[-1] is s[4]
    assert s[-2] is s[3]
    assert s.capacity == 5
