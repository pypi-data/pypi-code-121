import numpy as np


class SurfaceMap:
    """Base class for surface maps."""
    def __init__(self, nlon=361, nlat=181, map=None):
        """
        
        :param nlon: Number of longitude bins
        :param nlat: Number of latitude bins
        :param map: If present, the surface map to use
        """
