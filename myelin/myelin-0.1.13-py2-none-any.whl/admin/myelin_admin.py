import json
import os
from collections import namedtuple

import requests

ModelBackendMetadata = namedtuple('ModelBackendMetadata', 'id name url publicUrl clusterUrl status model_path timestamp')
TaskMetadata = namedtuple('TaskMetadata', 'id name status model_path data_path timestamp')


class MyelinAdmin:
    def __init__(self):
        self.admin_url = os.environ.get("ADMIN_URL") or None

        jwt_token = os.environ.get("ADMIN_JWT_TOKEN")
        if jwt_token is None:
            token_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
            if os.path.exists(token_file):
                with open(token_file, 'r') as file:
                    jwt_token = file.read().replace('\n', '')

        self.jwt_token = jwt_token

    def task(self, axon, task_name, namespace, default_value=None):
        if self.admin_url is None:
            return default_value

        response = requests.get("%s/api/v1/axons/%s/%s" % (self.admin_url, namespace, axon),
                                 headers={'Authorization': 'Bearer %s' % self.jwt_token})

        if response.ok:
            axon_details = response.json()
            all_sensors_executions =[item for sublist in [x['children'] for x in axon_details['sensors']] for item in sublist]
            all_tasks_executions =[item for sublist in [x['children'] for x in all_sensors_executions] for item in sublist if item['taskName'] == task_name]

            sorted_tasks = sorted(all_tasks_executions, key=lambda x: x['startedAtTs'], reverse=True)
            if len(sorted_tasks) > 0:
                latest_task = sorted_tasks[0]
                template = latest_task["template"]
                model_path = self.get_env(template["container"]['env'], 'MODEL_PATH')
                data_path = self.get_env(template["container"]['env'], 'DATA_PATH')
                return TaskMetadata(
                    id=latest_task['name'],
                    name=task_name,
                    status=latest_task['status'],
                    model_path=model_path,
                    data_path=data_path,
                    timestamp=latest_task['startedAtTs'])
            else:
                return None
        else:
            raise Exception("Failed to retrieve metadata from admin host %s, got response %s " %
                            (self.admin_url, response.content))

    def model_backend(self, axon, model_graph, model, model_backend, namespace, default_value=None):
        if self.admin_url is None:
            return default_value

        response = requests.post("%s/model-graphs/%s" % (self.admin_url, model_graph),
                                 json={"namespace": namespace, "axon": axon},
                                 headers={'Authorization': 'Bearer %s' % self.jwt_token})

        if response.ok:
            model_graphs_rs = response.json()
            model_graphs = sorted(model_graphs_rs['deployedModelGraphs'], key=lambda x: x['startedAtTs'], reverse=True)
            if len(model_graphs) > 0:
                latest_model_graph = model_graphs[0]
                for m in latest_model_graph['models']:
                    if m['modelName'] == model:
                        for backend in m['backends']:
                            if backend['modelBackendName'] == model_backend:
                                model_path = self.get_env(backend['env'], 'MODEL_PATH')
                                return ModelBackendMetadata(
                                    id=backend['name'],
                                    url=backend['url'],
                                    publicUrl=backend['publicUrl'],
                                    clusterUrl=backend['clusterUrl'],
                                    status=backend['status'],
                                    name=model_backend,
                                    model_path=model_path,
                                    timestamp=backend['startedAtTs'])
            else:
                return None
        else:
            raise Exception("Failed to retrieve metadata from admin host %s, got response %s " %
                            (self.admin_url, response.content))

    @staticmethod
    def get_env(env, evn_name):
        for e in env:
            if e['name'] == evn_name:
                return e['value']
        return None


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

