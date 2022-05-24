# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Collection of helper functions for ONNX conversion."""

import os
import logging
import copy
import tempfile

import keras
import onnx
import onnxruntime
import numpy as np
from skl2onnx.helpers.onnx_helper import select_model_inputs_outputs
import tensorflow as tf
from tensorflow.python.client import device_lib


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
            return onnx.numpy_helper.to_array(getattr(onnx_attr, 't'))

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


def is_numpy(obj):
    """Check of the type is instance of numpy array.

    Args:
        obj: object to check

    Returns:
        obj: True if the object is numpy-type array.
    """
    return isinstance(obj, (np.ndarray, np.generic, list))


def ensure_numpy_type(obj):
    """Raise exception if it's not a numpy.

    Args:
        obj: object to check

    Returns:
        obj: numpy object
    """
    if is_numpy(obj):
        return obj
    raise AttributeError(f'Not a numpy type. {type(obj)}')


def ensure_tf_type(obj, fake_input_layer=None, name=None):
    """Convert to Keras Constant if needed.

    Args:
        obj: numpy / tf type
        fake_input_layer: fake input layer to add constant

    Returns:
        obj: tf type
    """
    if is_numpy(obj):
        if obj.dtype == np.int64:
            obj = np.int32(obj)

        def target_layer(_, inp=obj, dtype=obj.dtype.name):
            import tensorflow as tf  # noqa pylint: disable=c0415, w0404
            if not isinstance(inp, (np.ndarray, np.generic)):
                inp = np.array(inp, dtype=dtype)
            return tf.constant(inp, dtype=inp.dtype)

        lambda_layer = keras.layers.Lambda(target_layer, name=name)
        return lambda_layer(fake_input_layer)

    return obj


def tf_shape(tensor, dtype=tf.int64):
    """Helper function returning the shape of a Tensor.

    The function will check for fully defined shape and will return
    numpy array or if the shape is not fully, it defined will use
    `tf.shape()` to return the shape as a Tensor.

    Args:
        tensor: A Tensor
        dtype: (Optional) The output dtype (tf.int32 or tf.int64).
                    Defaults to tf.int64.

    Returns:
        shape: Shape of the tensor
    """
    if tensor.shape.is_fully_defined():
        return np.array(tensor.shape.as_list(), dtype=dtype.as_numpy_dtype)
    return tf.shape(tensor, out_type=dtype)


def test_diff(model, onnx_model_path, model_name, penultimate_node=None, epsilon=1e-5):
    """Test difference between ONNX and Keras model used in entrypoint.

    Args:
        model: keras model
        onnx_model_path: path to the ONNX file
        model_name: name of the model
        penultimate_node: name of the node to intercept
        epsilon: absolute tolerance
    """
    logger = logging.getLogger(f"{__name__}.test_diff")

    # If penultimate node is specified, we need to intercept intermediate output in ONNX graph
    if penultimate_node:
        model_onnx = onnx.load(onnx_model_path)
        new_onnx = select_model_inputs_outputs(model_onnx, penultimate_node)

        fd, path = tempfile.mkstemp()
        new_model_path = os.path.join(path)
        onnx.save(new_onnx, new_model_path)

        session = onnxruntime.InferenceSession(new_model_path, None)
        os.close(fd)
    else:
        session = onnxruntime.InferenceSession(onnx_model_path, None)

    # Test on random inputs
    input_shape = model.input.get_shape().as_list()
    img = np.random.rand(1, *input_shape[1:]).astype(np.float32)

    onnx_preds = session.run(None, {session.get_inputs()[0].name: img})
    preds = model.predict(img)

    logger.info("Input Shape: %s", input_shape)

    if not isinstance(onnx_preds, list):
        onnx_preds = [onnx_preds]

    if not isinstance(preds, list):
        preds = [preds]

    passed = True
    for onnx_pred, pred in zip(onnx_preds, preds):
        onnx_pred_shape = list(onnx_pred.shape)
        pred_shape = list(pred.shape)

        # Check the output shape matches
        if onnx_pred_shape != pred_shape:
            raise ValueError(f"Original ONNX Output Shape {onnx_pred_shape} & Keras Output Shape {pred_shape}. "
                             f"Please check your penultimate node which was {penultimate_node}.")

        logger.info("ONNX Output Shape: %s & Keras Output Shape: %s", onnx_pred_shape, pred_shape)
        error = np.max(np.abs(onnx_pred - pred))
        if not (np.allclose(onnx_pred, pred, atol=epsilon)):
            logger.info("Difference between the original ONNX and converted Keras model is larger than "
                        "the set threshold %s with error of %s. ", epsilon, error)
            logger.info("This may be due to difference in deep learning frameworks. "
                        "If the error is not far from the threshold, you may proceed with training with TAO Toolkit. "
                        "If difference is large, please post an issue on the forum and link your original model.\n")
            logger.debug(error)
            logger.debug(onnx_pred[0])
            logger.debug(pred[0])
            passed = False

    if passed:
        logger.info("Model \"%s\" was converted successfully\n", model_name)


def freeze_nodes(model, freeze_node_list, layer_mappings):
    """Freeze provided layers.

    Args:
        model: A Keras Model
        freeze_node_list: list of ONNX nodes to freeze
        layer_mappings: mapping of ONNX node names and keras layer names

    Returns:
        model: Updated Keras Model
    """
    logger = logging.getLogger("tao_byom.freeze_nodes")

    inverted_layer_mappings = {v: k for k, v in layer_mappings.items()}
    frozen_layers = []
    for layer in model.layers:
        if hasattr(layer, "trainable") and \
                layer.name in inverted_layer_mappings and \
                inverted_layer_mappings[layer.name] in freeze_node_list:
            msg = f"Freezing ONNX node {inverted_layer_mappings[layer.name]} \
                    keras layer {layer.name} {type(layer)}"
            logger.debug(msg)

            layer.trainable = False
            frozen_layers.append(layer.name)

    return model, frozen_layers


def freeze_batchnorm(model):
    """Freeze every BatchNormalization layers in the model.

    The BN will be run in inference mode.
    Ref: https://github.com/keras-team/keras/pull/9965#issuecomment-587527961

    Args:
        model: A Keras Model

    Returns:
        model: Updated Keras Model
    """
    logger = logging.getLogger("tao_byom.freeze_batchnorm")

    # set training=False for BN layers
    def compose_call(prev_call_method):
        def call(self, inputs, training=False):
            return prev_call_method(self, inputs, training)

        return call

    logger.debug("Freezing every BN in the model")

    # We potentially need this to be a different object to avoid recursion
    prev_batchnorm_call = copy.deepcopy(keras.layers.normalization.BatchNormalization.call)
    keras.layers.normalization.BatchNormalization.call = compose_call(
        prev_batchnorm_call
    )

    return model


def get_gpu_type():
    """Return list of GPUs in the machine"""
    devices = device_lib.list_local_devices()
    return [device.physical_device_desc for device in devices if device.device_type == "GPU"]


def disable_tf32():
    """Disable TF32 for Ampere machines

    NVIDIA TensorFlow 1.15.2 from 20.06 release uses Ampere TF32 capabilities as default.
    This will lead to discrepency with ONNX and other DL frameworks.
    Hence, we disable this behavior.
    Ref: https://developer.nvidia.com/blog/accelerating-tensorflow-on-a100-gpus/
    """
    logger = logging.getLogger("tao_byom.disable_tf32")

    devices = device_lib.list_local_devices()
    for device in devices:
        if device.device_type == "GPU":
            os.environ["NVIDIA_TF32_OVERRIDE"] = "0"
            logger.debug("Disabling TF32")
            break
