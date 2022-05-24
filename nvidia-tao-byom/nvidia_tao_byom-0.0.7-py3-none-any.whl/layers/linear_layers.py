# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for linear related nodes."""

import keras
import logging
from tao_byom.utils.convert_utils import is_numpy, ensure_tf_type


def convert_gemm(node, params, layers, lambda_func, node_name, keras_name, kernel_initializer="glorot_uniform"):
    """Convert Linear / GEMM layer.

    Args:
        node: current operation node
        params: operation attributes
        layers: available keras layers
        lambda_func: function for keras Lambda layer
        node_name: internal converter name
        keras_name: resulting layer name
        kernel_initializer: type of layer initialization

    Returns:
        None
    """
    logger = logging.getLogger('tao_byom.gemm')

    # Check if Bias available
    if len(node.input) == 3:
        has_bias = True
        keras_weights = [layers[node.input[1]], layers[node.input[2]]]
        logger.debug('Convert GEMM with bias.')
    elif len(node.input) == 2:
        has_bias = False
        keras_weights = [layers[node.input[1]]]
        logger.debug('Convert GEMM without bias.')
    else:
        raise AttributeError('More than 3 or less than 2 inputs')

    # Linear can have additional flag to transpose weights
    if 'transB' in params and params['transB'] == 1:
        logger.debug('Transposing W matrix.')
        keras_weights[0] = keras_weights[0].transpose()

    # Estimate input/output neurons
    input_channels, output_channels = keras_weights[0].shape
    logger.debug('Input units %s, output units %s.', input_channels, output_channels)

    if is_numpy(keras_weights[0]):
        logger.debug("Weight is a Numpy so using Keras Dense Layer")
        dense = keras.layers.Dense(
            output_channels,
            weights=keras_weights,
            name=keras_name,
            bias_initializer='zeros',
            kernel_initializer=kernel_initializer,
            use_bias=has_bias
        )

        # The first input - always X
        try:
            layers[node_name] = dense(layers[node.input[0]])
        except ValueError:
            reshape = keras.layers.Reshape([input_channels], name=keras_name + '_reshape')
            reshaped_x = reshape(layers[node.input[0]])
            layers[node_name] = dense(reshaped_x)
    else:
        logger.debug("Weight is a not Numpy so using matrix multiply")
        layers[node_name] = keras.layers.Multiply()([layers[node.input[0]], layers[node.input[1]]])


def convert_matmul(node, params, layers, lambda_func, node_name, keras_name, kernel_initializer="glorot_uniform"):
    """Convert Matmul layer.

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
    logger = logging.getLogger('tao_byom.matmul')

    # MatMul is similar to GEMM except that there is no bias to add.

    if len(node.input) != 2:
        raise AttributeError('Number of inputs is not equal 2 for element-wise layer')

    keras_weights = [layers[node.input[1]]]
    # Estimate input/output neurons
    input_channels, output_channels = keras_weights[0].shape
    logger.debug('Input units %s, output units %s.', input_channels, output_channels)

    if is_numpy(keras_weights[0]):
        logger.debug("Weight is a Numpy so using Keras Dense Layer")
        input_0 = layers[node.input[0]]

        dense = keras.layers.Dense(
            output_channels,
            kernel_initializer=kernel_initializer,
            weights=keras_weights,
            use_bias=False,
            name=keras_name
        )

        try:
            layers[node_name] = dense(layers[node.input[0]])
        except ValueError as e:
            logger.debug('%s Reshape before Dense', e)
            reshape = keras.layers.Reshape([input_channels], name=keras_name + '_reshape')
            reshaped_x = reshape(layers[node.input[0]])
            layers[node_name] = dense(reshaped_x)
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")

        input_0_shape = input_0.get_shape().as_list()
        input_1_shape = input_1.get_shape().as_list()

        if len(input_0_shape) == len(input_1_shape) and input_0_shape == input_1_shape:
            logger.debug('Inputs are TF Tensors. Use Keras Dot.')

            dot = keras.layers.Dot(name=keras_name, axes=(len(input_0_shape) - 2, len(input_1_shape) - 1))
            layers[node_name] = dot([input_0, input_1])
        else:
            def target_layer(x1, x2=input_1):
                return x1 @ x2
            logger.debug('MatMul with braodcast. Fallback to TF lambda.')
            layers[node_name] = keras.layers.Lambda(lambda x: x[0] @ x[1],
                                                    name=f"{keras_name}_matmul")([input_0, input_1])
            layers[node_name].set_shape(layers[node_name].shape)
            lambda_func[f"{keras_name}_matmul"] = target_layer
