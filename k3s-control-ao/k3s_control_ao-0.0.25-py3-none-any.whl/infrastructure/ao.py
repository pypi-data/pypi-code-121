from typing import List, Union
import requests, json
from ddd_objects.infrastructure.ao import exception_class_dec
from ddd_objects.infrastructure.repository_impl import error_factory
from ddd_objects.domain.exception import return_codes
from .do import (
    CommandResultDO,
    ConditionDO,
    ConfigMapDO,
    ConfigMapUserSettingDO,
    DeploymentDO,
    IngressDO,
    InstanceInfoDO,
    InstanceTypeWithStatusDO,
    NamespaceDO,
    NodeInfoDO,
    NodeMetaDO, 
    NodeUserSettingDO,
    PodDO,
    PodOSSOperationInfoDO,
    ResourceOSSSettingDO,
    SecretDO,
    SecretUserSettingDO,
    ServiceDO
)

class K3SController:
    def __init__(self, ip: str, port: int, token: str) -> None:
        self.url = f"http://{ip}:{port}"
        self.header = {"api-token":token}

    def _check_error(self, status_code, info):
        if status_code>299:
            if isinstance(info['detail'], str):
                return_code = return_codes['OTHER_CODE']
                error_info = info['detail']
            else:
                return_code = info['detail']['return_code']
                error_info = info['detail']['error_info']
            raise error_factory.make(return_code)(error_info)

    @exception_class_dec(max_try=1)
    def check_connection(self, timeout=30):
        response=requests.get(f'{self.url}', headers=self.header, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        if info['message']=='Hello World':
            return True
        else:
            return False

    @exception_class_dec(max_try=1)
    def create_node(self, condition: ConditionDO, node_user_setting: NodeUserSettingDO, timeout=1200):
        data = {
            "condition": condition.to_json(),
            "node_user_setting": node_user_setting.to_json()
        }
        data = json.dumps(data)
        response=requests.post(f'{self.url}/node', headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return NodeInfoDO(**info)

    @exception_class_dec(max_try=1)
    def delete_nodes(self, node_infos: List[Union[NodeInfoDO, NodeMetaDO]], timeout=60):
        data = [info.to_json() for info in node_infos]
        data = json.dumps(data)
        response=requests.delete(f'{self.url}/nodes', headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def get_instance_info_by_node_meta(self, region_id: str, node_meta: NodeMetaDO, timeout=300):
        data = json.dumps(node_meta.to_json())
        response=requests.get(f'{self.url}/instance/region_id/{region_id}/node_meta', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        instance_info, instance_type_info = info
        instance_info = InstanceInfoDO(**instance_info)
        instance_type_info = InstanceTypeWithStatusDO(**instance_type_info)
        return instance_info, instance_type_info

    @exception_class_dec(max_try=1)
    def get_existing_nodes(self, cluster_name: str, timeout=300):
        response=requests.get(f'{self.url}/nodes/cluster_name/{cluster_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [NodeInfoDO(**info) for info in infos]

    @exception_class_dec(max_try=1)
    def get_existing_nodes_by_name(self, node_name:str, timeout=300):
        response=requests.get(f'{self.url}/nodes/node_name/{node_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [NodeInfoDO(**info) for info in infos]

    @exception_class_dec(max_try=1)
    def get_node_metas(self, cluster_name: str, timeout=30):
        response=requests.get(f'{self.url}/node_metas/cluster_name/{cluster_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [NodeMetaDO(**meta) for meta in infos]

    @exception_class_dec(max_try=1)
    def add_node_label(self, node_infos: List[NodeInfoDO], key: str, value: str, timeout=30):
        data = [info.to_json() for info in node_infos]
        data = json.dumps(data)
        response=requests.post(f'{self.url}/label/key/{key}/value/{value}', 
            headers=self.header, data=data, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [CommandResultDO(**r) for r in infos]

    @exception_class_dec(max_try=1)
    def get_namespaces(self, cluster_name: str, timeout=30):
        response=requests.get(f'{self.url}/namespaces/cluster_name/{cluster_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [NamespaceDO(**namespace) for namespace in infos]

    @exception_class_dec(max_try=1)
    def create_namespace(self, cluster_name: str, namespace_name: str, timeout=30):
        response=requests.post(
            f'{self.url}/namespace/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def create_secrets(
        self, 
        cluster_name: str, 
        secret_user_settings: List[SecretUserSettingDO],
        timeout=300
    ):
        data = [setting.to_json() for setting in secret_user_settings]
        data = json.dumps(data)
        response=requests.post(
            f'{self.url}/secrets/cluster_name/{cluster_name}', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def get_secrets(self, cluster_name: str, namespace_name: str, timeout=30):
        response=requests.get(
            f'{self.url}/secrets/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [SecretDO(**s) for s in infos]

    @exception_class_dec(max_try=1)
    def create_config_maps(
        self, 
        cluster_name: str, 
        config_map_user_settings: List[ConfigMapUserSettingDO],
        timeout=300
    ):
        data = [setting.to_json() for setting in config_map_user_settings]
        data = json.dumps(data)
        response=requests.post(
            f'{self.url}/config_maps/cluster_name/{cluster_name}', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def get_config_maps(self, cluster_name:str, namespace_name:str, timeout=30):
        response=requests.get(
            f'{self.url}/config_maps/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [ConfigMapDO(**s) for s in infos]

    @exception_class_dec(max_try=1)
    def create_resource_from_oss(self, cluster_name:str, target_paths:List[str], timeout=60):
        resource_oss_setting = ResourceOSSSettingDO(
            cluster_name=cluster_name, target_paths=target_paths)
        data = json.dumps(resource_oss_setting.to_json())
        response=requests.post(
            f'{self.url}/resource/oss', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def delete_resource_from_oss(self, cluster_name: str, target_paths: List[str], timeout=60):
        resource_oss_setting = ResourceOSSSettingDO(
            cluster_name=cluster_name, target_paths=target_paths)
        data = json.dumps(resource_oss_setting.to_json())
        response=requests.delete(
            f'{self.url}/resource/oss', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def get_deployments(self, cluster_name:str, namespace_name:str, timeout=30):
        response=requests.get(
            f'{self.url}/deployments/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [DeploymentDO(**s) for s in infos]

    @exception_class_dec(max_try=1)
    def get_ingresses(self, cluster_name:str, namespace_name:str, timeout=30):
        response=requests.get(
            f'{self.url}/ingresses/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [IngressDO(**s) for s in infos]

    @exception_class_dec(max_try=1)
    def get_pods(self, cluster_name:str, namespace_name:str, timeout=30):
        response=requests.get(
            f'{self.url}/pods/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [PodDO(**s) for s in infos]

    @exception_class_dec(max_try=1)
    def upload_to_oss_from_pod(self, pod_oss_operation_info: PodOSSOperationInfoDO, timeout=1200):
        data = json.dumps(pod_oss_operation_info.to_json())
        response=requests.post(
            f'{self.url}/oss/pod', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def get_services(self, cluster_name:str, namespace_name:str, timeout=30):
        response=requests.get(
            f'{self.url}/services/cluster_name/{cluster_name}/namespace_name/{namespace_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [ServiceDO(**s) for s in infos]


repo_info = \
{
    "K3SRepository":{
        "add_node_label":{
            "args":[["node_infos", True, "NodeInfo", None, True], ["key", False], ["value", False]],
            "ret":["command_result", True, None, None, True, True]
        },
        "check_connection":{
            "args":[],
            "ret":["bool", False, None, None, False, True]
        },
        "create_config_maps":{
            "args":[["cluster_name", False, "Name"], ["config_map_user_settings", True, "ConfigMapUserSetting", None, True]]
        },
        "create_namespace":{
            "args":[["cluster_name", False, "Name"], ["namespace_name", False, "Name"]]
        },
        "create_node":{
            "args":["condition", "node_user_setting"],
            "ret":["node_info", True, None, None, False, True]
        },
        "create_resource_from_oss":{
            "args":[["cluster_name", False, "Name"], ["target_paths", False, "Path", None, True]]
        },
        "create_secrets":{
            "args":[["cluster_name", False, "Name"], ["secret_user_settings", True, "SecretUserSetting", None, True]]
        },
        "delete_nodes":{
            "args":[["node_infos", True, "NodeInfo", None, True]]
        },
        "delete_resource_from_oss":{
            "args":[["cluster_name", False, "Name"], ["target_paths", False, "Path", None, True]]
        },
        "get_config_maps":{
            "args":[["cluster_name", False, "Name"], ["namespace_name", False, "Name"]],
            "ret":["config_map", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:{namespace_name.get_value()}:config_maps"
        },
        "get_deployments":{
            "args":[["cluster_name", False, "Name"], ["namespace_name", False, "Name"]],
            "ret":["deployment", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:{namespace_name.get_value()}:deployments"
        },
        "get_instance_info_by_node_meta":{
            "args":[["region_id", False], ["node_meta"]],
            "key": "{region_id.get_value()}:{node_name.get_value()}:{node_ip.get_value}:instance_and_instance_type_info"
        },
        "get_existing_nodes":{
            "args":[["cluster_name", False, "Name"]],
            "ret":["node_info", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:existing_nodes"
        },
        "get_existing_nodes_by_name":{
            "args":[["node_name", False, "Name"]],
            "ret":["node_info", True, None, None, True, True],
            "key": "{node_name.get_value()}:existing_nodes"
        },
        "get_namespaces":{
            "args":[["cluster_name", False, "Name"]],
            "ret":["namespace", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:namespaces"
        },
        "get_ingresses":{
            "args":[["cluster_name", False, "Name"], ["namespace_name", False, "Name"]],
            "ret":["ingress", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:{namespace_name.get_value()}:ingresses"
        },
        "get_node_metas":{
            "args":[["cluster_name", False, "Name"]],
            "ret":["node_meta", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:node_metas"
        },
        "get_pods":{
            "args":[["cluster_name", False, "Name"], ["namespace_name", False, "Name"]],
            "ret":["pod", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:{namespace_name.get_value()}:pods"
        },
        "get_secrets":{
            "args":[["cluster_name", False, "Name"], ["namespace_name", False, "Name"]],
            "ret":["secret", True, None, None, True, True],
            "key": "{cluster_name.get_value()}:{namespace_name.get_value()}:secrets"
        },
        "upload_to_oss_from_pod":{
            "args":[["pod_oss_operation_info", True, "PodOSSOperationInfo", None, False, False, "pod_oss_operation_info_converter"]]
        }
    }
}

        
        

