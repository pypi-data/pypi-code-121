

class Numpy:
    """The numpy object holds a reference to a tensor object in the zetane engine, which can be visualized in a variety of ways or used to power other graphics principles.

    Args:
        nsocket (Socket): Socket to communicate with the Zetane Engine.
        data (numpy, optional): A numpy array of any N dimensions.

    Returns:
        Numpy: A zetane object for a numpy array.
    """
    def __init__(self, nsocket, data=None, filepath=None):
        pass


    def update(self, data=None, filepath=None):
        """Send data to Zetane to update the Numpy array. Should only define either data or filepath, not both.

        Args:
            data (numpy.array, optional): data to be sent to Zetane.
            filepath (str, optional): Path to a .npy or .npz file.
        
        Returns:
            Numpy: A zetane numpy object that can be chained.
        """
        return self


    def read_as_1d_data(self, read_as_1d=False):
        """A utility function for treating a numpy array as a 1D vector. This is used to power certain types of visualizations

        Args:
            read_as_1d (bool): Toggles reading the numpy array as 1D.

        Returns:
            Numpy: A zetane numpy object that can be chained.
        """
        return self


    def visualize(self, viz=True):
        """Toggles visualization of the numpy vector. Useful for sending raw data into the engine.

        Args:
             viz (bool): Toggles visualizing the numpy vector.
        """
        return self
