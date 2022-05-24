# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for normalization related nodes."""

import keras
import numpy as np
import tensorflow as tf
import logging
from tao_byom.layers.custom_layers import InstanceNormalization
from tao_byom.utils.convert_utils import ensure_tf_type, ensure_numpy_type


def convert_batchnorm(node, params, layers, lambda_func, node_name, keras_name):
    """Convert BatchNorm2d layer.

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
    logger = logging.getLogger('tao_byom.batchnorm2d')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    if len(node.input) == 5:
        weights = [
            ensure_numpy_type(layers[node.input[1]]),
            ensure_numpy_type(layers[node.input[2]]),
            ensure_numpy_type(layers[node.input[3]]),
            ensure_numpy_type(layers[node.input[4]])
        ]
    elif len(node.input) == 3:
        weights = [
            ensure_numpy_type(layers[node.input[1]]),
            ensure_numpy_type(layers[node.input[2]])
        ]
    else:
        raise AttributeError('Unknown arguments for batch norm')

    eps = params['epsilon'] if 'epsilon' in params else 1e-05  # default epsilon
    momentum = params['momentum'] if 'momentum' in params else 0.9  # default momentum

    if len(weights) == 2:
        logger.debug('Batch normalization without running averages')
        bn = keras.layers.BatchNormalization(
            axis=1, momentum=momentum, epsilon=eps,
            center=False, scale=False,
            weights=weights,
            name=keras_name
        )
    else:
        bn = keras.layers.BatchNormalization(
            axis=1, momentum=momentum, epsilon=eps,
            weights=weights,
            name=keras_name
        )

    layers[node_name] = bn(input_0)


def convert_instancenorm(node, params, layers, lambda_func, node_name, keras_name):
    """Convert InstanceNorm2d layer.

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
    logger = logging.getLogger('tao_byom.instancenorm2d')

    logger.warning("Instance Norm is not tested thoroughly! Use with caution.")
    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    if len(node.input) == 3:
        gamma = ensure_numpy_type(layers[node.input[1]])
        beta = ensure_numpy_type(layers[node.input[2]])
    else:
        raise AttributeError('Unknown arguments for instance norm')

    epsilon = params['epsilon']

    instance_norm = InstanceNormalization(
        axis=1,
        epsilon=epsilon,
        beta_initializer=tf.constant_initializer(beta),
        gamma_initializer=tf.constant_initializer(gamma),
        trainable=False
    )
    layers[node_name] = instance_norm(input_0)


def convert_dropout(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Dropout layer.

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
    # In ONNX Dropout returns dropout mask as well.
    if isinstance(keras_name, list) and len(keras_name) > 1:
        keras_name = keras_name[0]

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    ratio = params['ratio'] if 'ratio' in params else 0.0
    lambda_layer = keras.layers.Dropout(ratio, name=keras_name)
    layers[node_name] = lambda_layer(input_0)


def convert_lrn(node, params, layers, lambda_func, node_name, keras_name):
    """Convert LRN layer.

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
    logger = logging.getLogger('tao_byom.LRN')
    logger.debug('LRN can\'t be tested with PyTorch exporter, so the support is experimental.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    alpha = params.get("alpha", 1e-4)
    beta = params.get("beta", 0.75)
    bias = params.get("bias", 1.0)
    size = params["size"]
    alpha = alpha / size
    depth_radius = np.floor([(size - 1) / 2.])[0]

    logger.warning("LRN depth radius %s", depth_radius)

    def target_layer(x, depth_radius=depth_radius, bias=bias, alpha=alpha, beta=beta):
        import tensorflow as tf  # noqa pylint: disable=C0415, W0404
        from keras import backend as K  # noqa pylint: disable=C0415
        data_format = 'NCHW' if K.image_data_format() == 'channels_first' else 'NHWC'

        if data_format == 'NCHW':
            x = tf.transpose(x, [0, 2, 3, 1])

        layer = tf.nn.local_response_normalization(
            x, depth_radius=depth_radius, bias=bias, alpha=alpha, beta=beta
        )

        if data_format == 'NCHW':
            layer = tf.transpose(x, [0, 3, 1, 2])

        return layer

    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_lrn")
    layers[node_name] = lambda_layer(input_0)
    lambda_func[f"{keras_name}_lrn"] = target_layer
