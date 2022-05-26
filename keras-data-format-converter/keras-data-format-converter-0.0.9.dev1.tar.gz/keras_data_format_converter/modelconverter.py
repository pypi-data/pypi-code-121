import logging
from typing import List, Dict, Set

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Cropping2D, Cropping3D, UpSampling2D, UpSampling3D, ZeroPadding2D, ZeroPadding3D, \
    ConvLSTM2D, Flatten, Layer, InputLayer, Input
from tensorflow.python.keras.engine.node import Node
from tensorflow.python.keras.layers.convolutional import Conv
from tensorflow.python.keras.layers.pooling import GlobalPooling1D, GlobalPooling2D, GlobalPooling3D

from keras_data_format_converter.layers.layer_utils import convert_layer


class ModelConverter:
    """The ModelConverter object converts keras models to the requested data_format

    The conversion process is handling special layers with data_format specific values like Concatenate,
    BatchNormalization, Reshape, etc. The logic of handling those layers is as follows:
    every special layer after an input from inputs_to_transpose until a layer with shape rank of 2 is being handled.

    :param target_data_format: Requested new data_format
    :type target_data_format: str
    :param inputs_to_transpose: List of input names required to be transposed
    :type inputs_to_transpose: List[str]
    :param model: The model to convert
    :type model: tensorflow.keras.Model
    """

    def __init__(self, model: keras.Model, target_data_format: str, inputs_to_transpose: List[str]):
        self.target_data_format: str = target_data_format
        self.inputs_to_transpose: List[str] = inputs_to_transpose
        self.model: keras.Model = model

        # transform_signal properties
        self._add_transform_signal_properties()

        # cache properties
        self._clear_cache()

        # logger
        self._logger = logging.getLogger(__name__)

    def convert_model(self) -> keras.Model:
        """
        Converting model to the requested target_data_format

        :return: Converted model
        :rtype: tensorflow.keras.Model
        """

        self._clear_cache()
        output_tensors: List[tf.Tensor] = []
        for out_tensor in self.model.outputs:
            converted_tensor = self._convert_tensor(out_tensor)
            output_tensors.append(converted_tensor)
        converted_model = tf.keras.Model(inputs=self._model_input_tensors, outputs=output_tensors)
        return converted_model

    def _convert_tensor(self, tensor: tf.Tensor) -> tf.Tensor:
        tensor_id = id(tensor)
        converted_tensor = self._tensor_cache.get(tensor_id)
        if converted_tensor is not None:
            return converted_tensor

        current_node = self._get_node_from_tensor(tensor)
        current_layer = self._get_layer_from_tensor(tensor)
        # Creating first model input layer
        if isinstance(current_layer, InputLayer):
            input_tensor = self._convert_input_tensor(tensor)
            self._tensor_cache[tensor_id] = input_tensor
            self._update_forward_tensor_transform_signal(input_tensor, is_input_tensor=True)
            self._model_input_tensors.append(input_tensor)
            return input_tensor

        # add backward layer signal
        self._update_backward_layer_transform_signal(current_node, current_layer)

        # get all input tensors
        node_input_tensors = []
        parent_nodes = current_node.parent_nodes
        for parent_node in parent_nodes:
            output_tensor = parent_node.outputs
            node_input_tensor = self._convert_tensor(output_tensor)
            node_input_tensors.append(node_input_tensor)

        layer_input_shape = [node_input_tensor.shape for node_input_tensor in node_input_tensors]
        self._update_forward_layer_transform_signal(node_input_tensors, current_layer)
        transform_signal = self._calc_transform_signal(node_input_tensors, current_layer)
        # squeeze
        if len(node_input_tensors) == 1:
            node_input_tensors = node_input_tensors[0]
            layer_input_shape = layer_input_shape[0]

        layer_name = current_layer.name
        converted_layer = self._layer_cache.get(layer_name)
        if converted_layer is None:
            converted_layer = convert_layer(current_layer, self.target_data_format, layer_input_shape, transform_signal)
            self._layer_cache[layer_name] = converted_layer

        converted_tensor = converted_layer(node_input_tensors)
        self._tensor_cache[tensor_id] = converted_tensor
        self._update_forward_tensor_transform_signal(converted_tensor, transform_signal=transform_signal,
                                                     is_input_tensor=False)
        return converted_tensor

    def _get_transform_signal(self, node_input_tensors: List[tf.Tensor]) -> bool:
        transform_signal = any(id(node_input_tensor) in self._tensor_transform_signal for node_input_tensor in
                               node_input_tensors)
        return transform_signal

    @staticmethod
    def _get_layer_from_tensor(tensor: tf.Tensor) -> Layer:
        history = tensor._keras_history
        layer = history.layer
        return layer

    @staticmethod
    def _get_node_from_tensor(tensor: tf.Tensor) -> Node:
        history = tensor._keras_history
        layer = history.layer
        node_index = history.node_index
        node = layer.inbound_nodes[node_index]
        return node

    def _convert_input_tensor(self, input_tensor: tf.Tensor) -> tf.Tensor:
        input_layer = input_tensor._keras_history.layer
        inp_config = input_layer.get_config()
        if input_tensor.name in self.inputs_to_transpose:
            input_shape = inp_config["batch_input_shape"]
            transposed_input_shape = (input_shape[0], *input_shape[2:], input_shape[1])
            if self.target_data_format == "channels_first":
                transposed_input_shape = (input_shape[0], input_shape[-1], *input_shape[1:-1])
            inp_config["batch_input_shape"] = transposed_input_shape

        new_input_tensor = Input(**inp_config)
        self._logger.debug(f"Input created, name: {new_input_tensor.name}, shape: {new_input_tensor.shape}")
        return new_input_tensor

    def _clear_cache(self) -> None:
        self._layer_cache: Dict[str, Layer] = {}
        self._tensor_cache: Dict[int, tf.Tensor] = {}
        self._tensor_transform_signal: Set[int] = set()
        self._model_input_tensors: List[tf.Tensor] = []
        self._layer_transform_signal: Set[str] = set()

    def _update_forward_tensor_transform_signal(self, tensor: tf.Tensor, is_input_tensor: bool,
                                                transform_signal: bool = False) -> None:
        if (is_input_tensor and tensor.name in self.inputs_to_transpose) or \
                (transform_signal and tensor.shape.rank != 2):
            tensor_id = id(tensor)
            self._tensor_transform_signal.add(tensor_id)

    def _add_transform_signal_properties(self) -> None:
        self._layers_type_transform_signal = (Conv, Cropping2D, Cropping3D,
                                              UpSampling2D, UpSampling3D, ZeroPadding2D,
                                              ZeroPadding3D, ConvLSTM2D)

        self._layers_type_not_transform_signal = (Flatten, GlobalPooling1D, GlobalPooling2D, GlobalPooling3D)

    def _update_backward_layer_transform_signal(self, node: Node, layer: Layer) -> None:
        layer_name = layer.name
        if isinstance(layer, self._layers_type_transform_signal):
            data_format = layer.data_format
            if data_format != self.target_data_format:
                self._layer_transform_signal.add(layer_name)

        # signal all back layers
        if layer_name in self._layer_transform_signal:
            parent_nodes = node.parent_nodes
            for parent_node in parent_nodes:
                output_tensor = parent_node.outputs
                backwards_layer = self._get_layer_from_tensor(output_tensor)
                if not isinstance(backwards_layer, self._layers_type_not_transform_signal):
                    backwards_layer_name = backwards_layer.name
                    self._layer_transform_signal.add(backwards_layer_name)

    def _calc_transform_signal(self, node_input_tensors: List[tf.Tensor], current_layer: Layer) -> bool:
        input_transform_signal = any(id(node_input_tensor) in self._tensor_transform_signal for node_input_tensor in
                                     node_input_tensors)
        layer_name = current_layer.name
        layer_transform_signal = layer_name in self._layer_transform_signal
        transform_signal = input_transform_signal or layer_transform_signal
        return transform_signal

    def _update_forward_layer_transform_signal(self, node_input_tensors: List[tf.Tensor], forward_layer: Layer) -> None:
        if isinstance(forward_layer, self._layers_type_not_transform_signal):
            return

        for node_input_tensor in node_input_tensors:
            back_layer = self._get_layer_from_tensor(node_input_tensor)
            back_layer_name = back_layer.name
            if back_layer_name in self._layer_transform_signal:
                forward_layer_name = forward_layer.name
                self._layer_transform_signal.add(forward_layer_name)
                return
