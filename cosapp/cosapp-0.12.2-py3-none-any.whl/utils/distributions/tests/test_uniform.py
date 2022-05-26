import pytest

from ..distribution import Distribution
from ..uniform import Uniform


def test_Uniform___init__():
    distrib = Uniform(-1.0, 4.0)
    assert isinstance(distrib, Distribution)
    assert isinstance(distrib, Uniform)

    for a, v in ({"best": 4, "worst": -1, "pbest": 0.15, "pworst": 0.15}).items():
        assert getattr(distrib, a) == v

    distrib = Uniform(4.0, 2.0, pbest=0.2, pworst=0.1)

    for a, v in ({"best": 2.0, "worst": 4, "pbest": 0.2, "pworst": 0.1}).items():
        assert getattr(distrib, a) == v

    with pytest.raises(ValueError):
        Uniform(0.0, 3.0, 0.7, 0.4)


def test_Uniform_draw():
    # Worst < Best
    distrib = Uniform(-1.0, 4.0, pworst=0.05, pbest=0.1)
    assert distrib.draw(1 - distrib.pbest) == pytest.approx(distrib.best)
    assert distrib.draw(distrib.pworst) == pytest.approx(distrib.worst)

    # Worst > Best
    distrib = Uniform(4.0, 2.0, pbest=0.2, pworst=0.1)
    assert distrib.draw(distrib.pbest) == pytest.approx(distrib.best)
    assert distrib.draw(1 - distrib.pworst) == pytest.approx(distrib.worst)

    # Call without args
    distrib = Uniform(1.0, 2.0, pbest=0.0, pworst=0.0)
    assert distrib.worst <= distrib.draw() <= distrib.best
