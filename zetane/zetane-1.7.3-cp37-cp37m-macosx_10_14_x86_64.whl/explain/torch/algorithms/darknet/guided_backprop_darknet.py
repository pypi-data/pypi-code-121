

class GuidedBackpropDarknet:
    """
   Produces gradients generated with guided backpropagation from the given image. Guided backpropagation zeroes out the negative gradients during backpropagation for clarity.

   Args:
       model (torch.nn.Module): the model used

   Attributes:
       model (torch.nn.Module): the model used
       gradients (torch.Tensor): the gradients at the target layer
       forward_relu_outputs (list): list of reLU layer outputs as torch tensors
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


    def update_relus(self):
        """
        Updates ReLU activation functions so that they:
            1) store the output in forward pass
            2) impute zero for gradient values that are less than zero

        Returns:
            None
        """
        return self


    def generate_gradients(self, input_image, target_class):
        """
        Generates gradients for a given input image and target class through backpropagation.

        Args:
            input_image (torch.Tensor): input image as a PyTorch tensor
            target_class (int): the class for which the images will be generated

        Returns:
            torch.Tensor: the gradients generated through backpropagation, HxWx3 (channels last) format with float values between 0-1
        """
        return self
