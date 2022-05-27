import os, json, time
from typing import List, Optional, Tuple, Union
from ddd_objects.infrastructure.repository_impl import RepositoryImpl
from ddd_objects.infrastructure.repository_impl import (
    RepositoryImpl, 
)
from ddd_objects.lib import Logger, get_md5
from .ao import K3SController
from .converter import(
    CommandResultConverter,
    ConditionConverter,
    InstanceInfoConverter,
    InstanceTypeWithStatusConverter,
    NodeInfoConverter,
)
from ..domain.repository import(
    K3SRepository,
)
from ..domain.entity import (
    Condition,
    InstanceInfo,
    InstanceTypeWithStatus,
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
    SecretUserSetting,
    Service
)
from ..domain.value_obj import (
    Key,
    Bool,
    Name,
    RegionID,
    Value,
    Path,
)
from .converter import (
    PodConverter,
    IngressConverter,
    NodeInfoConverter,
    ConditionConverter,
    NamespaceConverter,
    NodeUserSettingConverter,
    CommandResultConverter,
    NodeMetaConverter,
    SecretConverter,
    PodOSSOperationInfoConverter,
    ConfigMapConverter,
    DeploymentConverter,
    ConfigMapUserSettingConverter,
    SecretUserSettingConverter,
    ServiceConverter
)
from ..domain.repository import (
    K3SRepository
)
logger = Logger()
logger.set_labels(file_name=__file__)
condition_converter = ConditionConverter()
command_result_converter = CommandResultConverter()
node_info_converter = NodeInfoConverter()
config_map_user_setting_converter = ConfigMapUserSettingConverter()
node_user_setting_converter = NodeUserSettingConverter()
secret_user_setting_converter = SecretUserSettingConverter()
config_map_converter = ConfigMapConverter()
deployment_converter = DeploymentConverter()
namespace_converter = NamespaceConverter()
node_meta_converter = NodeMetaConverter()
pod_converter = PodConverter()
secret_converter = SecretConverter()
pod_oss_operation_info_converter = PodOSSOperationInfoConverter()
ingress_converter = IngressConverter()
service_converter = ServiceConverter()
instance_info_converter = InstanceInfoConverter()
instance_type_with_status_converter = InstanceTypeWithStatusConverter()


class K3SRepositoryImpl(K3SRepository, RepositoryImpl):
    def __init__(self, ip, port, token, log_func=None) -> None:
        self.ao = K3SController(ip, port, token)
        super().__init__(log_func=log_func)

    def check_connection(self, )->Optional[Bool]:
        result = self.ao.check_connection()
        if result.succeed:
            return Bool(result.get_value())
        else:
            self.log_func(result.error_traceback)
            return None

    def create_node(self, condition: Condition, node_user_setting: NodeUserSetting)->Optional[NodeInfo]:
        condition = condition_converter.to_do(condition)
        node_user_setting = node_user_setting_converter.to_do(node_user_setting)
        result = self.ao.create_node(condition, node_user_setting)
        if result.succeed:
            return node_info_converter.to_entity(result.get_value())
        else:
            self.log_func(result.error_traceback)
            return None

    def _get_existing_nodes(self, cluster_name: Name)->Optional[List[NodeInfo]]:
        cluster_name = cluster_name.get_value()
        result = self.ao.get_existing_nodes(cluster_name)
        if result.succeed:
            return [node_info_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_existing_nodes(self, cluster_name: Name)->Optional[List[NodeInfo]]:
        key = f'{cluster_name.get_value()}:existing_nodes'
        return self.find_entity_helper(
            self._get_existing_nodes,
            key=key,
            converter=None,
            cluster_name=cluster_name
        )

    def add_node_label(
        self, 
        node_infos: List[Union[NodeInfo, NodeMeta]], 
        key: Key, 
        value: Value
    )->Optional[List[CommandResult]]:
        node_infos = [
            node_info_converter.to_do(x) if isinstance(x, NodeInfo) 
            else node_meta_converter.to_do(x)
            for x in node_infos]
        key = key.get_value()
        value = value.get_value()
        result = self.ao.add_node_label(node_infos, key, value)
        if result.succeed:
            return [command_result_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def create_config_maps(self, cluster_name: Name, config_map_user_settings: List[ConfigMapUserSetting])->None:
        cluster_name = cluster_name.get_value()
        config_map_user_settings = [config_map_user_setting_converter.to_do(x) for x in config_map_user_settings]
        result = self.ao.create_config_maps(cluster_name, config_map_user_settings)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def create_namespace(self, cluster_name: Name, namespace_name: Name)->None:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.create_namespace(cluster_name, namespace_name)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def create_resource_from_oss(self, cluster_name: Name, target_paths: List[Path])->None:
        cluster_name = cluster_name.get_value()
        target_paths = [x.get_value() for x in target_paths]
        result = self.ao.create_resource_from_oss(cluster_name, target_paths)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def create_secrets(self, cluster_name: Name, secret_user_settings: List[SecretUserSetting])->bool:
        cluster_name = cluster_name.get_value()
        secret_user_settings = [secret_user_setting_converter.to_do(x) for x in secret_user_settings]
        result = self.ao.create_secrets(cluster_name, secret_user_settings)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def delete_nodes(self, node_infos: List[NodeInfo])->None:
        node_infos = [node_info_converter.to_do(x) for x in node_infos]
        result = self.ao.delete_nodes(node_infos)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def delete_resource_from_oss(self, cluster_name: Name, target_paths: List[Path])->None:
        cluster_name = cluster_name.get_value()
        target_paths = [x.get_value() for x in target_paths]
        result = self.ao.delete_resource_from_oss(cluster_name, target_paths)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def _get_config_maps(self, cluster_name: Name, namespace_name: Name)->Optional[List[ConfigMap]]:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.get_config_maps(cluster_name, namespace_name)
        if result.succeed:
            return [config_map_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_config_maps(self, cluster_name: Name, namespace_name: Name)->Optional[List[ConfigMap]]:
        key = f'{cluster_name.get_value()}:{namespace_name.get_value()}:config_maps'
        return self.find_entity_helper(
            self._get_config_maps,
            key=key,
            converter=None,
            cluster_name=cluster_name,
            namespace_name=namespace_name
        )

    def _get_deployments(self, cluster_name: Name, namespace_name: Name)->Optional[List[Deployment]]:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.get_deployments(cluster_name, namespace_name)
        if result.succeed:
            return [deployment_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_deployments(self, cluster_name: Name, namespace_name: Name)->Optional[List[Deployment]]:
        key = f'{cluster_name.get_value()}:{namespace_name.get_value()}:deployments'
        return self.find_entity_helper(
            self._get_deployments,
            key=key,
            converter=None,
            cluster_name=cluster_name,
            namespace_name=namespace_name
        )

    def _get_existing_nodes_by_name(self, node_name: Name)->Optional[List[NodeInfo]]:
        node_name = node_name.get_value()
        result = self.ao.get_existing_nodes_by_name(node_name)
        if result.succeed:
            return [node_info_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_existing_nodes_by_name(self, node_name: Name)->Optional[List[NodeInfo]]:
        key = f'{node_name.get_value()}:existing_nodes'
        return self.find_entity_helper(
            self._get_existing_nodes_by_name,
            key=key,
            converter=None,
            node_name=node_name
        )
    
    def _get_instance_info_by_node_meta(self, region_id: RegionID, node_meta: NodeMeta)->Tuple[Optional[InstanceInfo], Optional[InstanceTypeWithStatus]]:
        region_id = region_id.get_value()
        node_meta = node_meta_converter.to_do(node_meta)
        result = self.ao.get_instance_info_by_node_meta(region_id, node_meta)
        if result.succeed:
            instance_info, instance_type_info = result.get_value()
            instance_info = instance_info_converter.to_entity(instance_info)
            instance_type_info = instance_type_with_status_converter.to_entity(instance_type_info)
            return instance_info, instance_type_info
        else:
            self.log_func(result.error_traceback)
            return None, None

    def get_instance_info_by_node_meta(self, region_id: RegionID, node_meta: NodeMeta)->Tuple[Optional[InstanceInfo], Optional[InstanceTypeWithStatus]]:
        node_name = node_meta.name
        node_ip = node_meta.private_ip
        key = f'{region_id.get_value()}:{node_name.get_value()}:{node_ip.get_value}:instance_and_instance_type_info'
        return self.find_entity_helper(
            self._get_instance_info_by_node_meta,
            key=key,
            converter=None,
            region_id=region_id,
            node_meta=node_meta
        )

    def _get_namespaces(self, cluster_name: Name)->Optional[List[Namespace]]:
        cluster_name = cluster_name.get_value()
        result = self.ao.get_namespaces(cluster_name)
        if result.succeed:
            return [namespace_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_namespaces(self, cluster_name: Name)->Optional[List[Namespace]]:
        key = f'{cluster_name.get_value()}:namespaces'
        return self.find_entity_helper(
            self._get_namespaces,
            key=key,
            converter=None,
            cluster_name=cluster_name
        )

    def _get_node_metas(self, cluster_name: Name)->Optional[List[NodeMeta]]:
        cluster_name = cluster_name.get_value()
        result = self.ao.get_node_metas(cluster_name)
        if result.succeed:
            return [node_meta_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_node_metas(self, cluster_name: Name)->Optional[List[NodeMeta]]:
        key = f'{cluster_name.get_value()}:node_metas'
        return self.find_entity_helper(
            self._get_node_metas,
            key=key,
            converter=None,
            cluster_name=cluster_name
        )

    def _get_pods(self, cluster_name: Name, namespace_name: Name)->Optional[List[Pod]]:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.get_pods(cluster_name, namespace_name)
        if result.succeed:
            return [pod_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_pods(self, cluster_name: Name, namespace_name: Name)->Optional[List[Pod]]:
        key = f'{cluster_name.get_value()}:{namespace_name.get_value()}:pods'
        return self.find_entity_helper(
            self._get_pods,
            key=key,
            converter=None,
            cluster_name=cluster_name,
            namespace_name=namespace_name
        )

    def _get_secrets(self, cluster_name: Name, namespace_name: Name)->Optional[List[Secret]]:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.get_secrets(cluster_name, namespace_name)
        if result.succeed:
            return [secret_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_secrets(self, cluster_name: Name, namespace_name: Name)->Optional[List[Secret]]:
        key = f'{cluster_name.get_value()}:{namespace_name.get_value()}:secrets'
        return self.find_entity_helper(
            self._get_secrets,
            key=key,
            converter=None,
            cluster_name=cluster_name,
            namespace_name=namespace_name
        )

    def upload_to_oss_from_pod(self, pod_oss_operation_info: PodOSSOperationInfo)->None:
        pod_oss_operation_info = pod_oss_operation_info_converter.to_do(pod_oss_operation_info)
        result = self.ao.upload_to_oss_from_pod(pod_oss_operation_info)
        if result.succeed:
            return True
        else:
            self.log_func(result.error_traceback)
            return False

    def _get_ingresses(self, cluster_name: Name, namespace_name: Name)->Optional[List[Ingress]]:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.get_ingresses(cluster_name, namespace_name)
        if result.succeed:
            return [ingress_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_ingresses(self, cluster_name: Name, namespace_name: Name)->Optional[List[Ingress]]:
        key = f'{cluster_name.get_value()}:{namespace_name.get_value()}:ingresses'
        return self.find_entity_helper(
            self._get_ingresses,
            key=key,
            converter=None,
            cluster_name=cluster_name,
            namespace_name=namespace_name
        )

    def _get_services(self, cluster_name: Name, namespace_name: Name)->Optional[List[Service]]:
        cluster_name = cluster_name.get_value()
        namespace_name = namespace_name.get_value()
        result = self.ao.get_services(cluster_name, namespace_name)
        if result.succeed:
            return [service_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(result.error_traceback)
            return None

    def get_services(self, cluster_name: Name, namespace_name: Name)->Optional[List[Service]]:
        key = f'{cluster_name.get_value()}:{namespace_name.get_value()}:services'
        return self.find_entity_helper(
            self._get_services,
            key=key,
            converter=None,
            cluster_name=cluster_name,
            namespace_name=namespace_name
        )