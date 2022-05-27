from nexoclom.math import minmaxmean
import numpy as np
import pytest


@pytest.mark.math
def test_minmaxmean():
    array = np.random.random(50)
    assert (np.nanmin(array), np.nanmax(array), np.nanmean(array)) == minmaxmean(array)