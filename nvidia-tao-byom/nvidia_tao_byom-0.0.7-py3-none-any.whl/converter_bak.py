# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""The ONNX to keras converter module."""

import keras
import logging
import inspect
import sys
import onnx
from onnx import numpy_helper
import numpy as np
from tao_byom.utils.model_utils import load_model_from_config
from tao_byom.utils.convert_utils import disable_tf32
from tao_byom.layers.layers import AVAILABLE_CONVERTERS
import tao_byom.third_party.tensorflow_backend as TFB
import tao_byom.third_party.nn_ops as NOP


def onnx_node_attributes_to_dict(args):
    """Parse ONNX attributes to Python dictionary.

    Args:
        args: ONNX attributes object

    Returns:
        Python dictionary
    """
    def onnx_attribute_to_dict(onnx_attr):
        """Parse ONNX attribute.

        Args:
            onnx_attr: ONNX attribute

        Returns:
            Python data type
        """
        if onnx_attr.HasField('t'):
            return numpy_helper.to_array(getattr(onnx_attr, 't'))

        for attr_type in ['f', 'i', 's']:
            if onnx_attr.HasField(attr_type):
                return getattr(onnx_attr, attr_type)

        for attr_type in ['floats', 'ints', 'strings']:
            if getattr(onnx_attr, attr_type):
                return list(getattr(onnx_attr, attr_type))
        return None
    return {arg.name: onnx_attribute_to_dict(arg) for arg in args}


def replace_names(name):
    """Replace name that contains special characters.

    Args:
        name: String
    
    Returns:
        name: Updated name
    """
    logger = logging.getLogger('tao_byom')
    if name.find(":") != -1:
        old_name = name
        name = name.replace(":", ".")
        logger.debug("Replaced name %s to %s", old_name, name)
    if name.find("/") != -1:
        old_name = name
        name = name.replace("/", ".")
        logger.debug("Replaced name %s to %s", old_name, name)

    return name


def tao_byom_converter(onnx_model, input_names,
                       available_converters=AVAILABLE_CONVERTERS,
                       input_shapes=None, name_policy=None,
                       kernel_initializer='glorot_uniform', opset=11,
                       change_ordering=False, verbose=True):
    """Convert ONNX graph to Keras model format.

    Args:
        onnx_model: loaded ONNX model
        input_names: list with input names
        available_converters: dict of available conversion function. Default: AVAILABLE_CONVERTERS
        input_shapes: override input shapes (experimental)
        name_policy: override layer names. None, "short" or "renumerate" (experimental)
        kernel_initializer: type of layer initialization
        opset: opset_version of the onnx model
        change_ordering: change ordering to HWC (experimental)
        verbose: verbose output

    Returns:
        model: converted Keras model
        node_keras_mappings: dict mapping onnx nodes and keras layers
        lambda_funcs: dict of Keras lamba functions used
    """
    # Throw an error msg if system python version is not 3.6.*
    if sys.version_info.major != 3 or sys.version_info.minor != 6:
        raise RuntimeError('Please use Python version 3.6 TAO BYOM. This is required for loading BYOM model in the TAO container.')

    # Patch bug in keras==2.2.4
    TFB.patch()
    # Patch to enable Group Conv in TF 1.15.x
    NOP.patch()

    # Use channels first format by default.
    keras_fmt = keras.backend.image_data_format()
    keras.backend.set_image_data_format('channels_first')

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger('tao_byom')

    logger.info('Converter is called.')

    # Disable TF32 for Ampere machines
    disable_tf32()

    # Check Validity of onnx model
    try:
        onnx.checker.check_model(onnx_model)
    except onnx.checker.ValidationError as e:
        logger.error('The ONNX model file is invalid: %s', e)

    onnx_weights = onnx_model.graph.initializer
    onnx_inputs = onnx_model.graph.input
    onnx_outputs = [i.name for i in onnx_model.graph.output]
    onnx_nodes = onnx_model.graph.node

    logger.debug('List input shapes:')
    logger.debug(input_shapes)

    logger.debug('List inputs:')
    for i, inputs in enumerate(onnx_inputs):
        logger.debug('Input %s -> %s.', i, inputs.name)

    logger.debug('List outputs:')
    for i, output in enumerate(onnx_outputs):
        logger.debug('Output %s -> %s.', i, output)

    logger.debug('Gathering weights to dictionary.')
    weights = {}
    for onnx_w in onnx_weights:
        # Fix according to https://github.com/gmalivenko/onnx2keras/pull/76
        # Models that were exported using keras2onnx has this naming issue
        onnx_extracted_weights_name = onnx_w.name

        # Can cause error if the name contains these characters
        onnx_extracted_weights_name = replace_names(onnx_extracted_weights_name)

        weights[onnx_extracted_weights_name] = numpy_helper.to_array(onnx_w)

        logger.debug('Found weight %s with shape %s.',
                     onnx_extracted_weights_name,
                     weights[onnx_extracted_weights_name].shape)

    layers, lambda_funcs = {}, {}
    keras_outputs, keras_inputs = [], []

    unsupported_ops = set()
    for node in onnx_nodes:
        if node.op_type not in available_converters:
            unsupported_ops.add(node.op_type)

    if len(unsupported_ops):
        logger.error("These operators are not supported in our converter %s", list(unsupported_ops))
        logger.error("Supported Operators: %s", list(available_converters.keys()))
        logger.error("For more information about ONNX Operators, visit https://github.com/onnx/onnx/blob/master/docs/Operators.md")
        logger.error("Exiting conversion")
        sys.exit(1)

    if change_ordering:
        logger.error("Currently only NCHW format is supported.")
        raise NotImplementedError

    batch_sizes = []
    for i, input_name in enumerate(input_names):
        for onnx_i in onnx_inputs:
            if onnx_i.name == input_name:
                if input_shapes:
                    input_shape = input_shapes[i]
                    batch_sizes.append(input_shape[0])
                else:
                    input_shape = [i.dim_value for i in onnx_i.type.tensor_type.shape.dim][1:]
                    batch_sizes.append([i.dim_value for i in onnx_i.type.tensor_type.shape.dim][0])

                # Assume input is 4D tensor (N, H, C, W)
                if len(input_shape) == 4 and input_shape[1] > input_shape[-1]:
                    raise NotImplementedError(f"TAO BYOM currently supports channel_first only. Provided ONNX Input Shape: {input_shape}")

                input_name = replace_names(input_name)

                layers[input_name] = keras.layers.InputLayer(
                    input_shape=input_shape, name=input_name
                ).output

                keras_inputs.append(layers[input_name])

                logger.debug('Found input %s with shape %s', input_name, input_shape)

    # Error handling for input shape
    if min(batch_sizes) != max(batch_sizes):
        logger.error("Batch size for all inputs must be identical!. Found %s", batch_sizes)
        raise ValueError

    batch_size = min(batch_sizes)

    # Convert every operation separable
    node_names = []
    node_keras_mappings = {}
    for node_index, node in enumerate(onnx_nodes):
        node_type = node.op_type
        node_params = onnx_node_attributes_to_dict(node.attribute)

        # Add global converter info:
        node_params['change_ordering'] = change_ordering
        node_params['name_policy'] = name_policy
        node_params['batch_size'] = batch_size
        node_params['opset'] = opset

        node_name = str(node.output[0])
        keras_names = []
        for output_index, output in enumerate(node.output):
            output = replace_names(str(output))

            if name_policy == 'short':
                keras_name = keras_name_i = str(output)[:8]
                suffix = 1
                while keras_name_i in node_names:
                    keras_name_i = keras_name + '_' + str(suffix)
                    suffix += 1
                keras_names.append(keras_name_i)
            elif name_policy == 'renumerate':
                postfix = node_index if len(node.output) == 1 else f"{node_index}_{output_index}"
                keras_names.append(f'LAYER_{postfix}')
            else:
                keras_names.append(output)

        if len(node.output) != 1:
            logger.warning('Trying to convert multi-output node')
            node_params['_outputs'] = list(node.output)
            node_names.extend(keras_names)
        else:
            keras_names = keras_names[0]
            node_names.append(keras_names)

        logger.debug('######')
        logger.debug('...')
        logger.debug('Converting ONNX operation')
        logger.debug('type: %s', node_type)
        logger.debug('node_name: %s', node_name)
        logger.debug('node_params: %s', node_params)
        logger.debug('...')

        node_keras_mappings[node_name] = keras_names
        logger.debug('Check if all inputs are available:')
        if len(node.input) == 0 and node_type != 'Constant':
            raise AttributeError('Operation doesn\'t have an input. Aborting.')

        for i, node_input in enumerate(node.input):
            node.input[i] = replace_names(node_input)

        # Update layer dict with updated layer names
        new_layers = {}
        for layer_name, _ in layers.items():
            if layer_name.find(":") != -1:
                layer_name_new = layer_name.replace(":", ".")
                new_layers[layer_name_new] = layers[layer_name]
                logger.debug("Modified layer name from %s to %s", layer_name, layer_name_new)
                layer_name = layer_name_new
                continue
            if layer_name.find("/") != -1:
                layer_name_new = layer_name.replace("/", ".")
                new_layers[layer_name_new] = layers[layer_name]
                logger.debug("Modified layer name from %s to %s", layer_name, layer_name_new)
                layer_name = layer_name_new
                continue
            new_layers[layer_name] = layers[layer_name]
        layers = new_layers

        for i, node_input in enumerate(node.input):
            node.input[i] = replace_names(node_input)
            logger.debug('Check input %i (name %s).', i, node_input)
            if node_input not in layers:
                logger.debug('The input not found in layers / model inputs.')

                if node_input in weights:
                    logger.debug('Found in weights, add as a numpy constant.')
                    layers[node_input] = weights[node_input]
                else:
                    raise AttributeError(f'Current node is not in weights / model inputs / layers. {node_input}')

        keras.backend.set_image_data_format('channels_first')

        # Node that requires kernel initialization
        if node_type in ['Conv', 'ConvTranspose', 'Gemm']:
            available_converters[node_type](
                node,
                node_params,
                layers,
                lambda_funcs,
                node_name,
                keras_names,
                kernel_initializer=kernel_initializer
            )
        else:
            available_converters[node_type](
                node,
                node_params,
                layers,
                lambda_funcs,
                node_name,
                keras_names,
            )

        if isinstance(keras_names, list):
            keras_names = keras_names[0]

        try:
            logger.debug('Output TF Layer -> ' + str(layers[node_name]))
        except KeyError:
            logger.debug('Node %s w/ keras name %s does not exist', node_name, keras_names)
            pass

    # Check for terminal nodes
    for layer in onnx_outputs:
        if layer in layers:
            keras_outputs.append(layers[layer])

    # Create model
    model = keras.models.Model(inputs=keras_inputs, outputs=keras_outputs)

    if change_ordering:
        change_ord_axes_map = {
            3: 2,
            1: 3,
            -1: 1
        }

        conf = model.get_config()

        for layer in conf['layers']:
            if layer['config'] and 'shared_axes' in layer['config']:
                # TODO: check axes first (if it's not 4D tensor)
                layer['config']['shared_axes'] = [1, 2]

            if layer['config'] and 'batch_input_shape' in layer['config']:
                layer['config']['batch_input_shape'] = \
                    tuple(np.reshape(np.array(
                        [
                            [None] +
                            list(layer['config']['batch_input_shape'][2:][:]) +
                            [layer['config']['batch_input_shape'][1]]
                        ]), -1
                    ))
            if layer['config'] and 'target_shape' in layer['config']:
                if len(list(layer['config']['target_shape'][1:][:])) > 0:
                    layer['config']['target_shape'] = \
                        tuple(np.reshape(np.array(
                              list(layer['config']['target_shape'][1:]) +
                              [layer['config']['target_shape'][0]]
                              ), -1),)

            if layer['config'] and 'data_format' in layer['config']:
                layer['config']['data_format'] = 'channels_last'
            if layer['config'] and 'axis' in layer['config']:
                axis = layer['config']['axis']
                # BatchNorm wrap axis with ListWrapper instead single INT value
                if isinstance(axis, (tuple, list)):
                    axis = axis[0]
                layer['config']['axis'] = change_ord_axes_map.get(axis, layer['config']['axis'])

        for layer in conf['layers']:
            if 'function' in layer['config'] and layer['config']['function'][1] is not None:
                kerasf = list(layer['config']['function'])
                dargs = list(kerasf[1])
                func = lambda_funcs.get(layer['name'])

                if func:
                    # ReduceSum operation has 'axis' param as array of ints. When onnx uses ReduceSum
                    # to reproduce SoftMax - dargs become something like [[1]] (list of lists)
                    # that why we handle collections.Iterable
                    if len(dargs) > 1 or isinstance(dargs[0], (tuple, list)):
                        params = inspect.signature(func).parameters
                        i = list(params.keys()).index('axes') if ('axes' in params) else -1

                        if i > 0:
                            i -= 1
                            axes = list(range(len(dargs[i].shape)))
                            axes = axes[0:1] + axes[2:] + axes[1:2]
                            dargs[i] = np.transpose(dargs[i], axes)

                        i = list(params.keys()).index('axis') if ('axis' in params) else -1

                        if i > 0:
                            i -= 1
                            axis = np.array(dargs[i])
                            axes_map = np.array([0, 3, 1, 2])
                            # to list because some tf operations check only for core python types (e.g tf.norm)
                            dargs[i] = axes_map[axis].tolist()
                    else:
                        # if map exits will change else will remain the same
                        dargs[0] = change_ord_axes_map.get(dargs[0], dargs[0])

                kerasf[1] = tuple(dargs)
                layer['config']['function'] = tuple(kerasf)

        keras.backend.set_image_data_format('channels_last')
        # model_tf_ordering = keras.models.Model.from_config(conf)
        model_tf_ordering = load_model_from_config(conf)

        for dst_layer, src_layer, conf in zip(model_tf_ordering.layers, model.layers, conf['layers']):
            W = src_layer.get_weights()
            # TODO: check axes first (if it's not 4D tensor)
            if conf['config'] and 'shared_axes' in conf['config']:
                W[0] = W[0].transpose(1, 2, 0)
            dst_layer.set_weights(W)

        model = model_tf_ordering

    keras.backend.set_image_data_format(keras_fmt)

    logger.debug("Lambda/Custom Layer used during conversion: ")
    for k, v in lambda_funcs.items():
        logger.debug("Layer Name: %s Custom Layer Name: %s", k, v)
    logger.debug(set(lambda_funcs.values()))

    return model, node_keras_mappings, lambda_funcs
