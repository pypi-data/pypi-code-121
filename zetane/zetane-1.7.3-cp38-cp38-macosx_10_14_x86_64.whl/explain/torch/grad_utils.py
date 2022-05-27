

def get_positive_negative_saliency(gradient):
    """
    Generates positive and negative saliency maps based on the gradient

    Args:
        gradient (np.ndarray): Gradient of the operation to visualize

    Returns:
        np.ndarray: pos_saliency as the positive saliency values
        np.ndarray: neg_saliency as the negative saliency values
    """
    return None


def generate_smooth_grad(Backprop, prep_img, target_class, param_n, param_sigma_multiplier):
    """
    Generates smooth gradients of given Backprop type. You can use this with both vanilla and guided backprop

    Args:
        Backprop (class): Backprop type
        prep_img (torch Variable): preprocessed image
        target_class (int): target class of imagenet
        param_n (int): Amount of images used to smooth gradient
        param_sigma_multiplier (int): Sigma multiplier when calculating std of noise

    Returns:
        np.ndarray: output smooth_grad image as an ndarray, 3xHxW (channels first) format with float values between 0-1

    """
    return None


def guided_grad_cam(grad_cam_mask, guided_backprop_mask):
    """
    Guided grad cam is just pointwise multiplication of cam mask and guided backprop mask

    Args:
        grad_cam_mask (np_arr): Class activation map mask
        guided_backprop_mask (np_arr):Guided backprop mask

    Returns:
        np.ndarray: output guided Grad-CAM image as an ndarray
    """
    return None
