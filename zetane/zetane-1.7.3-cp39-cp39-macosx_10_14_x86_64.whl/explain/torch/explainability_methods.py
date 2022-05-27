

def vanilla_backprop(net, prep_img, out_class, class_name=None, out_dir=None, map_type='default', grad_times_image=True, smooth_grad=False, n=50, sigma=4):
    """
    Performs vanilla backpropagation, optionally applies SmoothGrad and Grad x Image, and saves the gradients as an image.

    Args:
        net (torch.nn.Module): the model used
        prep_img (torch.Tensor): input image to the network as tensor
        out_class (int): output class
        class_name (str): name of output class if any, otherwise defaults to str(out_class)
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        map_type (str): color map of the outputs, 'default' or 'grayscale' (default: 'default')
        grad_times_image (bool): whether to perform Grad x Image, which multiplies the two to generate B&W viz images. (default: True)
        smooth_grad (bool): whether to perform SmoothGrad (default: False)
        n (int): amount of images used to smooth gradient, only used if smooth_grad=True (default: 50)
        sigma (int): Sigma multiplier when calculating std of noise, only used if smooth_grad=True (default: 4)

    Returns:
        ndarray: backprop image as 3-channel ('default') or 1-channel ('grayscale'), HxWx3 (channels last) format with float values between 0-1
    """
    return None


def guided_backprop(net, prep_img, out_class, class_name, out_dir=None, map_type='default', smooth_grad=False, n=50, sigma=4):
    """
    Performs guided backpropagation, optionally applies SmoothGrad and Grad x Image, and saves the gradients as an image.

    Args:
        net (torch.nn.Module): the model used
        prep_img (torch.Tensor): input image to the network as tensor
        out_class (int): output class
        class_name (str): name of output class if any, otherwise defaults to str(out_class)
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        map_type (str): color map of the outputs, 'default' or 'grayscale' (default: 'default')
        smooth_grad (bool): whether to perform SmoothGrad (default: False)
        n (int): amount of images used to smooth gradient, only used if smooth_grad=True (default: 50)
        sigma (int): Sigma multiplier when calculating std of noise, only used if smooth_grad=True (default: 4)

    Returns:
        ndarray: backprop image as 3-channel ('default') or 1-channel ('grayscale'), HxWx3 (channels last) format with float values between 0-1
    """
    return None


def gradcam(net, out_class, class_name, prep_img, img_org=None, out_dir=None, layer_list=None, map_type='heatmap'):
    """
    Creates Grad-CAM images for a given class for the given list of convolutional layers.

    Args:
        net (torch.nn.Module): the model used
        out_class (int): output class
        class_name (str): name of output class if any, otherwise defaults to str(out_class)
        prep_img (torch.Tensor): input image to the network as tensor
        img_org (PIL.Image): the original image to overlay on, required for map_type='heatmap_on_image' (default: None)
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        layer_list (list(str)): the list of convolutional layers, None automatically infers all Conv layers. (default: None)
        map_type (str): type of map to be generated. One of 'heatmap', 'heatmap_on_image' or 'grayscale'. 'heatmap_on_image' is not advised for small images (default: 'heatmap')

    Returns:
        dict(str, ndarray): a dict of (layer name, Grad-CAM ndarray) pairs, with ndarrays in HxWx3 (channels last) format with float values between 0-1
    """
    return None


def guided_gradcam(net, out_class, class_name, prep_img, out_dir='ggc_test', layer_list=None, map_type='default'):
    """
    Creates Guided Grad-CAM images for a given class for the given list of convolutional layers.

    Args:
        net (torch.nn.Module): the model used
        out_class (int): output class
        class_name (str): name of output class if any, otherwise defaults to str(out_class)
        prep_img (torch.Tensor): input image to the network as tensor
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        layer_list (list(str)): the list of convolutional layers, None automatically infers all Conv layers. (default: None)
        map_type (str): type of map to be generated. One of 'heatmap', 'heatmap_on_image' or 'grayscale'. 'heatmap_on_image' is not advised for small images (default: 'heatmap')

    Returns:
        dict(str, ndarray): a dict of (layer name, Guided Grad-CAM ndarray) pairs, with ndarray in HxWx3 (channels last) format with float values between 0-1
    """
    return None


def scorecam(net, out_class, class_name, prep_img, img_org=None, out_dir=None, layer_list=None, map_type='heatmap'):
    """
    Creates Score-CAM images for a given class for the given list of convolutional layers.

    Args:
        net (torch.nn.Module): the model used
        out_class (int): output class
        class_name (str): name of output class if any, otherwise defaults to str(out_class)
        prep_img (torch.Tensor): input image to the network as tensor
        img_org (PIL.Image): the original image to overlay on, required for map_type='heatmap_on_image' (default: None)
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        layer_list (list(str)): the list of convolutional layers, None automatically infers all Conv layers. (default: None)
        map_type (str): type of map to be generated. One of 'heatmap', 'heatmap_on_image' or 'grayscale'. 'heatmap_on_image' is not advised for small images (default: 'heatmap')

    Returns:
        dict(str, ndarray): a dict of (layer name, Score-CAM ndarray) pairs, with ndarrays in HxWx3 (channels last) format with float values between 0-1
    """
    return None


def integrated_gradients(net, out_class, class_name, prep_img, out_dir=None, steps=100):
    """
    Generates Integrated Gradients visualizations from model gradients and saves them images.

    Args:
        net (torch.nn.Module): the model used
        out_class (int): output class
        class_name (str): name of output class if any, otherwise defaults to str(out_class)
        prep_img (torch.Tensor): input image to the network as tensor
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        steps (int): the number of steps IG should be applied (default: 100)

    Returns:
        ndarray: the integrated gradients as ndarray, HxWx3 (channels last) format with float values between 0-1
    """
    return None


def image_generation(net, target_class, image_size, out_dir=None, regularize=True):
    """
    Optimizes a given network to produce images resembling a given class.

    Args:
        net (torch.nn.Module): the model used
        target_class (int): the class for which the images will be generated
        image_size (tuple(int)): size of the input image
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)
        regularize (bool): whether to regularize the images. regularization improves the quality of generated images significantly (default: True)

    Returns:
        ndarray: the generated image as ndarray, HxWx3 (channels last) format with float values between 0-1
    """
    return None


def layer_visualization(net, cnn_layer, filter_pos, image_size, out_dir=None):
    """
    Visualizes the filters for a given convolutional layer. This is particularly useful to interpret the learned features associated with specific filters and layers.

    Args:
        net (torch.nn.Module): the model used
        cnn_layer (str): the layer to visualize
        filter_pos (int): the filter in the selected layer to be visualized
        image_size (tuple(int)): size of the input image
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)

    Returns:
        ndarray: the generated layer visualization as ndarray, HxWx3 (channels last) format with float values between 0-1
    """
    return None


def layer_activations(net, prep_img, out_class, cnn_layer, filter_pos, out_dir=None):
    """
    Visualizes activations for a specific input on a specific layer and filter. The method is quite similar to guided backpropagation but instead of guiding the signal from the last layer and a specific target, it guides the signal from a specific layer and filter.


    Args:
        net (torch.nn.Module): the model used
        prep_img (torch.Tensor): input image to the network as tensor
        out_class (int): output class
        cnn_layer (str): the layer to visualize
        filter_pos (int): the filter in the selected layer to be visualized
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)

    Returns:
        ndarray: the generated layer activation as ndarray, HxWx3 (channels last) format with float values between 0-1
    """
    return None


def deep_dream(net, cnn_layer, filter_pos, im_path, image_size, out_dir=None):
    """
    Performs Deep Dream on a given input image for selected filter and layer.

    Args:
        net (torch.nn.Module): the model used
        cnn_layer (str): the layer to visualize
        filter_pos (int): the filter in the selected layer to be visualized
        im_path (str): path to the image to be dreamt on
        image_size (tuple(int)): size of the input image
        out_dir (str): output directory. If set to None, does not save the output as an image (default: None)

    Returns:
        ndarray: the dreamed image as ndarray, HxWx3 (channels last) format with float values between 0-1

    """
    return None


def inverted_representation(net, prep_img, inv_mean, inv_std, out_dir=None, layer_list=None):
    return None


def lime_image(model, img, out_class, out_dir=None, min_weight=0):
    return None
