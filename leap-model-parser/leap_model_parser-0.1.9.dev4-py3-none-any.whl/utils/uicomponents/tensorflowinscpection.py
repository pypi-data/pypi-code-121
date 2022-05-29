import json
import os
from typing import List, Optional

import yaml
from leap_model_parser.utils.layerpedia.layerpedia import Layerpedia
from leap_model_parser.utils.tlinspection.leapinspection import LeapInspect


class TensorFlowInspection(LeapInspect):

    def __init__(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        with open(f'{file_path}/ui_components_config.yaml') as f:
            self.yaml_conf = yaml.load(f, Loader=yaml.FullLoader)
        self.ignores = self.yaml_conf['ignores']
        self.args = self.yaml_conf['args']
        self.group_type = self.yaml_conf['group_type']

    def get_function_args(self, func):
        _args = []
        args = LeapInspect.get_function_args(func)
        for arg in args.values():
            arg_name = arg['name']
            if arg_name in self.ignores['args_ignore']:
                continue

            is_tuple = arg.get('type') == 'tuple' and type(arg.get('default_val')) is tuple
            if is_tuple:
                _args.append(arg)
                continue

            if arg_name in list(self.args['arg_group'].keys()):
                arg['type'] = 'select'
                arg['values'] = self.args['arg_values'][self.args['arg_group'][arg_name]]
                arg['default_val'] = self.args['arg_values'][self.args['arg_group'][arg_name]][-1]
            if arg_name in list(self.args['overides'].keys()):
                arg['type'] = self.args['overides'][arg_name]['type']
                arg['isdefault'] = self.args['overides'][arg_name]['isdefault']
                if arg['isdefault']:
                    arg['default_val'] = self.args['overides'][arg_name]['default_val']
            _args.append(arg)
        return _args

    def filter_node(self, node):
        return node['name'] in self.ignores['clsignore']

    def inspect_lib(self, lib):
        # TODO: extract only classes and not aliases
        classes = LeapInspect.get_classes(lib, self.ignores['lib_ignore'])
        nodes = []
        for node_cls in classes:
            if self.filter_node(node_cls):
                continue
            node = {
                'name': node_cls['name'],
                'parents': node_cls['parents'],
                'properties': self.get_function_args(node_cls['class']),
                'options': self.query_layerpedia_options(node_cls['name'])
            }
            shape_rank = self.query_layerpedia_shape_rank(node_cls['name'])
            if shape_rank:
                node['shape_rank'] = shape_rank
            enable_bigger_input_rank = self.query_layerpedia_enable_bigger_input_rank(node_cls['name'])
            if enable_bigger_input_rank:
                node['enable_bigger_input_rank'] = enable_bigger_input_rank
            template_node = {}
            for d in [*node_cls['parents'], node['name']]:
                if d in self.group_type:
                    template_node = {**template_node, **self.group_type[d]}
            node = {**template_node, **node}
            if 'hash' in node and not self.query_layerpedia_is_trainable(node_cls['name']):
                node.pop('hash')
            nodes.append(node)
        return nodes

    def inspect(self, dist: str) -> List[dict]:
        from keras import layers as tf_layers  # type: ignore
        from keras import losses as tf_losses  # type: ignore
        import tensorflow.keras.optimizers as keras_optimizers  # type: ignore
        from onnx2kerastl import customonnxlayer  # type: ignore

        libs = [tf_layers, tf_losses, keras_optimizers, customonnxlayer]
        tofile = []
        for lib in libs:
            nodes = self.inspect_lib(lib)
            tofile.extend(nodes)
        tofile.extend(self.yaml_conf['nodes'])
        with open(f'{dist}ui_components.json', 'w') as outfile:
            json.dump(tofile, outfile, indent=4)
        return tofile

    def query_layerpedia_shape_rank(self, layer_name):
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        if layer_knowledge is None:
            return None
        rank = layer_knowledge.get('rank')
        return rank

    def query_layerpedia_enable_bigger_input_rank(self, layer_name) -> Optional[bool]:
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        return layer_knowledge.get('enable_bigger_input_rank') if layer_knowledge else None

    def query_layerpedia_is_trainable(self, layer_name) -> Optional[bool]:
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        return layer_knowledge.get('is_trainable') if layer_knowledge else None

    def query_layerpedia_options(self, layer_name):
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        if layer_knowledge is None:
            return None
        layer_options = {
            "representation_block": False,
            "layer_inspection": False
        }

        if layer_knowledge['is_trainable']:
            layer_options['representation_block'] = True
            layer_options['layer_inspection'] = True

        return layer_options


if __name__ == '__main__':
    tf_inspection = TensorFlowInspection()
    tf_inspection.inspect("")
