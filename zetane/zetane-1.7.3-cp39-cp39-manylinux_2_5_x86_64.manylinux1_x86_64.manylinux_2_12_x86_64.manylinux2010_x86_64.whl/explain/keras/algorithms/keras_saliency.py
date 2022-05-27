

class SaliencyMask:
    """Base class for saliency masks. Alone, this class doesn't do anything.
    
       Constructs a SaliencyMask
       
       Args:
            model: the keras model used to make prediction
            output_index: the index of the node in the last layer to take derivative on
            
    """
    def __init__(self, model, output_index=0):
        pass


    def get_mask(self, input_image):
        """Returns an unsmoothed mask.

        Args:
            input_image: input image with shape (H, W, 3).
        """
        return self


    def get_smoothed_mask(self, input_image, stdev_spread=.2, nsamples=50):
        """Returns a mask that is smoothed with the SmoothGrad method.

        Args:
            input_image: input image with shape (H, W, 3).
        """
        return self


class GradientSaliency:
    """A SaliencyMask class that computes saliency masks with a gradient."""
    def __init__(self, model, output_index=0):
        pass


    def get_mask(self, input_image):
        """Returns a vanilla gradient mask.

        Args:
            input_image: input image with shape (H, W, 3).
        """
        return self
