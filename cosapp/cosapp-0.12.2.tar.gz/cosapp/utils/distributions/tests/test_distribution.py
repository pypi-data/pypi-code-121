import json

import pytest

from ..distribution import Distribution


class DummyDistribution(Distribution):
    def _set_distribution(self):
        pass

    def draw(self, q):
        return q


def test_Distribution___init__():
    distrib = DummyDistribution(3.0, 7.0)
    assert isinstance(distrib, Distribution)

    assert distrib.worst == 3.0
    assert distrib.best == 7.0
    assert distrib.pworst == 0.15
    assert distrib.pbest == 0.15

    distrib = DummyDistribution(12.0, 5.0, 0.2, 0.8)
    assert isinstance(distrib, Distribution)

    assert distrib.worst == 12.0
    assert distrib.best == 5.0
    assert distrib.pworst == 0.2
    assert distrib.pbest == 0.8


def test_Distribution___json__():
    distrib = DummyDistribution(3.0, 7.0, 0.1, 0.9)
    try:
        json.dumps(distrib.__json__())
    except TypeError:
        pytest.fail("Distribution.__json__ raised TypeError")

    assert distrib.__json__() == {
        "worst": 3.0,
        "pworst": 0.1,
        "best": 7.0,
        "pbest": 0.9,
    }


def test_Distribution_worst():
    distrib = DummyDistribution(3.0, 7.0)

    distrib.worst = 4
    assert distrib.worst == 4


def test_Distribution_best():
    distrib = DummyDistribution(3.0, 7.0)

    distrib.best = 6
    assert distrib.best == 6


def test_Distribution_pworst():
    distrib = DummyDistribution(3.0, 7.0)

    distrib.pworst = 0.2
    assert distrib.pworst == 0.2

    with pytest.raises(ValueError):
        distrib.pworst = -1

    with pytest.raises(ValueError):
        distrib.pworst = 1.5


def test_Distribution_pbest():
    distrib = DummyDistribution(3.0, 7.0)

    distrib.pbest = 0.2
    assert distrib.pbest == 0.2

    with pytest.raises(ValueError):
        distrib.pbest = -1

    with pytest.raises(ValueError):
        distrib.pbest = 1.5
