from typing import List, Optional, Union
from ddd_objects.domain.repository import Repository
from .entity import(
    Condition,
    CommandResult
)
from .value_obj import(
    Name
)
from ..domain.entity import (
    Condition,
    Namespace,
    Deployment,
    Ingress,
    PodOSSOperationInfo,
    ConfigMap,
    CommandResult,
    Pod,
    ConfigMapUserSetting,
    Secret,
    NodeMeta,
    NodeUserSetting,
    NodeInfo,
    SecretUserSetting
)
from ..domain.value_obj import (
    Key,
    Bool,
    Name,
    Value,
    Path
)


class K3SRepository(Repository):

    def add_node_label(self, node_infos: List[Union[NodeInfo, NodeMeta]], key: Key, value: Value)->Optional[List[CommandResult]]:
        raise NotImplementedError

    def check_connection(self, )->Optional[Bool]:
        raise NotImplementedError

    def create_config_maps(self, cluster_name: Name, config_map_user_settings: List[ConfigMapUserSetting])->None:
        raise NotImplementedError

    def create_namespace(self, cluster_name: Name, namespace_name: Name)->bool:
        raise NotImplementedError

    def create_node(self, condition: Condition, node_user_setting: NodeUserSetting)->Optional[NodeInfo]:
        raise NotImplementedError

    def create_resource_from_oss(self, cluster_name: Name, target_paths: List[Path])->bool:
        raise NotImplementedError

    def create_secrets(self, cluster_name: Name, secret_user_settings: List[SecretUserSetting])->bool:
        raise NotImplementedError

    def delete_nodes(self, node_infos: List[NodeInfo])->bool:
        raise NotImplementedError

    def delete_resource_from_oss(self, cluster_name: Name, target_paths: List[Path])->bool:
        raise NotImplementedError

    def get_config_maps(self, cluster_name: Name, namespace_name: Name)->Optional[List[ConfigMap]]:
        raise NotImplementedError

    def get_deployments(self, cluster_name: Name, namespace_name: Name)->Optional[List[Deployment]]:
        raise NotImplementedError

    def get_existing_nodes(self, cluster_name: Name)->Optional[List[NodeInfo]]:
        raise NotImplementedError

    def get_existing_nodes_by_name(self, node_name: Name)->Optional[List[NodeInfo]]:
        raise NotImplementedError

    def get_namespaces(self, cluster_name: Name)->Optional[List[Namespace]]:
        raise NotImplementedError

    def get_node_metas(self, cluster_name: Name)->Optional[List[NodeMeta]]:
        raise NotImplementedError

    def get_pods(self, cluster_name: Name, namespace_name: Name)->Optional[List[Pod]]:
        raise NotImplementedError

    def get_secrets(self, cluster_name: Name, namespace_name: Name)->Optional[List[Secret]]:
        raise NotImplementedError

    def upload_to_oss_from_pod(self, pod_oss_operation_info: PodOSSOperationInfo)->bool:
        raise NotImplementedError

    def get_ingresses(self, cluster_name: Name, namespace_name: Name)->Optional[List[Ingress]]:
        raise NotImplementedError