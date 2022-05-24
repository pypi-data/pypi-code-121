# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for upsampling related nodes."""

import keras
import numpy as np
import logging
from tao_byom.layers.custom_layers import ImageResizeLayer


def convert_upsample(node, params, layers, lambda_func, node_name, keras_name):
    """Convert upsample.

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
    logger = logging.getLogger('tao_byom.upsample')
    mode = params['mode'].decode('utf-8')
    data_format = 'channels_last' if params['change_ordering'] else 'channels_first'

    if mode == "nearest" and len(node.input) < 4:  # We use default Upsampling from Keras if possible
        if "scales" in params:
            # for opset version - 7
            if len(node.input) != 1:
                raise AttributeError('Unsupported number of inputs')
            scale = np.uint8(params['scales'][-2:])
        elif len(node.input) == 2:
            # for opset version - 9+
            # Upsample since opset version 9 uses input[1] as 'scales' instead of attributes.
            scale = np.uint8(layers[node.input[1]][-2:])
            logger.debug("scale %s input 2", scale)
        elif len(node.input) == 3:  # 0: data 1: roi 2: scales
            scale = np.uint8(layers[node.input[2]][-2:])
            logger.debug("scale %s input 3", scale)

        upsampling = keras.layers.UpSampling2D(size=scale, name=keras_name, interpolation=mode)
        layers[node_name] = upsampling(layers[node.input[0]])

    else:  # Mode other than nearest
        if "scales" in params:
            # for opset version - 7
            if len(node.input) != 1:
                raise AttributeError('Unsupported number of inputs')
            scale = np.uint8(params['scales'][-2:])
        elif len(node.input) == 2:
            coordinate_transformation_mode = None  # Not introduced until Opset Version 11
            scale = np.uint8(layers[node.input[1]][-2:])
            logger.debug("Using custom Image Resize Layer with output scale of %s", scale)
            lambda_layer = ImageResizeLayer(output_scale=scale,
                                            data_format=data_format,
                                            mode=mode,
                                            coordinate_transformation_mode=coordinate_transformation_mode,
                                            name=keras_name)

        elif len(node.input) == 3:  # 0: data 1: roi 2: scales => Opset 11+
            coordinate_transformation_mode = params['coordinate_transformation_mode'].decode('utf-8')
            scale = np.uint8(layers[node.input[2]][-2:])
            logger.debug("Using custom Image Resize Layer with output scale of %s, mode %s, "
                         "and coordinate transformation mode of %s",
                         scale, mode, coordinate_transformation_mode)
            lambda_layer = ImageResizeLayer(output_scale=scale,
                                            data_format=data_format,
                                            mode=mode,
                                            coordinate_transformation_mode=coordinate_transformation_mode,
                                            name=keras_name)

        else:  # empty scale. use size instead => 0: data 1: roi 2: scales 3: sizes
            coordinate_transformation_mode = params['coordinate_transformation_mode'].decode('utf-8')

            # Here, we don't cast to uint8 as output size can be larger than 255
            output_size = np.int32(layers[node.input[3]][-2:])
            logger.debug("Using custom Image Resize Layer with output dim of %s, mode %s, "
                         "and coordinate transformation mode of %s",
                         output_size, mode, coordinate_transformation_mode)

            lambda_layer = ImageResizeLayer(output_dim=output_size,
                                            data_format=data_format,
                                            mode=mode,
                                            coordinate_transformation_mode=coordinate_transformation_mode,
                                            name=keras_name)

        layers[node_name] = lambda_layer(layers[node.input[0]])
        lambda_func[keras_name] = ImageResizeLayer
