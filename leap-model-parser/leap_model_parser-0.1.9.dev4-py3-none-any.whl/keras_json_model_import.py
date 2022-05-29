import json
from collections import defaultdict
from pathlib import Path
from typing import Set, Dict, Any

from leap_model_parser.contract.importmodelresponse import NodeResponse, WrapperData

layer_attributes_adaptation = {'bias_initializer', 'kernel_initializer'}


class KerasJsonModelImport:
    def __init__(self) -> None:
        self.id = 1
        self.nodes_cache: Dict[str, NodeResponse] = defaultdict()
        self.layer_name_to_layer: Dict[str, Dict] = defaultdict()
        self.visited_connections: Set[str] = set()
        self.ui_components: Dict[str, Dict] = defaultdict()

    def prepare_model_to_import(self, model_schema) -> None:
        ui_components_file_path = Path(__file__).parent / 'contract' / 'ui_components.json'
        with open(str(ui_components_file_path), 'r') as f:
            ui_component_json = json.load(f)

        for layer in model_schema['config']['layers']:
            layer['is_representation_block'] = KerasJsonModelImport.is_representation_block(layer)
            self.layer_name_to_layer[layer['name']] = layer

        self.ui_components = {layer['name']: layer for layer in ui_component_json}

    @staticmethod
    def is_representation_block(layer: Dict[str, Any]) -> bool:
        return len(layer['inbound_nodes']) > 1

    def generate_graph(self, model_schema: Dict) -> Dict[str, NodeResponse]:
        self.prepare_model_to_import(model_schema)
        for graph_output_layer in model_schema['config']['output_layers']:
            current_layer = self.layer_name_to_layer[graph_output_layer[0]]
            self.generate_graph_recursive(current_layer, graph_output_layer[1])

        nodes = {node.id: node for node in self.nodes_cache.values() if not node.name == 'Lambda'}
        _add_origin_name_to_nodes(nodes)
        return nodes

    def _prepare_inbound_nodes_to_enumerate(self, inbound_nodes_to_enumerate):
        inbound_nodes_to_enumerate_prepared = []
        single_inbound_node_to_enumerate = []
        for element in inbound_nodes_to_enumerate:
            if not isinstance(element, dict):
                single_inbound_node_to_enumerate.append(element)
            else:
                if single_inbound_node_to_enumerate:
                    inbound_nodes_to_enumerate_prepared.append(single_inbound_node_to_enumerate)
                single_inbound_node_to_enumerate = []
                for inbound_nodes in element.values():
                    if isinstance(inbound_nodes, list):
                        inbound_nodes_to_enumerate_prepared.extend(
                            self._prepare_inbound_nodes_to_enumerate(inbound_nodes))
        if single_inbound_node_to_enumerate:
            inbound_nodes_to_enumerate_prepared.append(single_inbound_node_to_enumerate)

        return inbound_nodes_to_enumerate_prepared

    def generate_graph_recursive(self, current_layer: Dict[str, Any], instance_index: int):
        self.generate_node(current_layer, instance_index)

        inbound_nodes = current_layer['inbound_nodes']
        if len(inbound_nodes) == 0:
            return
        inbound_nodes_to_enumerate = inbound_nodes[instance_index]
        if not isinstance(inbound_nodes_to_enumerate[0], list):
            inbound_nodes_to_enumerate = self._prepare_inbound_nodes_to_enumerate(inbound_nodes_to_enumerate)

        for input_index, input_layer_item in enumerate(inbound_nodes_to_enumerate):
            input_layer = self.layer_name_to_layer[input_layer_item[0]]
            self.generate_node(input_layer, input_layer_item[1])

            input_node_name = f"{input_layer['name']}_{input_layer_item[1]}"
            current_node_name = f"{current_layer['name']}_{instance_index}"
            connection_name = f"{input_node_name}_{current_node_name}_{input_index}"
            if connection_name in self.visited_connections:
                continue

            self.visited_connections.add(connection_name)
            self.attach(input_layer, input_node_name, current_node_name, input_index)
            self.generate_graph_recursive(current_layer=input_layer, instance_index=input_layer_item[1])

    def attach(self, input_layer: Dict, node_input_layer_name: str, node_output_layer_name: str, input_index: int):
        node_output_layer = self.nodes_cache[node_output_layer_name]
        if input_layer['class_name'] == 'InputLayer':
            if node_output_layer.name == 'Lambda':
                return
            node_input_layer_name = 'Dataset'

        node_input_layer = self.nodes_cache[node_input_layer_name]
        node_output_key = self.get_connection_key(input_layer, node_input_layer, 'outputs', input_index)
        node_input_key = self.get_connection_key(input_layer, node_output_layer, 'inputs', input_index)

        if node_output_key not in node_input_layer.outputs:
            node_input_layer.outputs[node_output_key] = {'connections': []}
        node_input_layer.outputs[node_output_key]['connections'].append({
            "node": node_output_layer.id,
            "input": node_input_key
        })

        if node_input_key not in node_output_layer.inputs:
            node_output_layer.inputs[node_input_key] = {'connections': []}
        node_output_layer.inputs[node_input_key]['connections'].append({
            "node": node_input_layer.id,
            "output": node_output_key
        })

    def generate_node(self, layer: Dict[str, Any], instance_index: int):
        if layer['class_name'] == 'InputLayer':
            self.handle_input_layer(layer)
            return

        node_key = f"{layer['name']}_{instance_index}"
        if node_key in self.nodes_cache:
            return

        layer = self.handle_cudnn(layer)
        layer_metadata = self.ui_components.get(layer['class_name'])
        if layer_metadata is None:
            raise Exception(f"{layer['class_name']} layer is not supported, please try to contact Tensorleap support")

        if layer_metadata['type'] == 'wrapper':
            wrapped_layer = self.handle_wrapper_layer(layer)
            self.generate_node(wrapped_layer, instance_index)
            return

        if layer['is_representation_block']:
            self.generate_rp_node(layer, layer_metadata, node_key)
        else:
            self.generate_regular_node(layer, layer_metadata, node_key)
        self.id += 1

    def generate_regular_node(self, layer: Dict[str, Any], layer_metadata: Dict[str, Any], node_key: str):
        data = layer['config']
        if layer['class_name'] in ('TFOpLambda', 'SlicingOpLambda'):
            data['additional_arg_names'] = ['inbound_nodes']
            data['inbound_nodes'] = layer['inbound_nodes'][0]

        self.layer_data_adjustments(data, layer_metadata)
        node = NodeResponse(id=str(self.id), name=layer["class_name"], data=data)
        if 'wrapper' in layer:
            node.wrapper = layer['wrapper']
        self.nodes_cache[node_key] = node

    @classmethod
    def handle_wrapper_layer(cls, layer):
        wrapped_layer = layer['config']['layer']
        wrapped_layer['name'] = layer['name']
        wrapped_layer['is_representation_block'] = layer['is_representation_block']
        wrapper_data = layer['config'].copy()
        wrapper_data.pop('layer')
        wrapper_data.pop('name')
        # TODO: remove this hard coded condition after support
        if 'merge_mode' in wrapper_data and wrapper_data.get('merge_mode') is None:
            raise Exception(f"{layer['class_name']} layer with merge_mode None is not supported,"
                            f" please try to contact Tensorleap support")
        wrapped_layer['wrapper'] = WrapperData(layer['class_name'], wrapper_data)
        return wrapped_layer

    @classmethod
    def layer_data_adjustments(cls, layer_config: Dict[str, Any], layer_metadata: Dict[str, Any]) -> None:
        if layer_metadata['name'] == 'Lambda':
            layer_config.pop('function')

        for layer_attribute in layer_attributes_adaptation:
            if layer_attribute in layer_config:
                layer_config[layer_attribute] = layer_config[layer_attribute]['class_name']

        layer_config["type"] = layer_metadata.get('type')
        # TODO: remove this hard coded condition after support
        if layer_config.get('return_state'):
            raise Exception(f"{layer_metadata.get('name')} layer with return_state True is not supported,"
                            f" please try to contact Tensorleap support")

    def generate_rp_node(self, layer: Dict[str, Any], layer_metadata: Dict[str, Any], node_key: str) -> None:
        if layer['name'] not in self.nodes_cache:
            data = layer['config']
            self.layer_data_adjustments(data, layer_metadata)
            data["output_blocks"] = []
            node = NodeResponse(id=str(self.id), name=layer["class_name"], data=data)
            if 'wrapper' in layer:
                node.wrapper = layer['wrapper']
            self.nodes_cache[layer['name']] = node

            self.id += 1
        data = {
            "output_name": "Action",
            "node_id": self.nodes_cache[layer["name"]].id,
            "parent_name": layer["class_name"]
        }
        self.nodes_cache[node_key] = NodeResponse(id=str(self.id), name='Representation Block', data=data)
        self.nodes_cache[layer["name"]].data["output_blocks"].append({
            "block_node_id": self.nodes_cache[node_key].id,
            "output_name": "Action"
        })

    def get_connection_key(self, node_input_layer, node: NodeResponse, direction: str, index: int) -> str:
        layer_metadata = self.ui_components.get(node.name)
        if node.name == 'Representation Block' or layer_metadata is None:
            if direction == 'inputs':
                connection_format = f"{node.id}-input"
            else:
                connection_format = f"{node.id}-feature_map"
        elif node.name == 'Dataset':
            connection_format = f"{node.id}-{node_input_layer['name']}"
        else:
            connection_format = layer_metadata[f"{direction}_data"][direction][0]['name']
            if connection_format.count('${id}') > 0:
                connection_format = f"{node.id}-{index}"
                if 'custom_input_keys' not in node.data:
                    node.data['custom_input_keys'] = []
                node.data['custom_input_keys'].append(connection_format)
            else:
                connection_format = f"{node.id}-{connection_format}"
        return connection_format

    def handle_cudnn(self, layer: Dict[str, Any]) -> Dict[str, Any]:
        if layer['class_name'] == 'CuDNNGRU':
            layer['class_name'] = 'GRU'
            gru_metadata = self.ui_components['GRU']
            gru_config = {}
            for gru_prop in gru_metadata["properties"]:
                if gru_prop["name"] in layer['config']:
                    gru_config[gru_prop["name"]] = layer['config'][gru_prop["name"]]
                elif gru_prop["isdefault"]:
                    gru_config[gru_prop["name"]] = gru_prop["default_val"]

            gru_config["name"] = layer['config']["name"]
            gru_config["trainable"] = layer['config']["trainable"]

            layer['config'] = gru_config
        return layer

    def handle_input_layer(self, layer: Dict[str, Any]):
        if 'Dataset' not in self.nodes_cache:
            self.nodes_cache['Dataset'] = NodeResponse(id=str(self.id), name='Dataset', data=DATASET_DATA)
            self.id += 1

        dataset = self.nodes_cache['Dataset']
        inputs = dataset.data['datasetVersion']['metadata']['setup']['inputs']

        if not any(input_data['name'] == layer['name'] for input_data in inputs):
            shape = layer['config']['batch_input_shape']
            input_data = {'name': layer['name'], 'shape': shape[1:]}
            inputs.append(input_data)


def _add_origin_name_to_nodes(nodes: Dict[str, NodeResponse]):
    for node in nodes.values():
        if "name" in node.data:
            node.data["origin_name"] = node.data["name"]
            node.data.pop("name")


DATASET_DATA = {'datasetVersion': {'metadata': {'setup': {'preprocess': {'training_length': 0, 'validation_length': 0},
                'inputs': [], 'metadata': [], 'outputs': [], 'visualizers': [], 'prediction_types': [],
                'custom_loss_names': []}}},
                'type': 'dataset'}
