import numpy as np
from pathlib import Path


def load_planck_data():
    path = Path(__file__).parent.parent / "data"
    sigma1_ns, sigma1_r = list(zip(*np.loadtxt(str(path / "sigma1.dat"), delimiter=",")))
    sigma2_ns, sigma2_r = list(zip(*np.loadtxt(str(path / "sigma2.dat"), delimiter=",")))

    return [sigma1_ns, sigma1_r, sigma2_ns, sigma2_r]
