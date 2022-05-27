

def show_image(image, result_dir, grayscale=False, ax=None, title=''):
    """
        Display the numpy array as the image and save the image in the directory specified by the user

    Args:
        image: numpy array of the image
        result_dir: the resulting directory where the image will be saved
        grayscale: Boolean to specify the image as grayscale
        ax: axis of the figure used when displaying the image inside the editor
        title(str): title of the output, also  used to store the image with the same(title) name

    """
    return None


def load_image(file_path):
    """
        Load/Open the image provided in the file_path

    Args:
        file_path: path of the image

    """
    return None


def keras_vanilla_backprop(model, img, result_dir, out_class, loss=None):
    """
        Display the vanilla backprop of the image according to the model

    Args:
        model: neural network (model) for explainability
        img(numpy array): numpy array of the image
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_guided_backprop(model, img, result_dir, out_class, loss=None):
    """
        Display the guided backprop gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        img(numpy array): numpy array of the image
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_integrated_grad(model, img, result_dir, out_class, loss=None):
    """
        Display the integrated gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        img (ndarray): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_smoothgrad(model, img, result_dir, out_class, num_samples=5, noise=1.0, loss=None):
    """
        Display the integrated gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        img (ndarray): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        num_samples (int): Number of noisy samples to generate for each input image
        noise (float): Standard deviation for noise normal distribution
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_gradximage(model, img, result_dir, out_class, use_guided_grads=False, loss=None):
    """
        Display the integrated gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        x(numpy array): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        use_guided_grads (boolean): Whether to use guided grads or raw gradients
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_gradcam(model, img, result_dir, out_class, loss=None):
    """
        Display the integrated gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        x(numpy array): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_guided_gradcam(model, img, result_dir, out_class, loss=None):
    """
        Display the integrated gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        x(numpy array): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_occlusion_sensitivity(model, img, result_dir, out_class, patch_size=16, postprocess_fn=None):
    """
        Display the integrated gradients of the image according to the model

    Args:
        model: neural network (model) for explainability
        x(numpy array): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        out_class (int): output class
        patch_size (int): size of the square occlusion patches
        postprocess_fn (function): Custom postprocessing function to extract class probabilities from model outputs if needed. If set to None, this defaluts to indexing into the 1D outputs array, assuming softmaxed outputs (default: None)

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_visual_back_prop(model, x, result_dir, smoothing=False):
    """
        Display the visual back propagation of the image according to the model

    Args:
        model: neural network (model) for explainability
        x(numpy array): numpy array of the image with proper shape that matchs the model
        result_dir: the resulting directory where the image will be saved
        smoothing: whether to apply smoothing

    Returns:
        mask(numpy array) : returns the output as numpy array
    """
    return None


def keras_gradcam_gb(model, img_path, layer_name, result_dir, cls=-1, save=True):
    """

        Display the smooth visual back propagation of the image according to the model

    Args:
        model: neural network (model) for explainability
        img_path: path of the image to calculate gradcam, guided back prop and guided gradcam for a given model
        layer_name: name of the layer for which gradcam, guided back prop and guided gradcam is calculated
        result_dir: the resulting directory where the image will be saved
        cls:class number to localize (-1 for most probable class)
        save: saving the image in the result directory folder

    Returns:
        gradcam(numpy array) : returns the gradcam output as numpy array
        gb(numpy array) : returns the guided backprop output as numpy array
        guided_gradcam(numpy array) : returns the guided_gradcam output as numpy array


    """
    return None


def keras_lime(model, img_path, result_dir, visualize=False):
    """
        Display the smooth visual back propagation of the image according to the model

    Args:
        model: neural network (model) for explainability
        img_path: path of the image to calculate gradcam, guided back prop and guided gradcam for a given model
        result_dir: the resulting directory where the image will be saved
        visualize: to visualize the results using matplotlib

    Returns:
        temp(numpy array): numpy array of the image
        mask(numpy array) : returns the output as numpy array

    """
    return None
