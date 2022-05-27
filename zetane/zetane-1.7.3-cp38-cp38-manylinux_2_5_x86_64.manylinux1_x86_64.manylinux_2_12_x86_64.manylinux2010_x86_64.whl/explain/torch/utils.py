

def get_layers(model):
    """
    Extracts the layers of a PyTorch neural network as a list.

    Args:
        model (torch.nn.Module): the model with the layers to be extracted

    Returns:
        list(torch.nn.Module): list of the layers of the neural network
    """
    return None


def get_darknet_layers(model):
    """
    Extracts the layers of a PyTorch neural network as a list.

    Args:
        model (torch.nn.Module): the model with the layers to be extracted

    Returns:
        list(torch.nn.Module): list of the layers of the neural network
    """
    return None


def convert_to_grayscale(im_as_arr):
    """
    Converts 3d image to grayscale.

    Args:
        im_as_arr (np.ndarray): RGB image with shape (D,W,H)

    Returns:
        grayscale_im (np.ndarray): grayscale image with shape (1,W,D)
    """
    return None


def save_gradient_images(gradient, path_to_file):
    """
    Exports the original gradient image.

    Args:
        gradient (np.ndarray): Numpy array of the gradient with shape (3, 224, 224)
        file_path (str): File name to be exported

    Returns:
        np.ndarray: the transposed array in WxHxC form
    """
    return None


def save_class_activation_images(org_img, activation_map, file_path, map_type='heatmap'):
    """
    Generates CAM heatmaps, either saves and returns them directly or overlays them on the original image first.

    Args:
        org_img (PIL.Image): Original image
        activation_map (np.ndarray): activation map (grayscale) 0-255
        file_path (str): File name of the exported image

    Returns:
        np.ndarray: the heatmap or overlaid array, HxWx3 (channels last) format with float values between 0-1
    """
    return None


def apply_colormap_on_image(org_im, activation, colormap_name):
    """
    Applies the colored activation heatmap on the original image.

    Args:
        org_img (PIL.Image): Original image
        activation_map (np.ndarray): Activation map (grayscale) 0-255
        colormap_name (str): Name of the colormap, standard matplotlib map names are used

    Returns:
        np.ndarray: no_trans_heatmap as the heatmap with no transparency
        np.ndarray: heatmap_on_image as the heatmap overlaid on the image
    """
    return None


def format_np_output(np_arr):
    """
    This is a (kind of) bandaid fix to streamline saving procedure. It converts all the outputs to the same format which is 3xWxH with using sucecssive if clauses.

    Args:
        np_arr (np.ndarray): Matrix of shape 1xWxH or WxH or 3xWxH

    Returns:
        np.ndarray: NumPy array with chape CxWxH
    """
    return None


def save_image(im, path):
    """
    Saves a numpy array or PIL image as an image.

    Args:
        im_as_arr (np.ndarray): Matrix of shape DxWxH
        path (str): Path to the image

    Returns:
        None
    """
    return None


def preprocess_image(pil_im, mean=None, std=None, size=(224, 224), resize_im=True):
    """
    Processes image to produce inputs for PyTorch CNNs.

    Args:
        pil_im (PIL.Image, ndarray or torch.Tensor): PIL Image or numpy/torch array to process
        mean (list): mean values between 0 and 1 for each channel (default: None)
        std (list): standard deviation values between 0 and 1 for each channel (default: None)
        size (tuple(int, int)): desired size of the output image, must be compatible with the neural network (default: (224, 224))
        resize_im (bool): to resize or not (default: True)
    Returns:
        im_as_var (torch variable): Variable that contains processed float tensor
    """
    return None


def recreate_image(im_as_var, reverse_mean=None, reverse_std=None):
    """
    Recreates original images from a torch variable, through a sort of reverse preprocessing process.

    Args:
        im_as_var (torch variable): Image to recreate
        reverse_mean (list(float)): inverted mean if any mean normalization has been performed on prep_img. None defaults to ImageNet metrics (default: None)
            e.g. if means for three channels were [0.485, 0.456, 0.406], inv_mean=[-0.485, -0.456, -0.406]
        reverse_std (list(float)): inverted standard deviation if any std normalization has been performed on prep_img. None defaults to ImageNet metrics (default: None)
            e.g. if stds for three channels were [0.229, 0.224, 0.225], inv_std=[1/0.229, 1/0.224, 1/0.225]
    Returns:
        recreated_im (numpy arr): Recreated image in array
    """
    return None


class CamExtractor:
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
    def __init__(self, model):
        pass


    def save_gradient(self, grad):
        """
        Saves the current gradients to a class attribute.

        Args:
            grad (torch.Tensor): the gradients at the target layer
        """
        return self


    def forward_pass_on_convolutions(self, x):
        """
        Does a forward pass on convolutions, hooks the function at given layer. Applies only to torchvision models which have the 'features' submodules/blocks.

        Args:
            x (torch.Tensor): inputs to the neural network

        Returns:
            torch.Tensor: x as the output of the last convolutional layer
        """
        return self


    def forward_pass_on_classifier(self, x):
        """
        Does a full forward pass on the model. Applies only to torchvision models which have 'classifier' submodules/blocks.

        Args:
            x (torch.Tensor): inputs to the neural network

        Returns:
            torch.Tensor: x as the output of the last layer
        """
        return self


    def forward_pass(self, x):
        """
        Does a full forward pass on the model. Treats self.model as a torchvision model that employs 'features' and 'classifier' submodules by default, fallbacks to a standard sequential model if not.

        Args:
            x (torch.Tensor): inputs to the neural network

        Returns:
            torch.Tensor: x as the output of the last layer
        """
        return self
