# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for constant related nodes."""

import tensorflow as tf
import keras
import numpy as np
import logging
from tao_byom.utils.convert_utils import is_numpy, ensure_numpy_type


def convert_constant(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Constant layer

    Args:
        node: current operation node
        params: operation attributes
        layers: available keras layers
        lambda_func: function for keras Lambda layer
        node_name: internal converter name
        keras_name: resulting layer name
    Returns:
        None
    """
    layers[node_name] = params['value']


def convert_constant_of_shape(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Constant Of Shape layer.

    Args:
        node: current operation node
        params: operation attributes
        layers: available keras layers
        lambda_func: function for keras Lambda layer
        node_name: internal converter name
        keras_name: resulting layer name

    Returns:
        None
    """
    logger = logging.getLogger('tao_byom.constantofshape')

    # the default value is 0, float32
    if "value" in params:
        value = params['value']
        if not isinstance(value, int):
            value = value.item()
    else:
        value = 0

    if is_numpy(layers[node.input[0]]):
        logger.debug('Using Numpy full')
        input_0 = ensure_numpy_type(layers[node.input[0]])

        layers[node_name] = np.full(input_0, value)
    else:
        logger.debug('Using tf.fill function')

        input_0 = layers[node.input[0]]

        def target_layer(x, value=value):
            if x.dtype not in [tf.int64, tf.int32]:
                x = tf.cast(x, tf.int64)
            return tf.fill(x, value)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_constantofshape")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_constantofshape"] = target_layer
