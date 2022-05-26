import json

import numpy
import pytest

from ..distribution import Distribution
from ..triangular import Triangular


def test_Triangular___init__():
    distrib = Triangular(-0.5, 1, 2)

    assert isinstance(distrib, Distribution)
    assert isinstance(distrib, Triangular)

    assert distrib.worst == -0.5
    assert distrib.likely == 1
    assert distrib.best == 2

    with pytest.raises(ValueError):
        Triangular(worst=9.0, likely=6.0, best=7.0)

    with pytest.raises(ValueError):
        Triangular(worst=1.0, likely=10.0, best=7.0)

    distrib2 = Triangular(worst=9.0, likely=6.0, best=5.0, pworst=0.0, pbest=0.0)
    for a, v in (
        {"worst": 9.0, "likely": 6.0, "best": 5.0, "pworst": 0.0, "pbest": 0.0}
    ).items():
        assert getattr(distrib2, a) == v

    with pytest.raises(
        ValueError,
        match=r"Likely value not within distribution bounds: \d+\.\d+ <= \d+\.\d+ <= \d+\.\d+\.",
    ):
        Triangular(4.0, 2.0, 6.0)


def test_Triangular___json__():
    distrib = Triangular(worst=9.0, likely=6.0, best=5.0, pworst=0.2, pbest=0.1)

    assert distrib.__json__() == {
        "worst": 9.0,
        "pworst": 0.2,
        "best": 5.0,
        "pbest": 0.1,
        "likely": 6.0,
    }


def test_Triangular_likely():
    distrib = Triangular(8.0, 9.0, 11.0)
    distrib.likely = 10.0
    assert 10.0 == distrib.likely

    distrib = Triangular(12.0, 10.0, 9.0, pworst=0.0, pbest=0.0)

    with pytest.raises(ValueError):
        distrib.likely = 8.0

    distrib.likely = 9.1
    assert 9.1 == distrib.likely


def test_Triangular_draw():
    # Symmetric case
    distrib = Triangular(8.0, 9.0, 10.0)

    assert distrib.draw(distrib.pworst) == pytest.approx(distrib.worst, abs=1e-7)
    assert distrib.draw(1.0 - distrib.pbest) == pytest.approx(distrib.best, abs=1e-7)
    assert distrib.draw(0.5) == pytest.approx(distrib.likely, abs=1e-7)

    # Unsymmetric case
    distrib = Triangular(8.0, 9.0, 10.0, pworst=0.2, pbest=0.1)

    assert distrib.draw(distrib.pworst) == pytest.approx(distrib.worst, abs=1e-7)
    assert distrib.draw(1.0 - distrib.pbest) == pytest.approx(distrib.best, abs=1e-7)

    loc = distrib.draw(0.0)
    scale = distrib.draw(1.0) - loc
    assert distrib.draw((distrib.likely - loc) / scale) == pytest.approx(
        distrib.likely, abs=1e-7
    )

    # Worst and best inverted
    distrib = Triangular(8.0, 5.0, 3.0, pworst=0.3, pbest=0.05)

    assert distrib.draw(1.0 - distrib.pworst) == pytest.approx(distrib.worst, abs=1e-7)
    assert distrib.draw(distrib.pbest) == pytest.approx(distrib.best, abs=1e-7)

    loc = distrib.draw(0.0)
    scale = distrib.draw(1.0) - loc
    assert distrib.draw((distrib.likely - loc) / scale) == pytest.approx(
        distrib.likely, abs=1e-7
    )

    # Test without quantile
    distrib = Triangular(8.0, 9.0, 10.0, 0.0, 0.0)
    assert distrib.worst <= distrib.draw() <= distrib.best
