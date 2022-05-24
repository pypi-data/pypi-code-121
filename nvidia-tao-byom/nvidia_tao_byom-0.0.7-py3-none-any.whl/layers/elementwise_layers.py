# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Conversion functions for activation related nodes."""

import keras
import logging
from tao_byom.utils.convert_utils import is_numpy, ensure_tf_type
from tao_byom.layers.custom_layers import AddLayer, SubtractLayer, DivideLayer, MultiplyLayer, EqualLayer


def convert_elementwise_div(node, params, layers, lambda_func, node_name, keras_name):
    """Convert element-wise division.

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
    logger = logging.getLogger('tao_byom.div')

    if len(node.input) != 2:
        raise AttributeError('Number of inputs is not equal 2 for element-wise layer')

    if is_numpy(layers[node.input[0]]) and is_numpy(layers[node.input[1]]):
        logger.debug('Divide numpy arrays.')
        layers[node_name] = layers[node.input[0]] / layers[node.input[1]]
    else:
        logger.debug('Convert inputs to Keras/TF layers if needed.')
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")

        def target_layer(x1, x2=input_1):
            return x1 / x2

        try:
            layers[node_name] = keras.layers.Lambda(lambda x: x[0] / x[1], name=f"{keras_name}_div")([input_0, input_1])
            layers[node_name].set_shape(layers[node_name].shape)
            lambda_func[f"{keras_name}_div"] = target_layer
        except Exception as e2:
            logger.debug('%s Failed to use TF lambda. Use custom layer', e2)
            lambda_layer = DivideLayer(name=keras_name)
            layers[node_name] = lambda_layer([input_0, input_1])
            lambda_func[keras_name] = DivideLayer


def convert_elementwise_add(node, params, layers, lambda_func, node_name, keras_name):
    """Convert element-wise add.

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
    logger = logging.getLogger('tao_byom.add')

    if len(node.input) != 2:
        raise AttributeError('Number of inputs is not equal 2 for element-wise layer')
    if is_numpy(layers[node.input[0]]) and is_numpy(layers[node.input[1]]):
        logger.debug('Both inputs are numpy')
        layers[node_name] = layers[node.input[0]] + layers[node.input[1]]
    else:
        logger.debug('Convert inputs to Keras/TF layers if needed.')
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")
        input_0_shape = input_0.get_shape().as_list()
        input_1_shape = input_1.get_shape().as_list()

        try:
            # Keras Elementwise Layers require two operands to be same shape
            if len(input_0_shape) == len(input_1_shape) and input_0_shape == input_1_shape:
                add = keras.layers.Add(name=keras_name)
                layers[node_name] = add([input_0, input_1])
            else:
                raise ValueError('Operands are different.')
        except Exception as e:
            logger.debug('%s Failed to use keras.layers.Add. Fallback to TF lambda.', e)

            def target_layer(x1, x2=input_1):
                return x1 + x2
            try:
                layers[node_name] = keras.layers.Lambda(lambda x: x[0] + x[1], name=f"{keras_name}_add")([input_0, input_1])
                layers[node_name].set_shape(layers[node_name].shape)
                lambda_func[f"{keras_name}_add"] = target_layer
            except Exception as e2:
                logger.debug('%s Failed to use TF lambda. Use custom layer', e2)
                lambda_layer = AddLayer(name=keras_name)
                layers[node_name] = lambda_layer([input_0, input_1])
                lambda_func[keras_name] = AddLayer


def convert_elementwise_mul(node, params, layers, lambda_func, node_name, keras_name):
    """Convert element-wise mul.

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
    logger = logging.getLogger('tao_byom.mul')

    if len(node.input) != 2:
        raise AttributeError('Number of inputs is not equal 2 for element-wise layer')

    if is_numpy(layers[node.input[0]]) and is_numpy(layers[node.input[1]]):
        logger.debug('Both inputs are numpy')
        layers[node_name] = layers[node.input[0]] * layers[node.input[1]]
    else:
        logger.debug('Convert inputs to Keras/TF layers if needed.')
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")
        input_0_shape = input_0.get_shape().as_list()
        input_1_shape = input_1.get_shape().as_list()

        try:
            # Keras Elementwise Layers require two operands to be same shape
            if len(input_0_shape) == len(input_1_shape) and input_0_shape == input_1_shape:
                mul = keras.layers.Multiply(name=keras_name)
                layers[node_name] = mul([input_0, input_1])
            else:
                raise ValueError('Operands are different.')
        except Exception as e:
            logger.debug('%s Failed to use keras.layers.Multiply. Fallback to TF lambda.', e)

            # Keras does not support broadcast multiply
            # Using target_layer with two inputs somehow causes problem in the serialization step
            # Instead use lambda operations
            def target_layer(x1, x2=input_1):
                return x1 * x2

            try:
                layers[node_name] = keras.layers.Lambda(lambda x: x[0] * x[1], name=f"{keras_name}_mul")([input_0, input_1])
                layers[node_name].set_shape(layers[node_name].shape)
                lambda_func[f"{keras_name}_mul"] = target_layer
            except Exception as e2:
                logger.debug('%s Failed to use TF lambda. Use custom layer', e2)
                lambda_layer = MultiplyLayer(name=keras_name)
                layers[node_name] = lambda_layer([input_0, input_1])
                lambda_func[keras_name] = MultiplyLayer


def convert_elementwise_sub(node, params, layers, lambda_func, node_name, keras_name):
    """Convert element-wise sub.

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
    logger = logging.getLogger('tao_byom.sub')

    if len(node.input) != 2:
        raise AttributeError('Number of inputs is not equal 2 for element-wise layer')

    logger.debug('Convert inputs to Keras/TF layers if needed.')
    if is_numpy(layers[node.input[0]]) and is_numpy(layers[node.input[1]]):
        logger.debug('Both inputs are numpy')
        layers[node_name] = layers[node.input[0]] - layers[node.input[1]]
    else:
        input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
        input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")

        input_0_shape = input_0.get_shape().as_list()
        input_1_shape = input_1.get_shape().as_list()

        try:
            # Keras Elementwise Layers require two operands to be same shape
            if len(input_0_shape) == len(input_1_shape) and input_0_shape == input_1_shape:
                sub = keras.layers.Subtract(name=keras_name)
                layers[node_name] = sub([input_0, input_1])
            else:
                raise ValueError('Operands are different.')
        except Exception as e:
            logger.debug('%s Failed to use keras.layers.Subtract. Fallback to TF lambda.', e)

            # Doesn't work with constants
            # IndexError: tuple index out of range
            def target_layer(x1, x2=input_1):
                return x1 - x2
            try:
                layers[node_name] = keras.layers.Lambda(lambda x: x[0] - x[1], name=f"{keras_name}_sub")([input_0, input_1])
                layers[node_name].set_shape(layers[node_name].shape)
                lambda_func[f"{keras_name}_sub"] = target_layer
            except Exception as e2:
                logger.debug('%s Failed to use TF lambda. Use custom layer', e2)
                lambda_layer = SubtractLayer(name=keras_name)
                layers[node_name] = lambda_layer([input_0, input_1])
                lambda_func[keras_name] = SubtractLayer


def convert_elementwise_equal(node, params, layers, lambda_func, node_name, keras_name):
    """Convert element-wise equal.

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
    logger = logging.getLogger('tao_byom.equal')

    if len(node.input) != 2:
        raise AttributeError('Number of inputs is not equal 2 for element-wise layer')

    """
    if not layers[node.input[0]][0]: # input is shape and batch dimension is 0
        layers[node.input[0]][0] = 1 # Very hacky. TODO: Genralizable way of handling such scenario
        layers[node.input[0]] = np.int32(layers[node.input[0]])
    """

    logger.debug('Convert inputs to Keras/TF layers if needed.')
    input_0 = ensure_tf_type(layers[node.input[0]], layers[list(layers)[0]], name=f"{keras_name}_const1")
    input_1 = ensure_tf_type(layers[node.input[1]], layers[list(layers)[0]], name=f"{keras_name}_const2")

    lambda_layer = EqualLayer(name=keras_name)
    layers[node_name] = lambda_layer([input_0, input_1])
    lambda_func[keras_name] = EqualLayer


def convert_min(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Min layer.

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
    if len(node.input) < 2:
        assert AttributeError('Less than 2 inputs for min layer.')

    inputs = []
    for i, inp in enumerate(node.input):
        input_ = ensure_tf_type(layers[inp], layers[list(layers)[0]], name=f"{keras_name}_const{i + 1}")
        inputs.append(input_)
    layers[node_name] = keras.layers.Minimum(name=keras_name)(inputs)


def convert_max(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Max layer.

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
    if len(node.input) < 2:
        assert AttributeError('Less than 2 inputs for max layer.')

    inputs = []
    for i, inp in enumerate(node.input):
        input_ = ensure_tf_type(layers[inp], layers[list(layers)[0]], name=f"{keras_name}_const{i + 1}")
        inputs.append(input_)
    layers[node_name] = keras.layers.Maximum(name=keras_name)(inputs)


def convert_mean(node, params, layers, lambda_func, node_name, keras_name):
    """Convert Mean layer.

    TODO: Test if this supports multidirectional (i.e., Numpy-style) broadcasting as required

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
    if len(node.input) < 2:
        assert AttributeError('Less than 2 inputs for mean layer.')

    inputs = []
    for i, inp in enumerate(node.input):
        input_ = ensure_tf_type(layers[inp], layers[list(layers)[0]], name=f"{keras_name}_const{i + 1}")
        inputs.append(input_)
    layers[node_name] = keras.layers.Average(name=keras_name)(inputs)
