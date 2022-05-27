

class CNNLayerVisualizationDarknet:
    """
    Produces an image that minimizes the loss of a convolution operation for a specific layer and filter.

    Args:
        model (torch.nn.Module): the model used
        selected_layer (str): the layer to visualize
        selected_filter (int): the filter in the selected layer to be visualized
        size (tuple(int)): size of the input image
        out_dir (str): output directory

    Attributes:
        model (torch.nn.Module): the model used
        selected_layer (str): the layer to visualize
        selected_filter (int): the filter in the selected layer to be visualized
        size (tuple(int)): size of the input image
        out_dir (str): output directory
        created_image (PIL image): the final image visualized by the network, WxHx3 (channels last) format with int values between 0-255
    """
    def __init__(self, model, selected_layer, selected_filter, size, out_dir):
        pass


    def hook_layer(self):
        """
        Registers a forward hook to the model, which triggers the hook_function when a prespecified layer is reached during a forward pass.

        Returns:
            None
        """
        return self


    def visualise_layer_with_hooks(self):
        """
        Visualizes the selected layer through using a randomly generated image as input and minimizing the mean of the output of the specified layer and filter using PyTorch hooks.

        Returns:
            np.ndarray: visualized layer image as a NumPy array, HxWx3 (channels last) format with float values between 0-1
        """
        return self


    def visualise_layer_without_hooks(self):
        """
        Visualizes the selected layer through using a randomly generated image as input and minimizing the mean of the output of the specified layer and filter without using PyTorch hooks.

        Returns:
            np.ndarray: visualized layer image as a NumPy array
        """
        return self
