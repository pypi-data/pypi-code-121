import numpy as np
from scipy import stats
import asyncio
import uvloop

class BasicCalc:
    def __init__(self):
        self.self = self
        
    async def describeData(self, data: list):
        """Calculates the mean, median, standard deviation, and variance of the data
        
        Args:
            data (list): list of data
            
        Returns:
            _type_: class
        """
        npyArray = np.array(data)
        return stats.describe(npyArray)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcMode(self, data: list):
        """Returns the mode of the data

        Args:
            data (list): _list of data
            
        Returns:
            _type_: array
        """
        array = np.array(data)
        return stats.mode(array, axis=None)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcMean(self, data: list):
        """Returns the mean of the data

        Args:
            data (list): _list of data
            
        Returns:
            _type_: float
        """
        array = np.array(data)
        return stats.tmean(array)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcStd(self, data: list):
        """Calculates the standard deviation of the data

        Args:
            data (list): list of data

        Returns:
            _type_: float
        """
        npArr = np.array(data)
        return stats.tstd(npArr)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcVariance(self, data: list):
        """Calculates the variance of the data

        Args:
            data (list): list of data

        Returns:
            _type_: float
        """
        npArr = np.array(data)
        return stats.tvar(npArr)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcSem(self, dataSem: list):
        """Calculates the standard error of the mean
        
        Args: 
            dataSem (list): list of data
            
        Returns:
            __type__: float
        """
        a = np.array(dataSem)
        return stats.tsem(a)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcVar(self, data: list):
        """_summary_

        Args:
            data (list): list of data
            
        Returns:
            _type_: float
        """
        ar = np.array(data)
        return stats.tvar(ar)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcMin(self, data: list): 
        """_summary_

        Args:
            data (list): list of data
            
        Returns:
            _type_: float
        """
        arr = np.array(data)
        return stats.tmin(arr)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcMax(self, data: list): 
        """_summary_

        Args:
            data (list): list of data
            
        Returns:
            _type_: float
        """
        arr = np.array(data)
        return stats.tmax(arr)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcIqr(self, data: list):
        """_summary_

        Args:
            data (list): list of data
            
        Returns:
            _type_: float
        """
        aaarr = np.array(data)
        return stats.iqr(aaarr)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

