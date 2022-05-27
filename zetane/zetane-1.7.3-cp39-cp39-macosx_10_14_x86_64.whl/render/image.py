

class Image:
    """The image object holds a reference to an image in the Zetane universe, which is either a 2D representation of numpy data in the format Height x Width x Depth or a string to a filepath.

        Args:
            nsocket (Socket): Socket to communicate with the Zetane Engine.
            data (numpy, optional): A numpy array of the format Height x Width x Depth that will be interpreted as a 2D image. Also takes an array of numpy arrays for multiple images.
            filepath (str, optional): A string to an image filepath, or an array of strings for multiple images.

        Returns:
            Image: An object wrapping an image in the Zetane engine.
    """
    def __init__(self, nsocket, data=None, filepath=None):
        pass


    def data(self, nparray):
        """
            Wrap data properly so that images can be rendered in Zetane.

        Args:
            nparray (numpy array list): list of numpy arrays or numpy array.
        """
        return self


    def highlight(self, rgb=(1.0, 1.0, 1.0), amount=0.5):
        """
            Set the highlight color (rgb) with a blend amount between 0 and 1

        Args:
            rgb (tuple): an (r,g,b) tuple representing the highlight hue.
            amount (float): factor between [0 = original rgb, 1 = highlight rgb].

        Returns:
            Image: Returns the image object so that calls can be chained.
        """
        return self


    def update(self, data=None, filepath=None):
        """
            Send data to Zetane to update the Image. Should only define either data or filepath, not both.

        Args:
            data (numpy array): Numpy array containing image data to be sent to Zetane.
            filepath (str list): Path or list of paths to .npy or .npz files.

        Returns:
            Image: Returns the image object so that calls can be chained.
        """
        return self
