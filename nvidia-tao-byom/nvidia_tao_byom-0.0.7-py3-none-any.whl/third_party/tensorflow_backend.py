# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.

"""Keras-specific Extensions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import keras
import tensorflow as tf


"""Logger for Keras tensorflow backend."""
logger = logging.getLogger(__name__)

DATA_FORMAT_MAP = {"channels_first": "NCHW", "channels_last": "NHWC"}


def batch_normalization(x, mean, var, beta, gamma, axis=-1, epsilon=1e-3):
    """Applies batch normalization on x given mean, var, beta and gamma.

    I.e. returns:
    `output = (x - mean) / sqrt(var + epsilon) * gamma + beta`

    # Arguments
        x: Input tensor or variable.
        mean: Mean of batch.
        var: Variance of batch.
        beta: Tensor with which to center the input.
        gamma: Tensor by which to scale the input.
        axis: Integer, the axis that should be normalized.
            (typically the features axis).
        epsilon: Fuzz factor.

    # Returns
        A tensor.
    """
    return tf.nn.batch_normalization(x, mean, var, beta, gamma, epsilon)


def softmax(x, axis=-1):
    """Softmax activation function.

    Patched to allow use of the backend's `softmax` regardless of the
    cardinality of the input dimensions.

    # Arguments
        x: Input tensor.
        axis: Integer, axis along which the softmax normalization is applied.
    # Returns
        Tensor, output of softmax transformation.
    # Raises
        ValueError: In case `dim(x) == 1`.
    """
    ndim = keras.backend.ndim(x)
    if ndim == 4 and axis == 1:
        # in the "channels_first" case tf.nn.softmax adds a channel swap
        # roundtrip to perform the softmax in "channels_last" order. The channel swap is done
        # through tensor shape manipulations, which TensorRT cannot handle (TensorRT needs
        # the permutation vector to be a constant). Below is a workaround for the NCHW softmax.
        # Transpose to "channels_last" order.
        x = tf.transpose(x, perm=[0, 2, 3, 1])
        # Do the softmax in "channels_last" order (do not necessitate transpose).
        x = tf.nn.softmax(x, axis=-1)
        # Tranpose back to "channels_first".
        x = tf.transpose(x, perm=[0, 3, 1, 2])
        return x
    if ndim >= 2:
        return tf.nn.softmax(x, axis=axis)
    raise ValueError(
        "Cannot apply softmax to a tensor that is 1D. " f"Received input: {x}"
    )


def flatten_call(self, inputs):
    """call method of Flatten layer."""
    # Overrides the suboptimal change added to keras that makes Flatten layers' channels_first
    # to be export incompatible (reverts https://github.com/keras-team/keras/pull/9696).
    return keras.backend.batch_flatten(inputs)


def _patch_backend_function(f):
    """Patch keras backend functionality.

    The patch is applied to both the general keras backend and the framework specific backend.

    Args:
        f (func): a function with the same name as exists in the keras backend.
    """
    name = f.__name__
    logger.debug("Patching %s", name)
    keras.backend.__setattr__(name, f)
    keras.backend.tensorflow_backend.__setattr__(name, f)


def patch():
    """Apply the patches to the module."""
    _patch_backend_function(batch_normalization)
    keras.layers.activations.__setattr__("softmax", softmax)
    keras.layers.Flatten.call = flatten_call
    keras.backend.set_image_data_format("channels_first")
