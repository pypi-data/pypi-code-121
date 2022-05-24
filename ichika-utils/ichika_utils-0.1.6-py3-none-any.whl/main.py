import asyncio
import numpy as np
import uvloop
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path


class IchikaUtils:
    def __init__(self):
        self.self = self
        
    async def calcMean(self, array: list):
        """Calculates the mean from a list of data

        Args:
            array (list): _description_

        Returns:
            _type_: _description_
        """
        a = np.array(array)
        return np.mean(a)
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcStats(self, array: list):
        """Returns the mean, median, standard deviation, and variance from a list of data

        Args:
            array (list): list of data

        Returns:
            _type_: dict
        """
        npyArray = np.array(array)
        return {"mean": np.mean(npyArray), "median": np.median(npyArray), "std": np.std(npyArray), "variances": np.var(npyArray)
                , "spread": np.ptp(npyArray)}
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def calcShape(self, xList: list):
        """Calculates the shape of the data

        Args:
            xList (list): list of data

        Returns:
            _type_: numpy shape
        """
        xListArray = np.array(xList)
        rowShape = xListArray[:, np.newaxis]
        return rowShape.shape
        
    async def graphHistoRandn(self, amount: int):
        """Graphs a Histogram randomly

        Args:
            amount (int): The amount of data to be randomly generated and plotted
        """
        fig, ax = plt.subplots()
        np.random.seed(19680801)
        n, bins = np.histogram(amount, 50)
        left = bins[:-1]
        right = bins[1:]
        bottom = np.zeros(len(left))
        top = bottom + n
        XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T
        barpath = path.Path.make_compound_path_from_polys(XY)
        patch = patches.PathPatch(barpath)
        ax.add_patch(patch)
        ax.set_xlim(left[0], right[-1])
        ax.set_ylim(bottom.min(), top.max())
        plt.show()
        
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def graphSetHistogram(self, data: list):
        """Graphs a histogram of the data

        Args:
            data (list): list of data
        """
        fig, ax = plt.subplots()
        (hist, bin_edges) = np.histogram(data)
        left = bin_edges[:-1]
        right = bin_edges[1:]
        bottom = np.zeros(len(left))
        top = bottom + hist
        XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T
        barpath = path.Path.make_compound_path_from_polys(XY)
        patch = patches.PathPatch(barpath)
        ax.add_patch(patch)
        ax.set_xlim(left[0], right[-1])
        ax.set_ylim(bottom.min(), top.max())
        plt.show()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())        
        
        
    
    
    
    
