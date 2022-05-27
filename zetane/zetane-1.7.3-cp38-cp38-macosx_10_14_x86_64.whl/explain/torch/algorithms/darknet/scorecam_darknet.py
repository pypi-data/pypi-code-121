

class CamExtractorDarknet:
    """
    Extracts class activation mapping (CAM) features from the model.

    Args:
         model (torch.nn.Module): the model used
         target_layer (str): the layer to visualize

    Attributes:
         model (torch.nn.Module): the model used
         target_layer (str): the layer to visualize
         gradients (torch.Tensor): the gradients at the target layer
    """
    def __init__(self, model, target_layer):
        pass


    def forward_pass_on_convolutions(self, x):
        return self


    def forward_pass_on_classifier(self, x):
        """
        Does a full forward pass on the model. Applies only to torchvision models which have 'classifier' submodules/blocks.

        Args:
            x (torch.Tensor): inputs to the neural network

        Returns:
            torch.Tensor: conv_output as the output of the target layer
            torch.Tensor: x as the output of the last layer
        """
        return self


    def forward_pass(self, x):
        """
        Does a full forward pass on the model. Treats self.model as a torchvision model that employs 'features' and 'classifier' submodules by default, fallbacks to a standard sequential model if not.

        Args:
            x (torch.Tensor): inputs to the neural network

        Returns:
            torch.Tensor: conv_output as the output of the target layer
            torch.Tensor: x as the output of the last layer
        """
        return self


class ScoreCamDarknet:
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
    def __init__(self, model, target_layer):
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
