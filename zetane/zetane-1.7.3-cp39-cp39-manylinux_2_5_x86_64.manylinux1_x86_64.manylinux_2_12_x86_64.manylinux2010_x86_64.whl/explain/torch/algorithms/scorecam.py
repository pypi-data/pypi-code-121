

class ScoreCam:
    """
    Produces class activation maps using the Score-CAM algorithm. For more info, see: 'H. Wang, Z. Wang, M. Du, F. Yang, Z. Zhang, S. Ding, P. Mardziel, X. Hu. Score-CAM: Score-Weighted Visual Explanations for Convolutional Neural Networks https://arxiv.org/abs/1910.01279'.

    Args:
         model (torch.nn.Module): the model used
         target_layer (str): the layer to visualize

    Attributes:
         model (torch.nn.Module): the model used
         target_layer (str): the layer to visualize
         extractor (CamExtractor): Extractor for CAM features.
    """
    def __init__(self, model):
        pass


    def generate_cam(self, input_image, target_class=None):
        """
        Applies the Score-CAM algorithm using the CamExtractor.

        Args:
            input_image (torch.Tensor): input image as a PyTorch tensor
            target_class (int): the index of the class for which Grad-CAM images will be produced, defaults to the argmax of the model output if set to None (default: None)

        Returns:
            np.ndarray: the class activation map as an ndarray
        """
        return self
