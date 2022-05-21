from matplotlib import pyplot as plt
import numpy as np

class LinearEquation:
    def __init__(self, slope: float, intercept: float):
        self.slope = slope
        self.intercept = intercept

    def plot(self, interval: int, step = 1):
        fig, ax = plt.subplots()
        x = np.arange(1, interval, step)
        y = (self.slope * x) + self.intercept
        ax.plot(x, y)
        plt.show()