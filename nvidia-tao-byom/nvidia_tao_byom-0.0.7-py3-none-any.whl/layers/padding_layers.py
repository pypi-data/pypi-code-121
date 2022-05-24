# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for padding related nodes."""

import keras
import logging
from tao_byom.utils.convert_utils import ensure_tf_type


def convert_padding(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Constant layer.

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
    # It's binary by-default
    logger = logging.getLogger("tao_byom.padding")

    # https://github.com/gmalivenko/onnx2keras/issues/112
    try:
        params['mode'] = params['mode'].decode('ascii')
    except ValueError:
        params['mode'] = 'constant'

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    if 'pads' in params:
        pads = params['pads']
    else:  # opset 11+
        pads = layers[node.input[1]]

    if params['mode'] == 'constant':

        if 'value' in params and params['value'] != 0.0:
            raise AssertionError('Cannot convert non-zero padding')

        # Magic ordering
        if len(pads) == 8:
            padding_layer = keras.layers.ZeroPadding2D(
                padding=((pads[2], pads[6]), (pads[3], pads[7])),
                name=keras_name
            )
        else:
            logger.warning("Caution - no test yet")
            padding_layer = keras.layers.ZeroPadding3D(
                padding=((pads[2], pads[7]), (pads[3], pads[8]), (pads[4], pads[9])),
                name=keras_name
            )
        layers[node_name] = padding_layer(input_0)
    elif params['mode'] == 'reflect':

        def target_layer(x, pads=pads):
            import tensorflow as tf  # noqa pylint: disable=C0415
            if len(pads) == 8:
                layer = tf.pad(x, [[0, 0], [0, 0], [pads[2], pads[6]], [pads[3], pads[7]]], 'REFLECT')
            else:
                logger.warning("Caution - no test yet")
                layer = tf.pad(x, [[0, 0], [0, 0], [pads[2], pads[7]], [pads[3], pads[8]], [pads[4], pads[9]]], 'REFLECT')
            return layer

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_reflect_pad")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_reflect_pad"] = target_layer
    elif params['mode'] == 'edge':

        def target_layer(x, pads=pads):
            import tensorflow as tf  # noqa pylint: disable=C0415
            if len(pads) == 8:  # TODO not tested yet
                layer = tf.pad(x, [[0, 0], [0, 0], [pads[2], pads[6]], [pads[3], pads[7]]], 'SYMMETRIC')
            else:
                logger.warning("Caution - no test yet")
                layer = tf.pad(x, [[0, 0], [0, 0], [pads[2], pads[7]], [pads[3], pads[8]], [pads[4], pads[9]]], 'SYMMETRIC')
            return layer

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_edge_pad")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_edge_pad"] = target_layer

    else:
        raise AttributeError('Unknown padding')
