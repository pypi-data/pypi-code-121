# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for operation related nodes."""

import keras
from keras import backend as K
import logging

from tao_byom.layers.custom_layers import WhereLayer
from tao_byom.utils.convert_utils import is_numpy, ensure_tf_type, ensure_numpy_type
import numpy as np

from collections.abc import Iterable


def convert_clip(node, params, layers, lambda_func, node_name, keras_name):
    """Convert clip layer.

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
    logger = logging.getLogger('tao_byom.clip')
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for clip layer.')

    # https://github.com/gmalivenko/onnx2keras/pull/123
    if 'min' not in params:
        node_input_data = [layers[attr] for attr in node.input[1:]]
        params["min"] = min(node_input_data)
    if 'max' not in params:
        node_input_data = [layers[attr] for attr in node.input[1:]]
        params["max"] = max(node_input_data)

    if is_numpy(layers[node.input[0]]):
        logger.debug("Clip from numpy array")
        layers[node_name] = np.clip(layers[node.input[0]], params['min'], params['max'])
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        if params['min'] == 0:
            logger.debug("Using ReLU(%s) instead of clip", params['max'])
            layer = keras.layers.ReLU(max_value=params['max'], name=keras_name)
        else:
            def target_layer(x, vmin=params['min'], vmax=params['max']):
                import tensorflow as tf # noqa pylint: disable=C0415
                return tf.clip_by_value(x, vmin, vmax)
            layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_clip")
            lambda_func[f"{keras_name}_clip"] = target_layer

        layers[node_name] = layer(input_0)


def convert_log(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Log layer.

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
    logger = logging.getLogger('tao_byom.log')

    if len(node.input) != 1:
        assert AttributeError('More than 1 input for log layer.')

    if is_numpy(layers[node.input[0]]):
        logger.debug("Log from numpy array")
        layers[node_name] = np.log(layers[node.input[0]])
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.log(x)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_log")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_log"] = target_layer


def convert_exp(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Exp layer.

    Args:
        node: current operation node
        params: operation attributes
        layers: available keras layers
        lambda_func: function for keras Lambda layer
        node_name: resulting layer name

    Returns:
        None
    """
    logger = logging.getLogger('tao_byom.exp')

    if len(node.input) != 1:
        assert AttributeError('More than 1 input for log layer.')

    if is_numpy(layers[node.input[0]]):
        logger.debug("Exp from numpy array")
        layers[node_name] = np.exp(layers[node.input[0]])
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.exp(x)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_exp")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_exp"] = target_layer


def convert_reduce_sum(node, params, layers, lambda_func, node_name, keras_name):
    """Convert reduce sum.

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
    logger = logging.getLogger('tao_byom.reduce_sum')

    # Opset 11+, the axes are not part of attributes anymore. It's in the input
    if 'axes' in params:
        axis = params['axes']
    else:
        axis = layers[node.input[1]]

    keepdims = params.get('keepdims', 1)

    if is_numpy(layers[node.input[0]]):
        input_0 = layers[node.input[0]]
        logger.debug('ReduceSum from numpy array')
        layers[node_name] = np.sum(input_0, axis=axis, keepdims=(keepdims == 1))
    else:
        input_0 = ensure_tf_type(layers[node.input[0]],  name=f"{keras_name}_const")

        # keras.backend.sum expects axis to be integer
        if isinstance(axis, np.ndarray):
            axis = axis[0]

        # Updated: keepdims was set to True by default. Need to be dynamically decided
        def target_layer(x, axis=axis, keepdims=keepdims):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.sum(x, keepdims=(keepdims == 1), axis=axis)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_reduce_sum")
        layers[node_name] = lambda_layer(input_0)
        layers[node_name].set_shape(layers[node_name].shape)
        lambda_func[f"{keras_name}_reduce_sum"] = target_layer


def convert_reduce_mean(node, params, layers, lambda_func, node_name, keras_name):
    """Convert reduce mean.

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
    logger = logging.getLogger('tao_byom.reduce_mean')

    if len(node.input) != 1:
        assert AttributeError('More than 1 input for reduce mean layer.')
    keepdims = params.get('keepdims', 1)
    axis = params.get("axes", -1)

    if is_numpy(layers[node.input[0]]):
        input_0 = layers[node.input[0]]
        logger.debug('ReduceMean from numpy array')
        layers[node_name] = np.mean(input_0, axis=axis, keepdims=(keepdims == 1))
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x, axis=axis, keepdims=keepdims):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.mean(x, keepdims=(keepdims == 1), axis=axis)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_reduce_mean")
        layers[node_name] = lambda_layer(input_0)
        layers[node_name].set_shape(layers[node_name].shape)
        lambda_func[f"{keras_name}_reduce_mean"] = target_layer


def convert_reduce_max(node, params, layers, lambda_func, node_name, keras_name):
    """Convert reduce max.

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
    logger = logging.getLogger('tao_byom.reduce_mean')

    if len(node.input) != 1:
        assert AttributeError('More than 1 input for reduce max layer.')

    keepdims = params.get('keepdims', 1)
    axis = params.get("axes", -1)

    if is_numpy(layers[node.input[0]]):
        input_0 = layers[node.input[0]]
        logger.debug('ReduceMax from numpy array')
        layers[node_name] = np.maximum.reduce(input_0, axis=axis, keepdims=(keepdims == 1))  # noqa pylint: disable=E1123
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x, axis=params['axes'], keepdims=keepdims):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.max(x, keepdims=(keepdims == 1), axis=axis)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_reduce_max")
        layers[node_name] = lambda_layer(input_0)
        layers[node_name].set_shape(layers[node_name].shape)
        lambda_func[f"{keras_name}_reduce_max"] = target_layer


def convert_pow(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Pow layer.

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
    logger = logging.getLogger('tao_byom.pow')

    if len(node.input) != 2:
        assert AttributeError('More than 2 inputs for pow layer.')

    power = ensure_numpy_type(layers[node.input[1]])

    if is_numpy(layers[node.input[0]]):
        input_0 = layers[node.input[0]]
        logger.debug('Pow from numpy array')
        layers[node_name] = np.power(input_0, power)
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x, a=power):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.pow(x, a)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_pow")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_pow"] = target_layer


def convert_sqrt(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Sqrt layer.

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
    logger = logging.getLogger('tao_byom.sqrt')

    if len(node.input) != 1:
        assert AttributeError('More than 1 input for sqrt layer.')

    if is_numpy(layers[node.input[0]]):
        input_0 = layers[node.input[0]]
        logger.debug('Sqrt from numpy array')
        layers[node_name] = np.sqrt(input_0)
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x):
            import keras.backend as K  # noqa pylint: disable=C0415, W0404
            return K.sqrt(x)

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_sqrt")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_sqrt"] = target_layer


def convert_split(node, params, layers, lambda_func, node_name, keras_names):
    """Convert Split layer.

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
        assert AttributeError('More than 1 input for split layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_names[0]}_const")
    if "split" in params:
        splits = params["split"]
    else:
        splits = np.uint8(layers[node.input[1]])

    axis = params.get("axis", 0)
    if not isinstance(splits, Iterable):
        # This might not work if `split` is a tensor.
        chunk_size = K.int_size(input_0)[axis] // splits
        splits = (chunk_size,) * splits

    cur = 0
    for i, split in enumerate(splits):
        node_name = params['_outputs'][i]

        def target_layer(x, axis=axis, start_i=cur, end_i=cur+split):  # noqa pylint: disable=W0640
            slices = [slice(None, None)] * len(K.int_shape(x))
            slices[axis] = slice(start_i, end_i)
            return x[tuple(slices)]

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_names[i]}_split")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_names[i]}_split"] = target_layer
        cur += split


def convert_cast(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Cast layer.

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
    logger = logging.getLogger('tao_byom.cast')

    if len(node.input) != 1:
        assert AttributeError('More than 1 input for cast layer.')

    if is_numpy(layers[node.input[0]]) or isinstance(layers[node.input[0]], (int, float)):
        logger.debug('Cast numpy array')

        cast_map = {
            1: np.float32,
            2: np.uint8,
            3: np.int8,
            5: np.int16,
            6: np.int32,
            7: np.int64,
            9: np.bool,
            10: np.float16,
            11: np.double,
        }

        layers[node_name] = cast_map[params['to']](layers[node.input[0]])
    else:
        logger.debug('Cast TF array')

        input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

        def target_layer(x, dtype=params['to']):
            import tensorflow as tf  # noqa pylint: disable=C0415
            cast_map = {1: tf.float32,
                        2: tf.uint8,
                        3: tf.int8,
                        5: tf.int16,
                        6: tf.int32,
                        7: tf.int64,
                        9: tf.bool,
                        10: tf.float16,
                        11: tf.double,
                        }
            return tf.cast(x, cast_map[dtype])

        lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_cast")
        layers[node_name] = lambda_layer(input_0)
        lambda_func[f"{keras_name}_cast"] = target_layer


def convert_floor(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Floor layer.

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
        assert AttributeError('More than 1 input for floor layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")

    def target_layer(x):
        # Floor is absent in keras.backend
        import tensorflow as tf  # noqa pylint: disable=C0415
        return tf.floor(x)

    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_floor")
    layers[node_name] = lambda_layer(input_0)
    lambda_func[f"{keras_name}_floor"] = target_layer


def convert_identity(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Identity layer.

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
        assert AttributeError('More than 1 input for itentity layer.')
    # Updated to lambda function so that it can be tested properly
    # Otherwise, we get tensorflow.python.framework.errors_impl.InvalidArgumentError: test_in:0 is both fed and fetched.
    # As the input layer and output are the same
    target_layer = keras.layers.Lambda(lambda x: x, name=f"{keras_name}_identity")
    layers[node_name] = target_layer(layers[node.input[0]])
    lambda_func[f"{keras_name}_identity"] = target_layer


def convert_argmax(node, params, layers, lambda_func, node_name, keras_name):
    """Convert ArgMax layer.

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
        assert AttributeError('More than 1 input for argmax layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")
    axis = params.get("axis", -1)

    def target_layer(x, axis=axis):
        import tensorflow as tf  # noqa pylint: disable=C0415
        return tf.argmax(x, axis=axis)

    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_argmax")
    layers[node_name] = lambda_layer(input_0)
    lambda_func[f"{keras_name}_argmax"] = target_layer


def convert_reduce_l2(node, params, layers, lambda_func, node_name, keras_name):
    """Convert ReduceL2 layer.

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
        assert AttributeError('More than 1 input for reduce_l2 layer.')

    input_0 = ensure_tf_type(layers[node.input[0]], name=f"{keras_name}_const")
    axis = params.get("axes", [-1])
    keepdims = params.get("keepdims", 0)

    def target_layer(x, axis=axis, keepdims=keepdims):
        import tensorflow as tf  # noqa pylint: disable=C0415
        return tf.norm(x, axis=axis, keepdims=keepdims == 1)

    lambda_layer = keras.layers.Lambda(target_layer, name=f"{keras_name}_reduce_l2")
    layers[node_name] = lambda_layer(input_0)
    lambda_func[f"{keras_name}_reduce_l2"] = target_layer


def convert_where(node, params, layers, lambda_func, node_name, keras_name):
    """Convert where layer.

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
    logger = logging.getLogger('tao_byom.where')
    input_0 = layers[node.input[0]]
    input_1 = layers[node.input[1]]
    input_2 = layers[node.input[2]]

    if is_numpy(layers[node.input[0]]):
        logger.debug("Numpy where")
        layers[node_name] = np.where(input_0, input_1, input_2)
    else:
        input_0 = ensure_tf_type(input_0, layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(input_1, layers[list(layers)[0]], name=f"{keras_name}_const2")
        input_2 = ensure_tf_type(input_2, layers[list(layers)[0]], name=f"{keras_name}_const3")

        lambda_layer = WhereLayer(name=keras_name)
        layers[node_name] = lambda_layer([input_0, input_1, input_2])
        lambda_func[keras_name] = WhereLayer
