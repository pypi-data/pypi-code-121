# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for reshape related nodes."""

import keras
import numpy as np
import logging
from tao_byom.utils.convert_utils import is_numpy, ensure_tf_type, ensure_numpy_type
from tao_byom.layers.custom_layers import ExpandLayer, SliceLayer, ReshapeLayer, GatherLayer


def convert_transpose(node, params, layers, lambda_func, node_name, keras_name):
    """Convert transpose.

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
    logger = logging.getLogger('tao_byom.transpose')
    input_name = node.input[0]

    if params['perm'][0] != 0:
        # logger.warning('Can\'t permute batch dimension. Result may be wrong.')
        if is_numpy(layers[input_name]):
            logger.debug('Transposing numpy array.')
            layers[node_name] = np.transpose(layers[input_name], axes=params['perm'])
        else:
            raise NotImplementedError('Can\'t modify this type of data')
    else:
        permute = keras.layers.Permute(params['perm'][1:], name=keras_name)
        layers[node_name] = permute(layers[input_name])


def convert_shape(node, params, layers, lambda_func, node_name, keras_name):
    """Convert shape.

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
    logger = logging.getLogger('tao_byom.shape')
    if is_numpy(layers[node.input[0]]):
        input_0 = layers[node.input[0]]
        logger.debug('Input was numpy array')
        logger.debug('Actual shape:')
        logger.debug(input_0.shape)
        layers[node_name] = np.array(input_0.shape)
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")
        logger.debug('Input was tf tensor')
        logger.debug('Actual shape:')
        logger.debug(np.array(input_0.get_shape().as_list()))

        shapes = []
        for i in input_0.get_shape().as_list():
            if i is not None:
                shapes.append(i)
            else:
                shapes.append(None)

        layers[node_name] = np.array(shapes)


def convert_gather(node, params, layers, lambda_func, node_name, keras_name):
    """Convert gather.

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
    logger = logging.getLogger('tao_byom.gather')

    if is_numpy(layers[node.input[0]]) and is_numpy(layers[node.input[1]]):
        logger.debug('Gather from numpy array')

        if params['axis'] == 0:
            layers[node_name] = np.array(layers[node.input[0]][layers[node.input[1]]])
        elif params['axis'] == 1:
            layers[node_name] = np.array(layers[:, node.input[0]][layers[node.input[1]]])
        elif params['axis'] == 2:
            layers[node_name] = np.array(layers[:, :, node.input[0]][layers[node.input[1]]])
        elif params['axis'] == 3:
            layers[node_name] = np.array(layers[:, :, :, node.input[0]][layers[node.input[1]]])
        else:
            raise AttributeError('Can\'t gather by axis more than 3.')
    else:
        logger.debug("Gather from TF tensor. Using GatherLayer")
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = layers[node.input[1]]

        try:
            lambda_layer = GatherLayer(input_1, params['axis'])
            layers[node_name] = lambda_layer(input_0)
            lambda_func[f"{keras_name}"] = GatherLayer
        except AttributeError as e:
            logger.warning('%s Can\'t gather from tf tensor.', e)


def convert_concat(node, params, layers, lambda_func, node_name, keras_name):
    """Convert concat.

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
    logger = logging.getLogger('tao_byom.concat')

    layer_input = [layers[node.input[i]] for i in range(len(node.input))]

    if all([is_numpy(layers[node.input[i]]) for i in range(len(node.input))]):  # noqa pylint: disable=R1729
        logger.debug('Concat numpy arrays.')
        layers[node_name] = np.concatenate(layer_input, axis=params['axis'])
    else:
        logger.debug('Concat Keras layers.')
        if len(layer_input) > 1:
            try:
                for i in range(len(layer_input)):
                    if is_numpy(layer_input[i]):
                        layer_input[i] = ensure_tf_type(layer_input[i], name=f"{keras_name}_const{i + 1}")

                layers[node_name] = keras.layers.concatenate(inputs=layer_input,
                                                             axis=params['axis'],
                                                             name=keras_name)
            except Exception as e:
                logger.warning('!!! IMPORTANT INFORMATION !!!')
                logger.warning(e)
                logger.warning('Failed to use Keras concatenate. Will use TF fallback.')
                logger.warning('---')

                def target_layer(x, axis=params['axis']):
                    # import keras.backend as K
                    import tensorflow as tf  # noqa pylint: disable=c0415, w0404
                    x = tf.concat(x, axis=axis)
                    # x = K.concatenate(x, axis=axis)
                    return x

                lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_concat_CHW")
                layers[node_name] = lambda_layer(layer_input)
                lambda_func[f"{keras_name}_concat_CHW"] = target_layer
        else:
            layers[node_name] = layer_input[0]


def convert_reshape(node, params, layers, lambda_func, node_name, keras_name):
    """Convert reshape.

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
    logger = logging.getLogger('tao_byom.reshape')

    input_0 = layers[node.input[0]]
    input_1 = layers[node.input[1]]

    if is_numpy(input_1):
        logger.debug('The second argument is numpy array.')
        if is_numpy(input_0):
            logger.debug('The first argument is numpy array. Apply np.reshape.')
            layers[node_name] = np.reshape(input_0, np.int32(input_1))
        else:
            if params['change_ordering']:
                input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")

                # Fix critical issue with NHWC
                if input_1[0] is None and input_1[1] == -1:
                    logger.warning('!!! IMPORTANT INFORMATION !!!')
                    logger.warning('The target shape if [None, -1] that means flatten.')
                    logger.warning('But the target ordering is NHWC, so we cant simply perform flatten')
                    logger.warning('The layer will be converted as lambda with tf.transpose')
                    logger.warning('---')

                    def target_layer(x):
                        import tensorflow as tf  # noqa pylint: disable=c0415, w0404
                        x = tf.transpose(x, [0, 3, 1, 2])
                        return x

                    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_reshape_CHW")
                    layers[node_name] = lambda_layer(input_0)
                    lambda_func[f"{keras_name}_reshape_CHW"] = target_layer
                else:
                    layers[node_name] = input_0

                reshape = keras.layers.Reshape(np.int32(input_1[1:]), name=keras_name)
                layers[node_name] = reshape(layers[node_name])

            else:
                input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")
                logger.debug('The first argument is Keras/tf layer. Apply keras.Reshape.')
                logger.debug('Target shape :')
                logger.debug(input_1)
                # Currently, we explicitly assume first dim to be batch but not always the case
                if input_1[0] is None or input_1[0] == params['batch_size']:
                    logger.debug("Target shape contains batch dim so exlcude batch dim")
                    target_shape = np.array(input_1[1:], dtype=np.int32)
                    logger.debug("Given Target Shape:%s & Updated Target Shape: %s", input_1, target_shape)

                    # We do not want -1 in target shape
                    # This can cause issue if we want to do operations on top of the shape
                    if -1 in target_shape:
                        input_shape = np.array(input_0.get_shape().as_list())[1:]
                        unknown_dim_index = list(target_shape).index(-1)
                        found_dim = np.prod(input_shape) / (-1 * np.prod(target_shape))
                        target_shape[unknown_dim_index] = int(found_dim)
                        logger.debug("Because there was -1 in dim %s, converted target shape to %s", unknown_dim_index, target_shape)

                    # Note: keras.layer.flatten() fails unit testing
                    # Use Reshape instead of flatten
                    reshape = keras.layers.Reshape(target_shape, name=keras_name)
                    layers[node_name] = reshape(input_0)

                else:
                    logger.debug("Target shape does not contain batch dim. Fallback to tf reshape")
                    logger.debug("Reshape's input size %s Batch Size %s", input_1[0], params['batch_size'])
                    target_shape = np.int32(input_1)
                    logger.debug(target_shape)
                    logger.debug(input_1)

                    lambda_layer = ReshapeLayer(shape=input_1, name=keras_name)
                    layers[node_name] = lambda_layer(input_0)
                    lambda_func[keras_name] = ReshapeLayer
    else:
        raise AttributeError('Can\'t reshape dynamic size.')


def convert_unsqueeze(node, params, layers, lambda_func, node_name, keras_name):
    """Convert unsqueeze.

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
    logger = logging.getLogger('tao_byom.unsqueeze')

    # Opset 11+, the axes are not part of attributes anymore. It's in the input
    if 'axes' in params:
        axes = params['axes']
    else:
        axes = layers[node.input[1]]
        logger.debug("Loading axes info from inputs")

    if is_numpy(layers[node.input[0]]):
        logger.debug('Work with numpy types.')
        layers[node_name] = layers[node.input[0]]
        for axis in axes:
            layers[node_name] = np.expand_dims(layers[node_name], axis)
    else:
        if len(axes) != 1:
            raise AttributeError('Number of axes is not equal 1. Cannot unsqueeze')

        def target_layer(x, axis=axes[0]):
            import keras.backend as K  # noqa pylint: disable=c0415, w0404
            return K.expand_dims(x, axis)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_unsqueeze")
        layers[node_name] = lambda_layer(layers[node.input[0]])
        lambda_func[f"{keras_name}_unsqueeze"] = target_layer


def convert_flatten(node, params, layers, lambda_func, node_name, keras_name):
    """Convert flatten.

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
    logger = logging.getLogger('tao_byom.flatten')

    if len(node.input) != 1:
        raise AttributeError('Number of inputs is not equal 1 for flatten layer')

    logger.debug('Convert inputs to Keras/TF layers if needed.')
    input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")

    if params['change_ordering']:
        # Fix critical issue with flatten
        def target_layer(x):
            import tensorflow as tf  # noqa pylint: disable=c0415, w0404
            x = tf.transpose(x, [0, 3, 1, 2])
            return x

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_flatten_CHW")
        tensor_chw = lambda_layer(input_0)
        flatten = keras.layers.Flatten(name=keras_name)
        layers[node_name] = flatten(tensor_chw)
        lambda_func[f"{keras_name}_flatten_CHW"] = target_layer
    else:
        reshape = keras.layers.Reshape([-1], name=keras_name)
        layers[node_name] = reshape(input_0)


def convert_slice(node, params, layers, lambda_func, node_name, keras_name):
    """Convert slice.

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
    logger = logging.getLogger('tao_byom.slice')

    if is_numpy(layers[node.input[0]]):
        if params['change_ordering']:
            raise NotImplementedError("change_ordering for Slice is not implemented")
        logger.debug('Slice numpy constants')
        # Opset < 10
        if 'axes' in params:
            if len(params["axes"]) != 1:
                raise NotImplementedError("Multiple axes in Slice is not implemented")
            axes = params["axes"][0]
            ends = params["ends"][0]
            starts = params["starts"][0]
            steps = 1
        elif len(node.input) == 4:  # No steps
            starts = ensure_numpy_type(layers[node.input[1]])
            ends = ensure_numpy_type(layers[node.input[2]])
            axes = ensure_numpy_type(layers[node.input[3]])
            steps = 1
        else:
            # Opset 10+. Moved to inputs. Steps is introduced.
            starts = ensure_numpy_type(layers[node.input[1]])
            ends = ensure_numpy_type(layers[node.input[2]])
            axes = ensure_numpy_type(layers[node.input[3]])
            steps = ensure_numpy_type(layers[node.input[4]])

        if len(axes) != 1:
            raise NotImplementedError("Multiple axes in Slice is not implemented")

        starts, ends, axes = starts[0], ends[0], axes[0]

        if isinstance(steps, np.ndarray):
            steps = steps[0]

        if axes == 0:
            layers[node_name] = layers[node.input[0]][starts:ends:steps]
        elif axes == 1:
            layers[node_name] = layers[node.input[0]][:, starts:ends:steps]
        elif axes == 2:
            layers[node_name] = layers[node.input[0]][:, :, starts:ends:steps]
        elif axes == 3:
            layers[node_name] = layers[node.input[0]][:, :, :, starts:ends:steps]
        elif axes == 4:
            layers[node_name] = layers[node.input[0]][:, :, :, :, starts:ends:steps]
        else:
            raise AttributeError('Not implemented')
    else:
        logger.debug('Convert inputs to Keras/TF layers if needed.')
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const")
        layers[node_name] = input_0

        # Opset < 10
        if 'axes' in params:
            if len(params["axes"]) != 1:
                raise NotImplementedError("Multiple axes in Slice is not implemented")
            axes = params["axes"][0]
            ends = params["ends"][0]
            starts = params["starts"][0]
            steps = 1
        elif len(node.input) == 4:  # No steps
            starts = ensure_numpy_type(layers[node.input[1]])
            ends = ensure_numpy_type(layers[node.input[2]])
            axes = ensure_numpy_type(layers[node.input[3]])
            steps = 1
        else:
            # Opset 10+. Moved to inputs. Steps is introduced.
            starts = ensure_numpy_type(layers[node.input[1]])
            ends = ensure_numpy_type(layers[node.input[2]])
            axes = ensure_numpy_type(layers[node.input[3]])
            steps = ensure_numpy_type(layers[node.input[4]])

            for i in range(len(starts)):
                if axes[i] != i:
                    assert AttributeError('Cant slice permuted axes')

        logger.debug("Use custom SliceLayer")
        if isinstance(axes, (list, np.ndarray)):
            if params['change_ordering']:
                raise NotImplementedError("change_ordering for Slice is not implemented")

            # TODO: Support multiple axes through tf.strided_slice
            if len(axes) != 1:
                raise NotImplementedError("Multiple axes in Slice is not implemented")
            starts, ends, axes = np.int32(starts[0]), np.int32(ends[0]), np.int32(axes[0])

            if isinstance(steps, np.ndarray):
                steps = np.int32(steps[0])
            lambda_layer = SliceLayer(axes, starts, ends, steps, name=keras_name)
            layers[node_name] = lambda_layer(input_0)
            lambda_func[keras_name] = SliceLayer
        else:
            starts, ends, axes, steps = np.int32(starts), np.int32(ends), np.int32(axes), np.int32(steps)
            lambda_layer = SliceLayer(axes, starts, ends, steps, name=keras_name)
            layers[node_name] = lambda_layer(input_0)
            lambda_func[keras_name] = SliceLayer


def convert_squeeze(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Squeeze layer.

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
    logger = logging.getLogger('tao_byom.squeeze')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    # Opset 11+, the axes are not part of param anymore. It's in the input
    if 'axes' in params:
        axes = params['axes'][0]
    else:
        axes = layers[node.input[1]]
        logger.debug("Loading axes info from inputs")

    if isinstance(axes, int):
        axes = [axes]
    elif isinstance(axes, np.ndarray):
        axes = list(axes)
    else:
        assert AttributeError("axes is neither int or np.ndarray type")

    def target_layer(x, axis=axes):
        import tensorflow as tf  # noqa pylint: disable=c0415, w0404
        return tf.squeeze(x, axis)

    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_squeeze")
    layers[node_name] = lambda_layer(input_0)
    lambda_func[f"{keras_name}_squeeze"] = target_layer


def convert_expand(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Expand layer.

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
    logger = logging.getLogger('tao_byom.expand')
    if len(node.input) != 2:
        assert AttributeError('More than 2 input for expand layer.')

    if is_numpy(layers[node.input[0]]) and is_numpy(layers[node.input[1]]):
        logging.debug("Expand numpy array")
        input_0 = layers[node.input[0]]
        input_1 = layers[node.input[1]]
        if input_1[0] is None:
            input_1[0] = input_0.shape[0]  # If shape batch size is None
        layers[node_name] = input_0 * np.ones(input_1, dtype=input_0.dtype)

    else:
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")

        logger.debug("Using custom ExpandLayer")
        lambda_layer = ExpandLayer(shape=input_1, name=keras_name)
        layers[node_name] = lambda_layer(input_0)
        lambda_func[keras_name] = ExpandLayer
