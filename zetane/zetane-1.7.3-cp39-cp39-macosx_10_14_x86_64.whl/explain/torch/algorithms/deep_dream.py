

class DeepDream:
    """
    Produces an image that minimizes the loss of a convolution operation for a specific layer and filter given an input image.

    Args:
        model (torch.nn.Module): the model used
        selected_layer (str): the layer to visualize
        selected_filter (int): the filter in the selected layer to be visualized
        im_path (str): path to the image to be dreamt on
        size (tuple(int)): size of the input image
        out_dir (str): output directory

    Attributes:
        model (torch.nn.Module): the model used
        selected_layer (str): the layer to visualize
        selected_filter (int): the filter in the selected layer to be visualized
        im_path (str or PIL Image): (path to) the image to be dreamt on
        size (tuple(int)): size of the input image
        out_dir (str): output directory
        created_image (PIL image): the final image dreamt by the network. WxHx3 (channels last) format with int values between 0-255
    """
    def __init__(self, model, selected_layer, selected_filter, im_path, size, out_dir):
        pass


    def hook_layer(self):
        """
        Registers a forward hook to the model, which triggers the hook_function when a prespecified layer is reached during a forward pass.

        Returns:
            None
        """
        return self


    def dream(self):
        """
        Visualizes the selected layer through using a given image as input and minimizing the mean of the output of the specified layer and filter using PyTorch hooks.

        Returns:
            np.ndarray: dream output image as a NumPy array, HxWx3 (channels last) format with float values between 0-1
        """
        return self
