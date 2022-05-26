import pytest

from ..distribution import Distribution
from ..normal import Normal


def test_Normal___init__():
    distrib = Normal(-1.0, 4.0)
    assert isinstance(distrib, Distribution)
    assert isinstance(distrib, Normal)

    for a, v in ({"best": 4, "worst": -1, "pbest": 0.15, "pworst": 0.15}).items():
        assert getattr(distrib, a) == v

    distrib = Normal(4.0, 2.0, pbest=0.2, pworst=0.1)

    for a, v in ({"best": 2.0, "worst": 4, "pbest": 0.2, "pworst": 0.1}).items():
        assert getattr(distrib, a) == v

    with pytest.raises(ValueError):
        Normal(0.0, 3.0, 0.7, 0.4)


def test_Normal_draw():
    # Worst < Best
    distrib = Normal(-1.0, 4.0, pworst=0.05, pbest=0.1)

    assert distrib.draw(1 - distrib.pbest) == distrib.best

    assert distrib.draw(distrib.pworst) == distrib.worst

    # Worst > Best
    distrib = Normal(4.0, 2.0, pbest=0.2, pworst=0.1)

    assert distrib.draw(distrib.pbest) == pytest.approx(distrib.best)

    assert distrib.draw(1 - distrib.pworst) == pytest.approx(distrib.worst)

    # Call without args
    ## Probability cannot be zero
    distrib = Normal(1.0, 2.0, pbest=1e-12, pworst=1e-12)

    assert distrib.worst <= distrib.draw() <= distrib.best
