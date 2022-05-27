import numpy as np
import astropy.units as u
from nexoclom.math import random_deviates_1d, random_deviates_2d
from nexoclom.math.distributions import MaxwellianDist, sputdist
from nexoclom.math import Histogram, smooth
import pytest



@pytest.mark.math
def test_random_deviates():
    # Test against gaussian
    nums = np.random.random(3)
    mean = nums[1] * 6 - 3
    sigma = nums[2] * 3
    x0 = np.linspace(-10, 10, 1000)
    f0 = np.exp(-(x0 - mean)**2/sigma**2)

    dev = random_deviates_1d(x0, f0, int(1e7))
    print(dev.mean(), mean)
    print(dev.std(), sigma/np.sqrt(2))
    # assert dev.mean() == pytest.approx(mean, abs=1e-2)
    # assert dev.std() == pytest.approx(sigma/np.sqrt(2), abs=1e-2)

    hist = Histogram(dev, bins=x0)
    hist.histogram /= hist.histogram.mean()
    f0_ = np.exp(-(hist.x - mean)**2/sigma**2)
    f0_ /= f0_.mean()
    print(np.mean((hist.histogram-f0_)**2),np.std((hist.histogram-f0_)**2))
    # assert np.mean((hist.histogram-f0_)**2) == pytest.approx(0, abs=1e-3)
    # assert np.std((hist.histogram-f0_)**2) == pytest.approx(0, abs=1e-3)

    # Test against maxwellian
    v1 = np.linspace(0, 10, 1000)*u.km/u.s
    f1 = MaxwellianDist(v1, 1500.*u.K, 'Na')
    dev = random_deviates_1d(v1, f1, int(1e8))
    hist = Histogram(dev.value, bins=v1.value)
    hist.histogram /= hist.histogram.mean()
    f1_ = MaxwellianDist(hist.x*u.km/u.s, 1500.*u.K, 'Na')
    f1_ /= f1_.mean()
    print(np.mean((hist.histogram-f1_)**2),np.std((hist.histogram-f1_)**2))
    assert np.mean((hist.histogram-f1_)**2) == pytest.approx(0, abs=1e-3)
    assert np.std((hist.histogram-f1_)**2) == pytest.approx(0, abs=1e-3)

if __name__ == '__main__':
    test_random_deviates()