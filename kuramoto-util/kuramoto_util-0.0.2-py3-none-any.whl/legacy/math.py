import numpy as np
import random

def from_lorentzian(gamma, omega_bar):
    y = random.uniform(0, 1)
    omega = gamma * np.tan(np.pi*(y-1/2)) + omega_bar
    return omega
