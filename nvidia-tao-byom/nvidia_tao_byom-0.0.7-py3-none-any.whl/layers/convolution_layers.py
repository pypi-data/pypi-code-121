# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for convolution related nodes."""

import keras
import logging

from tao_byom.utils.convert_utils import ensure_tf_type, ensure_numpy_type
from tao_byom.layers.custom_layers import GroupConv, ZeroPadding1D_NCW


def convert_conv(node, params, layers, lambda_func, node_name, keras_name, kernel_initializer="glorot_uniform"):
    """Convert convolution layer.

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
    logger = logging.getLogger('tao_byom.conv')

    if len(node.input) == 3:
        logger.debug('Conv with bias')
        # Has bias
        has_bias = True
        W = ensure_numpy_type(layers[node.input[1]])
        bias = ensure_numpy_type(layers[node.input[2]])

    elif len(node.input) == 2:
        logger.debug('Conv without bias')
        has_bias = False
        W = ensure_numpy_type(layers[node.input[1]])
        bias = None

    else:
        raise NotImplementedError('Not implemented')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")
    n_groups = params['group'] if 'group' in params else 1
    dilation = params['dilations'][0] if 'dilations' in params else 1
    pads = params['pads'] if 'pads' in params else [0, 0, 0]
    strides = params['strides'] if 'strides' in params else [1, 1, 1]
    auto_pad = params['auto_pad'] if 'auto_pad' in params else "NOTSET"
    auto_pad = params['auto_pad'] if 'auto_pad' in params else "NOTSET"

    if len(W.shape) == 5:  # 3D conv
        logger.debug('3D convolution')
        if pads[0] > 0 or pads[1] > 0 or pads[2] > 0:
            logger.debug('Paddings exist, add ZeroPadding layer')
            padding_name = keras_name + '_pad'
            padding_layer = keras.layers.ZeroPadding3D(
                padding=(pads[0], pads[1], pads[2]),
                name=padding_name
            )
            layers[padding_name] = input_0 = padding_layer(input_0)
        out_channels, channels_per_group, dimension, height, width = W.shape
        in_channels = channels_per_group * n_groups
        W = W.transpose(2, 3, 4, 1, 0)

        if has_bias:
            weights = [W, bias]
        else:
            weights = [W]
        if len(strides) == 1:  # could be single value
            strides = (strides[0], strides[0], strides[0])

        if n_groups == in_channels and n_groups != 1:
            logger.debug('Number of groups is equal to input channels, use DepthWise convolution')
            conv = keras.layers.DepthwiseConv3D(
                kernel_size=(height, width),
                strides=strides,
                padding='valid',
                use_bias=has_bias,
                activation=None,
                depth_multiplier=1,
                weights=weights,
                dilation_rate=dilation,
                bias_initializer='zeros',
                kernel_initializer=kernel_initializer,
                name=keras_name
            )
        else:
            # TODO: @scha remove this if we ever upgrade TF versions with group conv support
            conv = GroupConv(
                filters=out_channels,
                kernel_size=(dimension, height, width),
                strides=strides,
                padding='valid',
                weights=weights,
                use_bias=has_bias,
                activation=None,
                dilation_rate=dilation,
                bias_initializer='zeros',
                kernel_initializer=kernel_initializer,
                name=keras_name,
                groups=n_groups,
                rank=3
            )
            lambda_func[keras_name] = GroupConv
        layers[node_name] = conv(input_0)

    elif len(W.shape) == 4:  # 2D conv
        logger.debug('2D convolution')

        if auto_pad == "NOTSET":
            padding = None
            if len(pads) == 2 and (pads[0] > 0 or pads[1] > 0):
                padding = ((pads[0], pads[0]), (pads[1], pads[1]))
            elif len(pads) == 4 and (pads[0] > 0 or pads[1] > 0 or pads[2] > 0 or pads[3] > 0):
                padding = ((pads[0], pads[2]), (pads[1], pads[3]))

            W = W.transpose(2, 3, 1, 0)
            height, width, channels_per_group, out_channels = W.shape
            in_channels = channels_per_group * n_groups

            padding_mode = "valid"
            if padding:
                # Even though explicit padding values were provided,
                # we need verify if the padding type is SAME.
                # The calculation for padding value is adopted from
                # https://github.com/pytorch/pytorch/issues/3867#issuecomment-349279036
                out_height = (input_0.shape[2].value + strides[0] - 1) // strides[0]
                out_width = (input_0.shape[3].value + strides[1] - 1) // strides[1]
                filter_size_height = (height - 1) * dilation + 1
                filter_size_width = (width - 1) * dilation + 1

                height_padding = (out_height - 1) * strides[0] + filter_size_height - input_0.shape[2].value
                width_padding = (out_width - 1) * strides[1] + filter_size_width - input_0.shape[3].value

                if (sum(padding[0]) == height_padding) and (sum(padding[1]) == width_padding):
                    logger.debug("SAME padding applied to Conv directly instead of prepending ZeroPadding")
                    padding_mode = 'same'
                else:
                    logger.debug('Not SAME / VALID Padding, Add ZeroPadding layer')
                    padding_name = keras_name + '_pad'
                    padding_layer = keras.layers.ZeroPadding2D(
                        padding=padding,
                        name=padding_name,
                        data_format='channels_first'
                    )
                    layers[padding_name] = input_0 = padding_layer(input_0)
        elif auto_pad == "VALID":
            padding_mode = "valid"
        elif auto_pad == "SAME_UPPER":
            padding_mode = "same"
        else:
            raise NotImplementedError("auto_pad SAME_UPPER, VALID, NOTSET are only supported in keras")

        if n_groups == in_channels and n_groups != 1:
            logger.debug('Number of groups is equal to input channels, use DepthWise convolution')
            W = W.transpose(0, 1, 3, 2)
            if has_bias:
                weights = [W, bias]
            else:
                weights = [W]

            if len(strides) == 1:  # could be single value
                strides = (strides[0], strides[0])

            conv = keras.layers.DepthwiseConv2D(
                kernel_size=(height, width),
                strides=strides,
                padding=padding_mode,
                use_bias=has_bias,
                activation=None,
                depth_multiplier=1,
                weights=weights,
                dilation_rate=dilation,
                bias_initializer='zeros',
                kernel_initializer=kernel_initializer,
                name=keras_name
            )
            layers[node_name] = conv(input_0)

        elif n_groups != 1:
            logger.debug('Number of groups more than 1, but less than number of in_channel, use group convolution')
            if has_bias:
                weights = [W, bias]
            else:
                weights = [W]

            # TODO: @scha remove this if we ever upgrade TF versions with group conv support
            conv = GroupConv(
                filters=out_channels,
                kernel_size=(height, width),
                strides=(strides[0], strides[1]),
                padding=padding_mode,
                weights=weights,
                use_bias=has_bias,
                activation=None,
                dilation_rate=dilation,
                bias_initializer='zeros',
                kernel_initializer=kernel_initializer,
                name=keras_name,
                groups=n_groups,
                rank=2
            )

            layers[node_name] = conv(input_0)
            lambda_func[keras_name] = GroupConv

        else:
            if has_bias:
                weights = [W, bias]
            else:
                weights = [W]

            conv = keras.layers.Conv2D(
                filters=out_channels,
                kernel_size=(height, width),
                strides=(strides[0], strides[1]),
                padding=padding_mode,
                weights=weights,
                use_bias=has_bias,
                activation=None,
                dilation_rate=dilation,
                bias_initializer='zeros',
                kernel_initializer=kernel_initializer,
                name=keras_name,
            )

            layers[node_name] = conv(input_0)
    else:
        logger.debug('1D convolution')

        # 1D conv
        W = W.transpose(2, 1, 0)
        width, _, n_filters = W.shape

        if has_bias:
            weights = [W, bias]
        else:
            weights = [W]

        if pads[0] > 0:
            logger.debug('Paddings exist, add ZeroPadding layer')

            # ZeroPadding1D only supports NWC format
            padding_name = keras_name + '_pad'
            padding_layer = ZeroPadding1D_NCW(
                padding=(pads[0]),
                name=padding_name
            )
            layers[padding_name] = input_0 = padding_layer(input_0)

        # TODO: @scha remove this if we ever upgrade TF versions with group conv support
        conv = GroupConv(
            filters=n_filters,
            kernel_size=width,
            strides=strides,
            padding='valid',
            weights=weights,
            use_bias=has_bias,
            activation=None,
            dilation_rate=dilation,
            input_shape=input_0.get_shape().as_list()[1:],
            bias_initializer='zeros',
            kernel_initializer=kernel_initializer,
            name=keras_name,
            groups=n_groups,
            rank=1
        )
        layers[node_name] = conv(input_0)


def convert_convtranspose(node, params, layers,
                          lambda_func, node_name, keras_name, kernel_initializer='glorot_uniform'):
    """Convert transposed convolution layer

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
    logger = logging.getLogger('tao_byom.convtranpose')

    if len(node.input) == 3:
        logger.debug('ConvTranspose with bias')
        # Has bias
        has_bias = True
        W = ensure_numpy_type(layers[node.input[1]])
        bias = ensure_numpy_type(layers[node.input[2]])

    elif len(node.input) == 2:
        logger.debug('ConvTranspose without bias')
        has_bias = False
        W = ensure_numpy_type(layers[node.input[1]])
        bias = None

    else:
        raise NotImplementedError('Not implemented')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")
    n_groups = params['group'] if 'group' in params else 1
    dilation = params['dilations'][0] if 'dilations' in params else 1
    pads = params['pads'] if 'pads' in params else [0, 0]
    strides = params['strides'] if 'strides' in params else [1, 1]

    # 3D conv
    if len(W.shape) == 5:  # noqa pylint: disable=R1720
        raise NotImplementedError('Not implemented')
    elif len(W.shape) == 4:  # 2D conv
        W = W.transpose(2, 3, 1, 0)
        height, width, n_filters, _ = W.shape

        if has_bias:
            weights = [W, bias]
        else:
            weights = [W]

        if n_groups > 1:
            raise AttributeError('Cannot convert ConvTranspose2d with groups != 1')

        if dilation > 1:
            raise AttributeError('Cannot convert ConvTranspose2d with dilation_rate != 1')

        conv = keras.layers.Conv2DTranspose(
            filters=n_filters,
            kernel_size=(height, width),
            strides=strides,
            padding='valid',
            output_padding=0,
            weights=weights,
            use_bias=has_bias,
            activation=None,
            dilation_rate=dilation,
            bias_initializer='zeros',
            kernel_initializer=kernel_initializer,
            name=keras_name
        )

        if 'output_shape' in params and 'pads' not in params:
            logger.debug('!!!!! Paddings will be calculated automatically !!!!!')
            pads = [strides[0] * (int(input_0.shape[2]) - 1) + 0 + (height - 1) * dilation - params['output_shape'][0],
                    strides[1] * (int(input_0.shape[3]) - 1) + 0 + (height - 1) * dilation - params['output_shape'][1]]

        layers[node_name] = input_0 = conv(input_0)

        # Magic ad-hoc.
        # See the Keras issue: https://github.com/keras-team/keras/issues/6777
        # input_0.set_shape(input_0.shape)

        if 'output_padding' in params and (params['output_padding'][0] > 0 or params['output_padding'][1] > 0):
            raise AttributeError('Cannot convert ConvTranspose2d with output_padding != 0')

        if pads[0] > 0:
            logger.debug('Add cropping layer for output padding')
            assert(len(pads) == 2 or (pads[2] == pads[0] and pads[3] == pads[1]))

            crop = keras.layers.Cropping2D(
                pads[:2],
                name=keras_name + '_crop'
            )
            layers[node_name] = crop(input_0)
    else:
        raise AttributeError('Layer is not supported for now')
