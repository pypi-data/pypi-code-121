import glob
import json
import tempfile
from pathlib import Path
from typing import Callable, Optional, Dict, Tuple

from keras import Model  # type: ignore
from tensorflow.keras.models import load_model  # type: ignore
import tarfile
import ntpath

import onnx  # type: ignore
from onnx2kerastl import onnx_to_keras  # type: ignore

from keras_data_format_converter import convert_channels_first_to_last  # type: ignore

from leap_model_parser.contract.importmodelresponse import NodeResponse, ImportModelTypeEnum
from leap_model_parser.keras_json_model_import import KerasJsonModelImport


class ModelParser:
    def __init__(self):
        self._should_transform_inputs = False

        self._model_types_converter = {
            ImportModelTypeEnum.JSON_TF2.value: self.convert_json_model,
            ImportModelTypeEnum.H5_TF2.value: self.convert_h5_model,
            ImportModelTypeEnum.ONNX.value: self.convert_onnx_model,
            ImportModelTypeEnum.PB_TF2.value: self.convert_pb_model,
        }

    def get_keras_model_and_model_graph(self, model_path: Path, model_type: ImportModelTypeEnum,
                                        should_transform_inputs=False) -> Tuple[
        Dict[str, NodeResponse], Optional[Model]]:
        self._should_transform_inputs = should_transform_inputs
        model_to_keras_converter: Optional[Callable[[str], Dict]] = self._model_types_converter.get(model_type.value)
        if model_to_keras_converter is None:
            raise Exception(f"Unable to import external version, {str(model_path)} file format isn't supported")

        model_schema, keras_model = model_to_keras_converter(str(model_path))
        model_generator = KerasJsonModelImport()
        return model_generator.generate_graph(model_schema), keras_model

    def generate_model_graph(self, model_path: Path, model_type: ImportModelTypeEnum,
                             should_transform_inputs=False) -> Dict[str, NodeResponse]:
        model_graph, _ = self.get_keras_model_and_model_graph(model_path, model_type, should_transform_inputs)
        return model_graph

    @classmethod
    def convert_json_model(cls, file_path: str) -> Tuple[Dict[str, NodeResponse], None]:
        with open(file_path, 'r') as f:
            model_schema = json.load(f)
        return model_schema, None

    def convert_pb_model(self, file_path: str) -> Tuple[Dict[str, NodeResponse], Model]:
        tf = tarfile.open(file_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            tf.extractall(temp_dir)
            pb_files = glob.glob(temp_dir + "/**/*.pb", recursive=True)
            if len(pb_files) == 0:
                raise Exception('no pb files were found')

            pb_file_path = next(iter(pb_files))
            pb_folder_path = next(iter(ntpath.split(pb_file_path)))
            k_model = load_model(pb_folder_path)

        return self.convert_to_keras_model(k_model)

    def convert_onnx_model(self, file_path: str) -> Tuple[Dict[str, NodeResponse], Model]:
        onnx_model = onnx.load_model(file_path)
        input_names = [_input.name for _input in onnx_model.graph.input]
        k_model = onnx_to_keras(onnx_model, input_names=input_names,
                                name_policy='attach_weights_name')

        return self.convert_to_keras_model(k_model)

    def convert_h5_model(self, file_path: str) -> Tuple[Dict[str, NodeResponse], Model]:
        imported_model = load_model(file_path)

        return self.convert_to_keras_model(imported_model)

    def convert_to_keras_model(self, k_model) -> Tuple[Dict[str, NodeResponse], Model]:
        inputs_to_transpose = []
        if self._should_transform_inputs:
            inputs_to_transpose = [k_input.name for k_input in k_model.inputs]

        converted_k_model = convert_channels_first_to_last(k_model, inputs_to_transpose)
        model_schema = json.loads(converted_k_model.to_json())
        model_schema = replace_dots_in_model_schema(model_schema)

        return model_schema, converted_k_model


def replace_dots_in_model_schema(model_schema: dict) -> dict:
    dot_input_names = set()
    for inp_layer in model_schema["config"]["input_layers"]:
        if "." in inp_layer[0]:
            dot_input_names.add(inp_layer[0])
            inp_layer[0] = inp_layer[0].replace(".", "_")
    for layer in model_schema["config"]["layers"]:
        if layer["name"] in dot_input_names:
            layer["name"] = layer["name"].replace(".", "_")
            layer["config"]["name"] = layer["config"]["name"].replace(".", "_")
        for inbound_nodes in layer["inbound_nodes"]:
            try:
                for inbound_node in inbound_nodes:
                    if inbound_node[0] in dot_input_names:
                        inbound_node[0] = inbound_node[0].replace(".", "_")
            except TypeError:
                pass

    return model_schema
