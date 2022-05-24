# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for pooling related nodes."""

import keras
import logging
import numpy as np
from tao_byom.utils.convert_utils import ensure_tf_type


def convert_maxpool(node, params, layers, lambda_func, node_name, keras_name):
    """Convert MaxPooling layer.

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
    logger = logging.getLogger('tao_byom.maxpool')

    input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")

    kernel_shape = params['kernel_shape']
    stride_shape = params['strides']

    ceil_mode = params['ceil_mode'] if 'ceil_mode' in params else None  # Supported since Opset 10

    pads = params['pads'] if 'pads' in params else [0, 0, 0, 0, 0, 0]
    pad = 'valid'
    in_spatial_shape = input_0.get_shape().as_list()[2:]  # Remove N & C dims

    if 'dilations' in params and len(params['dilations'][params['dilations'] == 1]) != len(params['dilations']):
        raise NotImplementedError('Dilated Max Pooling not implemented')

    # noqa pylint: disable=R1729
    if all([shape % 2 == 1 for shape in kernel_shape]) and \
       all([kernel_shape[i] // 2 == pads[i] for i in range(len(kernel_shape))]) and \
       all([shape == 1 for shape in stride_shape]):
        pad = 'same'
        logger.debug('Use `same` padding parameters.')
    else:
        logger.debug('Unable to use `same` padding. Add ZeroPadding2D layer to fix shapes.')
        padding_name = keras_name + '_pad'
        if len(kernel_shape) == 2:
            padding = None

            if len(pads) == 2 and (pads[0] > 0 or pads[1] > 0):
                padding = (pads[0], pads[1])
            elif len(pads) == 4 and (pads[0] > 0 or pads[1] > 0 or pads[2] > 0 or pads[3] > 0):
                padding = ((pads[0], pads[2]), (pads[1], pads[3]))
            elif ceil_mode:
                logger.debug('Ceil_mode enabled. We might need to pad additionally')
                # Default output shape calculation for Keras Maxpool is math.floor
                # If ceil_mode is set to True, then we need to calculate the difference between math.ceil and math.floor
                # and pad additional dimensions to correctly convert Maxpool
                # Reference Code:
                # https://github.com/onnx/onnx-tensorflow/blob/master/onnx_tf/handlers/backend/dilated_pooling.py#L448
                padding = []
                for i in range(len(kernel_shape)):
                    dim_size = in_spatial_shape[i]
                    filter_size = (kernel_shape[i] - 1) + 1
                    out_size = (dim_size - filter_size) / stride_shape[i]
                    p = int(np.ceil(out_size) - np.floor(out_size)) * stride_shape[i]
                    padding.append([0, p])
                if np.sum(padding) == 0:  # No need for additional padding
                    padding = None
                else:
                    padding = tuple(padding)
                    logger.debug('Additional padding of size %s', padding)

            if padding is not None:
                padding_layer = keras.layers.ZeroPadding2D(
                    padding=padding,
                    name=padding_name
                )
                layers[padding_name] = input_0 = padding_layer(input_0)
        else:  # 3D padding
            padding_layer = keras.layers.ZeroPadding3D(
                padding=pads[:len(stride_shape)],
                name=padding_name
            )
            layers[padding_name] = input_0 = padding_layer(input_0)
    if len(kernel_shape) == 2:
        pooling = keras.layers.MaxPooling2D(
            pool_size=kernel_shape,
            strides=stride_shape,
            padding=pad,
            name=keras_name,
            data_format='channels_first'
        )
    else:
        pooling = keras.layers.MaxPooling3D(
            pool_size=kernel_shape,
            strides=stride_shape,
            padding=pad,
            name=keras_name,
            data_format='channels_first'
        )

    layers[node_name] = pooling(input_0)


def convert_avgpool(node, params, layers, lambda_func, node_name, keras_name):
    """Convert AvgPooling layer.

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
    logger = logging.getLogger('tao_byom.avgpool')

    input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")

    kernel_shape = params['kernel_shape']
    stride_shape = params['strides']

    pads = params['pads'] if 'pads' in params else [0, 0, 0, 0, 0, 0]
    pad = 'valid'

    # noqa pylint: disable=R1729
    if all([shape % 2 == 1 for shape in kernel_shape]) and \
       all([kernel_shape[i] // 2 == pads[i] for i in range(len(kernel_shape))]) and \
       all([shape == 1 for shape in stride_shape]):
        pad = 'same'
        logger.debug('Use `same` padding parameters.')
    else:
        logger.debug('Unable to use `same` padding. Add ZeroPadding2D layer to fix shapes.')
        padding_name = keras_name + '_pad'
        if len(kernel_shape) == 2:
            padding_layer = keras.layers.ZeroPadding2D(
                padding=pads[:len(stride_shape)],
                name=padding_name
            )
        else:  # 3D padding
            padding_layer = keras.layers.ZeroPadding3D(
                padding=pads[:len(stride_shape)],
                name=padding_name
            )
        layers[padding_name] = input_0 = padding_layer(input_0)
    if len(kernel_shape) == 2:
        pooling = keras.layers.AveragePooling2D(
            pool_size=kernel_shape,
            strides=stride_shape,
            padding=pad,
            name=keras_name,
            data_format='channels_first'
        )
    else:
        pooling = keras.layers.AveragePooling3D(
            pool_size=kernel_shape,
            strides=stride_shape,
            padding=pad,
            name=keras_name,
            data_format='channels_first'
        )
    layers[node_name] = pooling(input_0)


def convert_global_avg_pool(node, params, layers, lambda_func, node_name, keras_name):
    """Convert GlobalAvgPool layer.

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
    # logger = logging.getLogger('tao_byom.global_avg_pool')

    input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")

    global_pool = keras.layers.GlobalAveragePooling2D(data_format='channels_first', name=keras_name)
    input_0 = global_pool(input_0)
    new_shape = input_0.shape.as_list()
    new_shape = new_shape[1:]
    new_shape.extend([1, 1])
    reshape_layer = keras.layers.Reshape(new_shape)
    input_0 = reshape_layer(input_0)
    layers[node_name] = input_0
    # def target_layer(x):
    #     # from tensorflow import keras
    #     import keras
    #     return keras.backend.expand_dims(x)

    # logger.debug('Now expand dimensions twice.')
    # lambda_layer1 = keras.layers.Lambda(target_layer, name=keras_name + '_EXPAND1')
    # lambda_layer2 = keras.layers.Lambda(target_layer, name=keras_name + '_EXPAND2')
    # input_0 = lambda_layer1(input_0)  # double expand dims
    # layers[node_name] = lambda_layer2(input_0)
    # lambda_func[keras_name + '_EXPAND1'] = target_layer
    # lambda_func[keras_name + '_EXPAND2'] = target_layer
