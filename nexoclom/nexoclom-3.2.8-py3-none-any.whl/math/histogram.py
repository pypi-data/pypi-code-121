import numpy as np
from sklearn.neighbors import KDTree, BallTree


class Histogram:
    """ Wrapper for np.histogram that makes the x-axis the center of each bin.
    Returns a class with everything self-contained.
    """
    def __init__(self, a, bins=10, range=None, normed=None, weights=None,
                 density=None):
        hist, x = np.histogram(a, bins, range, normed, weights, density)
        self.histogram = hist.astype(np.float)
        self.dx = x[1]-x[0]  # width of the bin
        self.x = x[:-1] + self.dx/2
        
    # def __repr__(self):
    #     string = f"{'x':6}{'#':6}\n"
    #     string += '-'*12 + '\n'
    #     for x, h in zip(self.x, self.histogram):
    #         string += f"{x:6f}{h:6f}\n"
    #
    #     return string
    
    def __str__(self):
        return self.__repr__()
        
        
class Histogram2d:
    """ Wrapper for np.histogram2d that makes the x,y axes the centers of each bin.
    Returns a class with everything self-contained.
    """
    def __init__(self, ptsx, ptsy, bins=10, range=None, normed=None, weights=None,
                 density=None):
        hist, x, y = np.histogram2d(ptsx, ptsy, bins, range, normed, weights, density)
        self.histogram = hist
        self.dx, self.dy = x[1]-x[0], y[1]-y[0]
        self.x = x[:-1] + self.dx/2
        self.y = y[:-1] + self.dy/2


class HistogramSphere:
    def __init__(self, longitude, latitude, weights=None,
                 dphi=np.deg2rad(5), bins=(180, 90)):
        ptsx = np.cos(longitude) * np.cos(latitude)
        ptsy = np.sin(longitude) * np.cos(latitude)
        ptsz = np.sin(latitude)

        if isinstance(bins, tuple) or isinstance(bins, list):
            self.bins = bins
        elif isinstance(bins, int):
            self.bins = (bins, bins)
        else:
            raise TypeError('bins must be an int, tuple, or list')

        self.dphi = dphi

        self.longitude = np.linspace(0, 2*np.pi, bins[0], endpoint=False)
        self.longitude += (self.longitude[1]-self.longitude[0])/2.
        self.latitude = np.linspace(-np.pi/2, np.pi/2, bins[1], endpoint=False)
        self.latitude += (self.latitude[1]-self.latitude[0])/2.

        gridlongitude, gridlatitude = np.meshgrid(self.longitude, self.latitude)
        gridx = (np.cos(gridlongitude) * np.cos(gridlatitude)).flatten()
        gridy = (np.sin(gridlongitude) * np.cos(gridlatitude)).flatten()
        gridz = np.sin(gridlatitude).flatten()
        grid = np.array([gridx, gridy, gridz]).T

        tree = KDTree(np.array([ptsx, ptsy, ptsz]).T)
        ind = tree.query_radius(grid, self.dphi)
        if weights is None:
            result = np.array([len(x) for x in ind])
        else:
            result = np.array([np.sum(weights[x]) for x in ind])

        self.histogram = result.reshape(gridlatitude.shape)
