import keras.backend as K
from regex import E
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
import numpy as np

"""
This preprocessing code was given by the instructor.
"""


def get_layer_functor(model: MobileNetV2, layer_name: str) -> K.function:
    """Creates a function that will run the images through the model but only return the outputs of the specified layer

    Parameters
    ----------
    model : MobileNetV2
        The pretrained network
    layer_name : str
        The layer whose outputs we would like to retrieve representations from

    Returns
    -------
    K.function
        A keras function (a modified version of the model)
    """
    inp = model.input
    output = model.get_layer(layer_name).output
    return K.function([inp], [output])


def eval_layer(x, layer_functor):
    return layer_functor(x)[0]


def eval_layer_batched(
    model: MobileNetV2, layer_name: str, x: np.ndarray, batch_size: int
) -> np.ndarray:
    """Evaluate the layer with name layer_name for all images in x

    Parameters
    ----------
    model : _type_
        The pretrained network
    layer_name : str
        The layer to retrieve image representations from
    x : np.ndarray
        Input images
    batch_size : int
        Number of images to process at a time

    Returns
    -------
    np.ndarray
        The neural codes with rows corresponding to images and columns to each output unit of the specified layer.
    """
    layer_functor = get_layer_functor(model, layer_name)
    idx = 0
    ret_vals = None
    while idx < x.shape[0]:
        if idx + batch_size > x.shape[0]:
            batch_x = x[idx:, ...]
        else:
            batch_x = x[idx : (idx + batch_size), ...]

        # Normalize to [-1, 1]
        batch_x = np.float32(2.0 * (batch_x - np.min(batch_x)) / np.ptp(batch_x) - 1)
        assert np.max(batch_x) <= 1.0
        assert np.min(batch_x) >= -1.0
        batch_vals = eval_layer(batch_x, layer_functor)

        ret_vals = (
            batch_vals
            if ret_vals is None
            else np.concatenate((ret_vals, batch_vals), 0)
        )
        idx += batch_size
    return ret_vals


def get_image_representations(images: np.ndarray) -> np.ndarray:
    """Extract image representations

    Parameters
    ----------
    images : np.ndarray
       The images to be processed

    Returns
    -------
    np.ndarray
       Neural codes, or image representations

    """

    convnet = MobileNetV2(
        input_shape=(128, 128, 3), include_top=False, weights="imagenet"
    )
    image_representations = eval_layer_batched(convnet, "Conv_1", images, 200)
    return image_representations.reshape(len(images), 20480)
