from copy import deepcopy
from .constants import special_topics, PIPELINE_INPUT_TPL, TOPIC_TPL, TOPIC_TPL_IN
from .dockerfile_generator import FabriqueDockerfile
from .templates_generator import TemplatesGenerator
import os
import sys
import json

TOPIC_PREFIX = os.getenv('FABRIQUE_TOPIC_PREFIX', 'fabrique')


class ActorConfigs:
    """
    All information to start all actors with different
    pipeline_out and pipeline_inputs
    and for Kubernetes
    """

    def __init__(self,
                 nodes,
                 pipeline_name='pipeline_name',
                 pipeline_version='pipeline_version'
                 ):

        assert nodes
        self.nodes = nodes
        self.pipeline_name = pipeline_name
        self.pipeline_version = pipeline_version
        self.pipeline_in_topic = PIPELINE_INPUT_TPL.format(prefix=TOPIC_PREFIX,
                                                           pipeline_name=self.pipeline_name,
                                                           pipeline_version=self.pipeline_version)

    def nodename2config(self, nodename, store=None):
        name2config = self.nodename2configs(store)
        return name2config[nodename]

    def save_nodes_for_prod(self, proj_path):
        with open(os.path.join(proj_path, 'pipeline.json'), 'w') as fp:
            json.dump({'nodes': self.nodes, 'python_ver': sys.version_info}, fp, indent=2)

        print(f'pipeline.json is generated in {proj_path}')

    @staticmethod
    def generate_dockerfile(proj_path):
        FabriqueDockerfile(pipeline_pth=proj_path).render_and_write()

    def generate_templates(self, proj_path):
        TemplatesGenerator(proj_path, self.nodes.keys()).write()

    def nodename2configs(self, store=None):
        message_busses = self.make_message_bus_configs()
        name2config = {}
        for nodename, message_bus in message_busses.items():
            config = {}
            if store:
                config['store'] = store
            config['message_bus'] = message_bus
            name2config[nodename] = config
        return name2config

    def make_message_bus_configs(self):
        message_busses = {}
        for nodename, node in self.nodes.items():
            message_busses[nodename] = {}

            for field in node:
                if field in ['engine_instance', ]:
                    continue
                message_busses[nodename][field] = deepcopy(node[field])

        for node_name, node in message_busses.items():
            actor_type = node['actor_type']

            # group_ids
            node['group_id'] = f"{self.pipeline_name}-{self.pipeline_version}"
            node['client_id'] = node_name
            node['type'] = actor_type

            # out_topics -> in_topics
            if actor_type == 'dispatcher':
                node['out_topic_dict'] = {}
                for output in node['outputs']:
                    if output == 'end':
                        node['out_topic_dict'][output] = special_topics.end
                        continue
                    topic_name = TOPIC_TPL_IN.format(prefix=TOPIC_PREFIX,
                                                     to_node=output,
                                                     pipeline_name=self.pipeline_name,
                                                     pipeline_version=self.pipeline_version)
                    node['out_topic_dict'][output] = topic_name
                    message_busses[output]['in_topic'] = topic_name

            else:
                output = node['outputs'][0]
                if output == 'end':
                    node['out_topic'] = special_topics.end
                else:
                    topic_name = TOPIC_TPL.format(prefix=TOPIC_PREFIX,
                                                  from_node=node_name,
                                                  pipeline_name=self.pipeline_name,
                                                  pipeline_version=self.pipeline_version)
                    node['out_topic'] = topic_name
                    message_busses[output]['in_topic'] = topic_name

            node['error_topic'] = special_topics.error
            node['metrics_topic'] = special_topics.metrics

            if node['from'][0] == 'begin':
                node['in_topic'] = self.pipeline_in_topic

            for field in ['class_name', 'actor_type', 'outputs', 'engine_cls', 'from']:
                node.pop(field, None)

        return message_busses
