

class InvertedRepresentation:
    """
    An algorithm that aims to generate the original image using the learned features of a given layer. For more info, see: 'A. Mahendran, A. Vedaldi. Understanding Deep Image Representations by Inverting Them, https://arxiv.org/abs/1412.0035'.

    Args:
        model (torch.nn.Module): the model used
        out_dir (str): output directory

    Attributes:
        model (torch.nn.Module): the model used
        out_dir (str): output directory
     """
    def __init__(self, model, out_dir):
        pass


    def alpha_norm(self, input_matrix, alpha):
        """
        Converts the input matrix to vector, and then calculates its alpha norm.

        Args:
            input_matrix (torch.Tensor): the image that is being optimized
            alpha (float): alpha coefficient for exponential component

        Returns:
            float: sum of the alpha exponential of the flattened input matrix
        """
        return self


    def total_variation_norm(self, input_matrix, beta):
        """
        Total variation norm is the second norm in the paper, represented as R_V(x).

        Args:
            input_matrix (torch.Tensor): the image that is being optimized
            beta (float): beta coefficient for exponential component

        Returns:
            float: sum of the variation of the input matrix
        """
        return self


    def euclidian_loss(self, org_matrix, target_matrix):
        """
        Euclidian loss is the main loss function in the paper: ||fi(x) - fi(x_0)||_2^2& / ||fi(x_0)||_2^2

        Args:
            org_matrix (torch.Tensor): the original output of the target layer
            target_matrix (torch.Tensor): the output of the target layer that is being optimized

        Returns:
            torch.Tensor: the normalized euclidean distance between the two matrices
        """
        return self


    def get_output_from_specific_layer(self, x, layer_id):
        """
        Saves the output after a forward pass until nth layer. This operation could be done with a forward hook too, but this method is deemed more straightforward.

        Args:
            x (torch.Tensor): the input to the neural network
            layer_id (str): the index/name of the layer to target

        Returns:
            torch.Tensor: the output of the layer with the specified layer_id
        """
        return self


    def generate_inverted_image_specific_layer(self, input_image, inv_mean, inv_std, target_layer):
        """
        Generates an inverted representation of the input image using the learned features of a specific network layer.

        Args:
            input_image (torch.Tensor): input image to the network as tensor
            inv_mean (list(float)): inverted mean if any mean normalization has been performed on prep_img.
                e.g. if means for three channels were [0.485, 0.456, 0.406], inv_mean=[-0.485, -0.456, -0.406]
            inv_std (list(float)): inverted standard deviation if any std normalization has been performed on prep_img.
                e.g. if stds for three channels were [0.229, 0.224, 0.225], inv_std=[1/0.229, 1/0.224, 1/0.225]
            target_layer (str): the index/name of the layer to target

        Returns:
            np.ndarray: inverted representation output image as a NumPy array, HxWx3 (channels last) format with float values between 0-1
        """
        return self
