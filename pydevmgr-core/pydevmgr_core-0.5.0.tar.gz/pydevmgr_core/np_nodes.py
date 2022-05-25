""" some nodes that required numpy to be executed if numpy is not installed theses nodes will not be loaded """

from .base import  BaseNode, NodeAlias, NodeAlias1, record_class
from collections import deque
from typing import Optional, List, Tuple
import numpy as np
from enum import Enum 

__all__ = [
"DISTRIBUTION", 
"Noise",
"NoiseAdder",
"Histogram",
"MeanFilter", 
"MaxFilter", 
"MinFilter", 
"VarianceFilter", 
"RmsFilter", 
"MedianFilter", 
"PickToValleyFilter"
]

def _random(mean, scale, size):
    return np.random.random(size)*scale+mean


class DISTRIBUTION(Enum):
    RANDOM = "random"
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
DISTRIBUTION.RANDOM.func = _random
DISTRIBUTION.NORMAL.func = np.random.normal
DISTRIBUTION.LOGNORMAL.func = np.random.lognormal

@record_class
class Noise(BaseNode):
    """ Node returning random value 

    Config:
        mean (optional, float): centre of the distribution (default 0.0)
        scale (optional, float): Standard deviation (spread or width) (default 1.0)
        size : Returned array size (default is scalar number = None)
        distribution (DISTRIBUTION, str): "random", "normal", "lognormal"

    """
    class Config(BaseNode.Config):
        type: str = "Noise"
        mean: float = 0.0 # Mean ("centre") of the distribution
        scale: float = 1.0 # Standard deviation (spread or "width") of the distribution
        size: Optional[List[int]] = None
        distribution: DISTRIBUTION = DISTRIBUTION.NORMAL
    
    def fget(self):
        c = self.config
        return DISTRIBUTION(c.distribution).func(c.mean, c.scale, c.size)
        
@record_class
class NoiseAdder(NodeAlias1):
    """ NodeAlias1, add anode to the original node value 
        
    Config:
        scale (optional, float): Standard deviation (spread or width) (default 1.0)
        distribution (DISTRIBUTION, str): "random", "normal", "lognormal"
    """
    class Config(NodeAlias1.Config):
        type: str = "NoiseAdder"
        scale: float = 1.0 # Standard deviation (spread or "width") of the distribution
        distribution: DISTRIBUTION = DISTRIBUTION.NORMAL
    
    def fget(self, value):
        c = self.config
        return DISTRIBUTION(c.distribution).func(value, c.scale)
        
@record_class
class Histogram(NodeAlias1):
    """ NodeAlias1, return an histogram from original node value 

    Config:
        bins (3 tuple): (min, max, nbin)   
    
    Feature:
        reset() method rebuild the bins array and clean histogram 
        bins  attribute is the bins array built at init or reset
    """
    class Config(NodeAlias1.Config):
        type: str = "Histogram"
        bins: Tuple[float,float,int] = (-100,100,10)        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()
    
    @property
    def bins(self):
        return self._bins
    
    def reset(self):
        min,max,n = self.config.bins
        self._bins = np.linspace(min,max,n)
        self._hist = [0]*(len(self._bins)-1)
        
    def fget(self, value):
        min,max,_ = self.config.bins
        if value<min or value>max:
            return self._hist
        i = np.digitize(value, self._bins)    
        self._hist[i-1] += 1
        return self._hist
            

class _Filter(NodeAlias1):
    class Config(NodeAlias1.Config):
        size : int = 10
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self._data = deque([], self.config.size)
    
    def fget(self, value):
        self._data.append(value)
        return self._func(self._data)

@record_class(overwrite=True)
class MeanFilter(_Filter):
    """ NodeAlias1, Filter input Node by mean
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """
    class Config(_Filter.Config):
        type = "MeanFilter"    
    _func = staticmethod(np.mean)    

@record_class(overwrite=True)
class MaxFilter(_Filter):
    """ NodeAlias1, Filter input Node by max
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """

    class Config(_Filter.Config):
        type = "MaxFilter"    
    _func = staticmethod(np.max)  
      
@record_class(overwrite=True)
class MinFilter(_Filter):
    """ NodeAlias1, Filter input Node by min
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """
    class Config(_Filter.Config):
        type = "MinFilter"    
    _func = staticmethod(np.min)

@record_class
class VarianceFilter(_Filter):
    """ NodeAlias1, Filter input Node by vartiance
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """
    class Config(_Filter.Config):
        type = "VarianceFilter"
    
    @staticmethod
    def _func(data):
        data = np.asarray(data)
        m = np.mean(data)
        return (data-m)**2/len(data)

@record_class
class RmsFilter(_Filter):
    """ NodeAlias1, Filter input Node by rms 
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """
    class Config(_Filter.Config):
        type = "RmsFilter"
    
    @staticmethod
    def _func(data):
        data = np.asarray(data)
        m = np.mean(data)
        return np.sqrt(  (data-m)**2/len(data) )         

@record_class
class MedianFilter(_Filter):
    """ NodeAlias1, Filter input Node by maedian
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """
    
    class Config(_Filter.Config):
        type = "MedianFilter"    
    _func = staticmethod(np.median)

@record_class
class PickToValleyFilter(_Filter):
    """ NodeAlias1, Filter input Node by pick to valley 
    
    The filter is apply on a sliding window of size ``size``. 
    
    Config:
        size (int): size of the filter (default 10)
    
    """
    class Config(_Filter.Config):
        type = "PickToValleyFilter"
    
    @staticmethod
    def _func(data):
        return  np.max(data)-np.min(data)  
   
del record_class, deque, Optional, List, Tuple, np, Enum         
