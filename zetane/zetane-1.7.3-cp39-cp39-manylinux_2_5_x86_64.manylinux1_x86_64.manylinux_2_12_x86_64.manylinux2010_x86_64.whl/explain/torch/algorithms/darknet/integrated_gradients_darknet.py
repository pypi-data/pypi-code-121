

class IntegratedGradientsDarknet:
    """
    Produces gradients generated with integrated gradients from the image. For more info, see: 'M. Sundararajan, A. Taly, Q. Yan. Axiomatic Attribution for Deep Networks https://arxiv.org/abs/1703.01365'

    Args:
        model (torch.nn.Module): the model used

    Attributes:
        model (torch.nn.Module): the model used
        gradients (torch.Tensor): the backpropagated gradients
    """
    def __init__(self, model):
        pass


    def hook_input(self, input_tensor):
        """
        Registers a forward hook to the input tensor, which saves the gradients of the input tensor.

        Args:
            input_tensor (torch.Tensor): the input tensor to hook

        Returns:
            None
        """
        return self


    def generate_images_on_linear_path(self, input_image, steps):
        """
        Generates the list of uniform intervals for an image and step count. Used to generate the composed IG image.

        Args:
            input_image (torch.Tensor): input image as a PyTorch tensor
            steps (int): for how many steps to apply the algorithm

        Returns:
            list(np.ndarray): the list of uniform intervals for the given number of steps
        """
        return self


    def generate_gradients(self, input_image, target_class):
        """
        Generates gradients for a given input image and target class through backpropagation.

        Args:
            input_image (torch.Tensor): input image as a PyTorch tensor
            target_class (int): the class for which the images will be generated

        Returns:
            torch.Tensor: the gradients generated through backpropagation
        """
        return self


    def generate_integrated_gradients(self, input_image, target_class, steps):
        """
        Applies the integrated gradients algorithm given an input image and target class by linearly composing multiple attributions determined by the number of steps.

        Args:
            input_image (torch.Tensor): input image as a PyTorch tensor
            target_class (int): the class for which the images will be generated
            steps (int): for how many steps to apply the algorithm

        Returns:
            np.ndarray: the integrated gradients output image, 3xHxW (channels first) format with float values between 0-1
        """
        return self
