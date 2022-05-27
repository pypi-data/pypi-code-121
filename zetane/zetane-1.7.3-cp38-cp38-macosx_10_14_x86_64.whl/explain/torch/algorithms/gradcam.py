

class GradCam:
    """
    Produces class activation maps using the Grad-CAM algorithm. For more info, see: 'R. R. Selvaraju, A. Das, R. Vedantam, M. Cogswell, D. Parikh, and D. Batra. Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization, https://arxiv.org/abs/1610.02391'

    Args:
         model (torch.nn.Module): the model used
         target_layer (str): the layer to visualize

    Attributes:
         model (torch.nn.Module): the model used
         target_layer (str): the layer to visualize
         extractor (CamExtractor): Extractor for CAM features
    """
    def __init__(self, model):
        pass


    def generate_cam(self, input_image, target_class=None):
        """
        Applies the Grad-CAM algorithm using the CamExtractor.

        Args:
            input_image (torch.Tensor): input image as a PyTorch tensor
            target_class (int, None): the index of the class for which Grad-CAM images will be produced, defaults to the argmax of the model output if set to None (default: None)

        Returns:
            np.ndarray: the class activation map as an ndarray, HxW format with float values between 0-1
        """
        return self
