

class Keras_IntegratedGradients:
    """A SaliencyMask class that implements the integrated gradients method.
    """


    def GetMask(self, input_image, input_baseline=None, nsamples=101, smoothing=True):
        """
        Gets the mask for the Integrated Gradients
        Args:
            input_image (string): Provides the input image
            input_baseline: Provides the baseline 
            nsamples: provides the number of samples
        Returns a integrated gradients mask.
        
        """
        return self
