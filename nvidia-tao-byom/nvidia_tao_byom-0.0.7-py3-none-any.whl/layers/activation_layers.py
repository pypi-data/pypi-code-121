# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for activation related nodes."""

import keras
import logging
from tao_byom.utils.convert_utils import ensure_tf_type, ensure_numpy_type, is_numpy


def convert_relu(node, params, layers, lambda_func, node_name, keras_name):
    """Convert ReLU activation layer.

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
    logger = logging.getLogger("tao_byom.relu")
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')
    if is_numpy(layers[node.input[0]]):
        logger.debug("Input is numpy")
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")
    else:
        logger.debug("Input is TF tensor")
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    relu = keras.layers.Activation('relu', name=keras_name)
    layers[node_name] = relu(input_0)


def convert_elu(node, params, layers, lambda_func, node_name, keras_name):
    """Convert ELU activation layer.

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    elu = keras.layers.ELU(alpha=params['alpha'], name=keras_name)
    layers[node_name] = elu(input_0)


def convert_lrelu(node, params, layers, lambda_func, node_name, keras_name):
    """Convert LeakyReLU activation layer.

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    leakyrelu = keras.layers.LeakyReLU(alpha=params['alpha'], name=keras_name)
    layers[node_name] = leakyrelu(input_0)


def convert_sigmoid(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Sigmoid activation layer

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    sigmoid = keras.layers.Activation('sigmoid', name=keras_name)
    layers[node_name] = sigmoid(input_0)


def convert_tanh(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Tanh activation layer.

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    tanh = keras.layers.Activation('tanh', name=keras_name)
    layers[node_name] = tanh(input_0)


def convert_selu(node, params, layers, lambda_func, node_name, keras_name):
    """Convert SELU activation layer.

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    selu = keras.layers.Activation('selu', name=keras_name)
    layers[node_name] = selu(input_0)


def convert_softplus(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Softplus activation layer.

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    selu = keras.layers.Activation('softplus', name=keras_name)
    layers[node_name] = selu(input_0)


def convert_softmax(node, params, layers, lambda_func, node_name, keras_name):
    """Convert softmax activation layer.

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
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for an activation layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")
    if params['opset'] < 11:
        axis = params.get("axis", -1)
    else:
        axis = params.get("axis", 1)

    softmax_layer = keras.layers.Softmax(axis=axis, name=keras_name)
    layers[node_name] = softmax_layer(input_0)
    layers[node_name].set_shape(layers[node_name].shape)


def convert_prelu(node, params, layers, lambda_func, node_name, keras_name):
    """Convert PReLU activation layer.

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
    logger = logging.getLogger('tao_byom.prelu')

    if len(node.input) != 2:
        assert AttributeError('Activation layer PReLU should have 2 inputs.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")
    W = ensure_numpy_type(layers[node.input[1]])

    if params['change_ordering']:
        logger.warning('PRelu + change ordering needs to be fixed after TF graph is built.')
        logger.warning('It\'s experimental.')

    shared_axes = [2, 3]

    # for case when W.shape (n,). When activation is used for single dimension vector.
    shared_axes = shared_axes if len(W.shape) > 1 else None

    prelu = keras.layers.PReLU(weights=[W], shared_axes=shared_axes, name=keras_name)
    layers[node_name] = prelu(input_0)
