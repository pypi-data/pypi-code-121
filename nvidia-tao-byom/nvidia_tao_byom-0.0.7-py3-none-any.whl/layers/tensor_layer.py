# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for tensor related nodes."""

import keras
import numpy as np
# import logging


def convert_range(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Range layer.

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
    start = layers[node.input[0]]
    limit = layers[node.input[1]]
    delta = layers[node.input[2]]

    layers[node_name] = np.arange(start, limit, delta)


def convert_tile(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Tile layer.

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
    input_0 = layers[node.input[0]]
    input_1 = layers[node.input[1]]

    def target_layer(x, repeats=input_1):
        # Floor is absent in keras.backend
        import tensorflow as tf  # noqa pylint: disable=c0415, w0404
        return tf.tile(x, repeats)

    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_tile")
    layers[node_name] = lambda_layer(input_0)
    lambda_func[f"{keras_name}_tile"] = target_layer
