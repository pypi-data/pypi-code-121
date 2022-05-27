from typing import List
from ddd_objects.infrastructure.converter import Converter
from ..domain.entity import (
    Secret,
    InstanceUserSetting,
    PodOSSOperationInfo,
    NodeInfo,
    InstanceTypeUserSetting,
    OSSOperationInfo,
    Condition,
    InstanceTypeWithStatus,
    ConfigMapUserSetting,
    ResourceOSSSetting,
    NodeMeta,
    ConfigMap,
    Deployment,
    DNSRecord,
    NodeUserSetting,
    SecretUserSetting,
    Ingress,
    CommandSetting,
    Namespace,
    InstanceInfo,
    Service,
    CommandResult,
    Pod
)
from ..domain.value_obj import (
    InstanceTypeStatusCategory,
    TimeInterval,
    ServiceType,
    Status,
    InternetPayType,
    DomainName,
    Path,
    Key,
    Subdomain,
    NodeStatus,
    Version,
    Hostname,
    Output,
    Password,
    RecordID,
    Command,
    ZoneID,
    GPUType,
    Usage,
    NodeLabel,
    DNSLine,
    BandWidth,
    Weight,
    Endpoint,
    Name,
    NodeName,
    ImageID,
    Number,
    Size,
    InstanceType,
    DateTime,
    IP,
    Port,
    Value,
    ID,
    InstanceID,
    DNSType,
    Username,
    KeyType,
    InstanceName,
    SecurityGroupID,
    InstanceTypeStatus,
    RegionID,
    Bool,
    Data,
    Price,
    Type,
    Time,
    NodeType,
    Token,
    Info,
    PayType
)
from .do import (
    OSSOperationInfoDO,
    ResourceOSSSettingDO,
    InstanceInfoDO,
    InstanceUserSettingDO,
    NodeMetaDO,
    NodeInfoDO,
    CommandResultDO,
    ServiceDO,
    ConfigMapDO,
    ConditionDO,
    InstanceTypeUserSettingDO,
    DNSRecordDO,
    SecretUserSettingDO,
    ConfigMapUserSettingDO,
    CommandSettingDO,
    NodeUserSettingDO,
    NamespaceDO,
    PodOSSOperationInfoDO,
    SecretDO,
    PodDO,
    DeploymentDO,
    InstanceTypeWithStatusDO,
    IngressDO
)

class ConditionConverter(Converter):
    def to_entity(self, do: ConditionDO):
        return Condition(
            min_cpu_num = Number(do.min_cpu_num),
            max_cpu_num = Number(do.max_cpu_num),
            min_memory_size = Size(do.min_memory_size),
            max_memory_size = Size(do.max_memory_size),
            min_gpu_num = Number(do.min_gpu_num),
            max_gpu_num = Number(do.max_gpu_num),
            min_gpu_memory_size = Size(do.min_gpu_memory_size),
            max_gpu_memory_size = Size(do.max_gpu_memory_size)
        )
    def to_do(self, x: Condition):
        return ConditionDO(
            min_cpu_num = None if x.min_cpu_num is None else x.min_cpu_num.get_value(),
            max_cpu_num = None if x.max_cpu_num is None else x.max_cpu_num.get_value(),
            min_memory_size = None if x.min_memory_size is None else x.min_memory_size.get_value(),
            max_memory_size = None if x.max_memory_size is None else x.max_memory_size.get_value(),
            min_gpu_num = None if x.min_gpu_num is None else x.min_gpu_num.get_value(),
            max_gpu_num = None if x.max_gpu_num is None else x.max_gpu_num.get_value(),
            min_gpu_memory_size = None if x.min_gpu_memory_size is None else x.min_gpu_memory_size.get_value(),
            max_gpu_memory_size = None if x.max_gpu_memory_size is None else x.max_gpu_memory_size.get_value()
        )

class CommandResultConverter(Converter):
    def to_entity(self, do: CommandResultDO):
        return CommandResult(
            output = Output(do.output),
            instance_id = InstanceID(do.instance_id),
            instance_name = InstanceName(do.instance_name),
            ip = IP(do.ip),
            succeed = Bool(do.succeed)
        )
    def to_do(self, x: CommandResult):
        return CommandResultDO(
            output = None if x.output is None else x.output.get_value(),
            instance_id = None if x.instance_id is None else x.instance_id.get_value(),
            instance_name = None if x.instance_name is None else x.instance_name.get_value(),
            ip = None if x.ip is None else x.ip.get_value(),
            succeed = None if x.succeed is None else x.succeed.get_value()
        )

class NodeUserSettingConverter(Converter):
    def to_entity(self, do: NodeUserSettingDO):
        return NodeUserSetting(
            name = NodeName(do.name),
            k3s_token = Token(do.k3s_token),
            region_id = RegionID(do.region_id),
            disk_size = Size(do.disk_size),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            image_id = ImageID(do.image_id),
            node_type = NodeType(do.node_type),
            postfix = Bool(do.postfix),
            diff_instance_type = Bool(do.diff_instance_type),
            random_password = Bool(do.random_password),
            internet_pay_type = Type(do.internet_pay_type),
            master_ip = IP(do.master_ip),
            inner_connection = Bool(do.inner_connection)
        )
    def to_do(self, x: NodeUserSetting):
        return NodeUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            k3s_token = None if x.k3s_token is None else x.k3s_token.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            disk_size = None if x.disk_size is None else x.disk_size.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            node_type = None if x.node_type is None else x.node_type.get_value(),
            postfix = None if x.postfix is None else x.postfix.get_value(),
            diff_instance_type = None if x.diff_instance_type is None else x.diff_instance_type.get_value(),
            random_password = None if x.random_password is None else x.random_password.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            master_ip = None if x.master_ip is None else x.master_ip.get_value(),
            inner_connection = None if x.inner_connection is None else x.inner_connection.get_value()
        )

class NamespaceConverter(Converter):
    def to_entity(self, do: NamespaceDO):
        return Namespace(
            name = Name(do.name),
            status = Status(do.status),
            age = TimeInterval(do.age),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Namespace):
        return NamespaceDO(
            name = None if x.name is None else x.name.get_value(),
            status = None if x.status is None else x.status.get_value(),
            age = None if x.age is None else x.age.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class SecretConverter(Converter):
    def to_entity(self, do: SecretDO):
        return Secret(
            name = Name(do.name),
            age = TimeInterval(do.age),
            namespace = Name(do.namespace),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Secret):
        return SecretDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class ConfigMapConverter(Converter):
    def to_entity(self, do: ConfigMapDO):
        return ConfigMap(
            name = Name(do.name),
            age = TimeInterval(do.age),
            namespace = Name(do.namespace),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: ConfigMap):
        return ConfigMapDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class ConfigMapUserSettingConverter(Converter):
    def to_entity(self, do: ConfigMapUserSettingDO):
        return ConfigMapUserSetting(
            name = Name(do.name),
            key = Key(do.key),
            value = Value(do.value),
            key_type = KeyType(do.key_type),
            namespace = Name(do.namespace)
        )
    def to_do(self, x: ConfigMapUserSetting):
        return ConfigMapUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            key = None if x.key is None else x.key.get_value(),
            value = None if x.value is None else x.value.get_value(),
            key_type = None if x.key_type is None else x.key_type.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value()
        )

class SecretUserSettingConverter(Converter):
    def to_entity(self, do: SecretUserSettingDO):
        return SecretUserSetting(
            name = Name(do.name),
            key = Key(do.key),
            value = Value(do.value),
            namespace = Name(do.namespace)
        )
    def to_do(self, x: SecretUserSetting):
        return SecretUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            key = None if x.key is None else x.key.get_value(),
            value = None if x.value is None else x.value.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value()
        )

class DeploymentConverter(Converter):
    def to_entity(self, do: DeploymentDO):
        return Deployment(
            name = Name(do.name),
            age = TimeInterval(do.age),
            namespace = Name(do.namespace),
            ready_info = Info(do.ready_info),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Deployment):
        return DeploymentDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            ready_info = None if x.ready_info is None else x.ready_info.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class PodConverter(Converter):
    def to_entity(self, do: PodDO):
        return Pod(
            name = Name(do.name),
            node_name = NodeName(do.node_name),
            status = Status(do.status),
            age = TimeInterval(do.age),
            pod_ip = IP(do.pod_ip),
            namespace = Name(do.namespace),
            restarts = Number(do.restarts),
            readiness_info = Info(do.readiness_info),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Pod):
        return PodDO(
            name = None if x.name is None else x.name.get_value(),
            node_name = None if x.node_name is None else x.node_name.get_value(),
            status = None if x.status is None else x.status.get_value(),
            age = None if x.age is None else x.age.get_value(),
            pod_ip = None if x.pod_ip is None else x.pod_ip.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            restarts = None if x.restarts is None else x.restarts.get_value(),
            readiness_info = None if x.readiness_info is None else x.readiness_info.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class PodOSSOperationInfoConverter(Converter):
    def to_entity(self, do: PodOSSOperationInfoDO):
        return PodOSSOperationInfo(
            name = Name(do.name),
            cluster_name = Name(do.cluster_name),
            namespace_name = Name(do.namespace_name),
            pod_name = Name(do.pod_name),
            container_name = Name(do.container_name),
            target_dir = Path(do.target_dir),
            local_path = Path(do.local_path)
        )
    def to_do(self, x: PodOSSOperationInfo):
        return PodOSSOperationInfoDO(
            name = None if x.name is None else x.name.get_value(),
            cluster_name = None if x.cluster_name is None else x.cluster_name.get_value(),
            namespace_name = None if x.namespace_name is None else x.namespace_name.get_value(),
            pod_name = None if x.pod_name is None else x.pod_name.get_value(),
            container_name = None if x.container_name is None else x.container_name.get_value(),
            target_dir = None if x.target_dir is None else x.target_dir.get_value(),
            local_path = None if x.local_path is None else x.local_path.get_value()
        )

class ResourceOSSSettingConverter(Converter):
    def to_entity(self, do: ResourceOSSSettingDO):
        return ResourceOSSSetting(
            cluster_name = Name(do.cluster_name),
            target_paths = [Path(m) for m in do.target_paths]
        )
    def to_do(self, x: ResourceOSSSetting):
        return ResourceOSSSettingDO(
            cluster_name = None if x.cluster_name is None else x.cluster_name.get_value(),
            target_paths = None if x.target_paths is None else [m.get_value() for m in x.target_paths]
        )

class NodeInfoConverter(Converter):
    def to_entity(self, do: NodeInfoDO):
        return NodeInfo(
            node_name = NodeName(do.node_name),
            node_type = NodeType(do.node_type),
            node_status = NodeStatus(do.node_status),
            instance_id = InstanceID(do.instance_id),
            instance_type = InstanceType(do.instance_type),
            hostname = Hostname(do.hostname),
            price = Price(do.price),
            image_id = ImageID(do.image_id),
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            internet_pay_type = InternetPayType(do.internet_pay_type),
            pay_type = PayType(do.pay_type),
            security_group_id = [SecurityGroupID(m) for m in do.security_group_id],
            node_label = NodeLabel(do.node_label),
            cpu_number = Number(do.cpu_number),
            cpu_usage = Usage(do.cpu_usage),
            memory_size = Size(do.memory_size),
            actual_memory_size = Size(do.actual_memory_size),
            memory_usage = Size(do.memory_usage),
            flow_in = Size(do.flow_in),
            flow_out = Size(do.flow_out),
            disk_size = Size(do.disk_size),
            disk_usage = Usage(do.disk_usage),
            io_in = Number(do.io_in),
            io_out = Number(do.io_out),
            gpu_type = GPUType(do.gpu_type),
            gpu_number = Number(do.gpu_number),
            instance_type_status = InstanceTypeStatus(do.instance_type_status),
            instance_type_status_category = InstanceTypeStatusCategory(do.instance_type_status_category),
            instance_name = Name(do.instance_name),
            instance_status = Status(do.instance_status),
            instance_create_time = DateTime(do.instance_create_time),
            os_name = Name(do.os_name),
            public_ip = [IP(m) for m in do.public_ip],
            private_ip = IP(do.private_ip),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            expired_time = DateTime(do.expired_time),
            auto_release_time = DateTime(do.auto_release_time),
            key_name = Name(do.key_name),
            run_time = Time(do.run_time),
            k3s_version = Version(do.k3s_version),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: NodeInfo):
        return NodeInfoDO(
            node_name = None if x.node_name is None else x.node_name.get_value(),
            node_type = None if x.node_type is None else x.node_type.get_value(),
            node_status = None if x.node_status is None else x.node_status.get_value(),
            instance_id = None if x.instance_id is None else x.instance_id.get_value(),
            instance_type = None if x.instance_type is None else x.instance_type.get_value(),
            hostname = None if x.hostname is None else x.hostname.get_value(),
            price = None if x.price is None else x.price.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            pay_type = None if x.pay_type is None else x.pay_type.get_value(),
            security_group_id = None if x.security_group_id is None else [m.get_value() for m in x.security_group_id],
            node_label = None if x.node_label is None else x.node_label.get_value(),
            cpu_number = None if x.cpu_number is None else x.cpu_number.get_value(),
            cpu_usage = None if x.cpu_usage is None else x.cpu_usage.get_value(),
            memory_size = None if x.memory_size is None else x.memory_size.get_value(),
            actual_memory_size = None if x.actual_memory_size is None else x.actual_memory_size.get_value(),
            memory_usage = None if x.memory_usage is None else x.memory_usage.get_value(),
            flow_in = None if x.flow_in is None else x.flow_in.get_value(),
            flow_out = None if x.flow_out is None else x.flow_out.get_value(),
            disk_size = None if x.disk_size is None else x.disk_size.get_value(),
            disk_usage = None if x.disk_usage is None else x.disk_usage.get_value(),
            io_in = None if x.io_in is None else x.io_in.get_value(),
            io_out = None if x.io_out is None else x.io_out.get_value(),
            gpu_type = None if x.gpu_type is None else x.gpu_type.get_value(),
            gpu_number = None if x.gpu_number is None else x.gpu_number.get_value(),
            instance_type_status = None if x.instance_type_status is None else x.instance_type_status.get_value(),
            instance_type_status_category = None if x.instance_type_status_category is None else x.instance_type_status_category.get_value(),
            instance_name = None if x.instance_name is None else x.instance_name.get_value(),
            instance_status = None if x.instance_status is None else x.instance_status.get_value(),
            instance_create_time = None if x.instance_create_time is None else x.instance_create_time.get_value(),
            os_name = None if x.os_name is None else x.os_name.get_value(),
            public_ip = None if x.public_ip is None else [m.get_value() for m in x.public_ip],
            private_ip = None if x.private_ip is None else x.private_ip.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            expired_time = None if x.expired_time is None else x.expired_time.get_value(),
            auto_release_time = None if x.auto_release_time is None else x.auto_release_time.get_value(),
            key_name = None if x.key_name is None else x.key_name.get_value(),
            run_time = None if x.run_time is None else x.run_time.get_value(),
            k3s_version = None if x.k3s_version is None else x.k3s_version.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class NodeMetaConverter(Converter):
    def to_entity(self, do: NodeMetaDO):
        return NodeMeta(
            name = NodeName(do.name),
            status = NodeStatus(do.status),
            run_time = Time(do.run_time),
            k3s_version = Version(do.k3s_version),
            label = NodeLabel(do.label),
            private_ip = IP(do.private_ip),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: NodeMeta):
        return NodeMetaDO(
            name = None if x.name is None else x.name.get_value(),
            status = None if x.status is None else x.status.get_value(),
            run_time = None if x.run_time is None else x.run_time.get_value(),
            k3s_version = None if x.k3s_version is None else x.k3s_version.get_value(),
            label = None if x.label is None else x.label.get_value(),
            private_ip = None if x.private_ip is None else x.private_ip.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class IngressConverter(Converter):
    def to_entity(self, do: IngressDO):
        return Ingress(
            name = Name(do.name),
            host_info = Info(do.host_info),
            address_info = Info(do.address_info),
            port = Number(do.port),
            age = DateTime(do.age),
            namespace = Name(do.namespace),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Ingress):
        return IngressDO(
            name = None if x.name is None else x.name.get_value(),
            host_info = None if x.host_info is None else x.host_info.get_value(),
            address_info = None if x.address_info is None else x.address_info.get_value(),
            port = None if x.port is None else x.port.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class InstanceInfoConverter(Converter):
    def to_entity(self, do: InstanceInfoDO):
        return InstanceInfo(
            id = ID(do.id),
            status = Status(do.status),
            security_group_id = [SecurityGroupID(m) for m in do.security_group_id],
            instance_type = InstanceType(do.instance_type),
            name = Name(do.name),
            hostname = Hostname(do.hostname),
            price = Price(do.price),
            image_id = ImageID(do.image_id),
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            internet_pay_type = InternetPayType(do.internet_pay_type),
            pay_type = PayType(do.pay_type),
            create_time = DateTime(do.create_time),
            os_name = Name(do.os_name),
            public_ip = [IP(m) for m in do.public_ip],
            private_ip = IP(do.private_ip),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            expired_time = DateTime(do.expired_time),
            auto_release_time = DateTime(do.auto_release_time),
            key_name = Name(do.key_name),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: InstanceInfo):
        return InstanceInfoDO(
            id = None if x.id is None else x.id.get_value(),
            status = None if x.status is None else x.status.get_value(),
            security_group_id = None if x.security_group_id is None else [m.get_value() for m in x.security_group_id],
            instance_type = None if x.instance_type is None else x.instance_type.get_value(),
            name = None if x.name is None else x.name.get_value(),
            hostname = None if x.hostname is None else x.hostname.get_value(),
            price = None if x.price is None else x.price.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            pay_type = None if x.pay_type is None else x.pay_type.get_value(),
            create_time = None if x.create_time is None else x.create_time.get_value(),
            os_name = None if x.os_name is None else x.os_name.get_value(),
            public_ip = None if x.public_ip is None else [m.get_value() for m in x.public_ip],
            private_ip = None if x.private_ip is None else x.private_ip.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            expired_time = None if x.expired_time is None else x.expired_time.get_value(),
            auto_release_time = None if x.auto_release_time is None else x.auto_release_time.get_value(),
            key_name = None if x.key_name is None else x.key_name.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class InstanceUserSettingConverter(Converter):
    def to_entity(self, do: InstanceUserSettingDO):
        return InstanceUserSetting(
            name = Name(do.name),
            password = Password(do.password),
            image_id = ImageID(do.image_id),
            region_id = RegionID(do.region_id),
            exclude_instance_types = [InstanceType(m) for m in do.exclude_instance_types],
            user_data = Data(do.user_data),
            internet_pay_type = Type(do.internet_pay_type),
            amount = Number(do.amount),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            disk_size = Size(do.disk_size),
            key_name = Name(do.key_name),
            inner_connection = Bool(do.inner_connection)
        )
    def to_do(self, x: InstanceUserSetting):
        return InstanceUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            password = None if x.password is None else x.password.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            exclude_instance_types = None if x.exclude_instance_types is None else [m.get_value() for m in x.exclude_instance_types],
            user_data = None if x.user_data is None else x.user_data.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            amount = None if x.amount is None else x.amount.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            disk_size = None if x.disk_size is None else x.disk_size.get_value(),
            key_name = None if x.key_name is None else x.key_name.get_value(),
            inner_connection = None if x.inner_connection is None else x.inner_connection.get_value()
        )

class CommandSettingConverter(Converter):
    def to_entity(self, do: CommandSettingDO):
        return CommandSetting(
            command = Command(do.command),
            forks = Number(do.forks),
            timeout = Number(do.timeout),
            password = Password(do.password),
            username = Username(do.username),
            port = Port(do.port),
            inner_connection = Bool(do.inner_connection)
        )
    def to_do(self, x: CommandSetting):
        return CommandSettingDO(
            command = None if x.command is None else x.command.get_value(),
            forks = None if x.forks is None else x.forks.get_value(),
            timeout = None if x.timeout is None else x.timeout.get_value(),
            password = None if x.password is None else x.password.get_value(),
            username = None if x.username is None else x.username.get_value(),
            port = None if x.port is None else x.port.get_value(),
            inner_connection = None if x.inner_connection is None else x.inner_connection.get_value()
        )

class OSSOperationInfoConverter(Converter):
    def to_entity(self, do: OSSOperationInfoDO):
        return OSSOperationInfo(
            name = Name(do.name),
            endpoint = Endpoint(do.endpoint),
            bucket_name = Name(do.bucket_name),
            local_path = Path(do.local_path),
            target_path = Path(do.target_path),
            with_tar = Bool(do.with_tar)
        )
    def to_do(self, x: OSSOperationInfo):
        return OSSOperationInfoDO(
            name = None if x.name is None else x.name.get_value(),
            endpoint = None if x.endpoint is None else x.endpoint.get_value(),
            bucket_name = None if x.bucket_name is None else x.bucket_name.get_value(),
            local_path = None if x.local_path is None else x.local_path.get_value(),
            target_path = None if x.target_path is None else x.target_path.get_value(),
            with_tar = None if x.with_tar is None else x.with_tar.get_value()
        )

class InstanceTypeWithStatusConverter(Converter):
    def to_entity(self, do: InstanceTypeWithStatusDO):
        return InstanceTypeWithStatus(
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            instance_type_id = InstanceType(do.instance_type_id),
            cpu_number = Number(do.cpu_number),
            memory_size = Size(do.memory_size),
            gpu_type = GPUType(do.gpu_type),
            gpu_number = Number(do.gpu_number),
            status = InstanceTypeStatus(do.status),
            status_category = InstanceTypeStatusCategory(do.status_category),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: InstanceTypeWithStatus):
        return InstanceTypeWithStatusDO(
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            instance_type_id = None if x.instance_type_id is None else x.instance_type_id.get_value(),
            cpu_number = None if x.cpu_number is None else x.cpu_number.get_value(),
            memory_size = None if x.memory_size is None else x.memory_size.get_value(),
            gpu_type = None if x.gpu_type is None else x.gpu_type.get_value(),
            gpu_number = None if x.gpu_number is None else x.gpu_number.get_value(),
            status = None if x.status is None else x.status.get_value(),
            status_category = None if x.status_category is None else x.status_category.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class InstanceTypeUserSettingConverter(Converter):
    def to_entity(self, do: InstanceTypeUserSettingDO):
        return InstanceTypeUserSetting(
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            instance_type_id = InstanceType(do.instance_type_id)
        )
    def to_do(self, x: InstanceTypeUserSetting):
        return InstanceTypeUserSettingDO(
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            instance_type_id = None if x.instance_type_id is None else x.instance_type_id.get_value()
        )

class DNSRecordConverter(Converter):
    def to_entity(self, do: DNSRecordDO):
        return DNSRecord(
            domain_name = DomainName(do.domain_name),
            subdomain = Subdomain(do.subdomain),
            value = Value(do.value),
            id = RecordID(do.id),
            weight = Weight(do.weight),
            dns_type = DNSType(do.dns_type),
            ttl = Number(do.ttl),
            priority = Number(do.priority),
            line = DNSLine(do.line)
        )
    def to_do(self, x: DNSRecord):
        return DNSRecordDO(
            domain_name = None if x.domain_name is None else x.domain_name.get_value(),
            subdomain = None if x.subdomain is None else x.subdomain.get_value(),
            value = None if x.value is None else x.value.get_value(),
            id = None if x.id is None else x.id.get_value(),
            weight = None if x.weight is None else x.weight.get_value(),
            dns_type = None if x.dns_type is None else x.dns_type.get_value(),
            ttl = None if x.ttl is None else x.ttl.get_value(),
            priority = None if x.priority is None else x.priority.get_value(),
            line = None if x.line is None else x.line.get_value()
        )

class ServiceConverter(Converter):
    def to_entity(self, do: ServiceDO):
        return Service(
            name = Name(do.name),
            service_type = ServiceType(do.service_type),
            cluster_ip = IP(do.cluster_ip),
            external_ip = IP(do.external_ip),
            port_info = Info(do.port_info),
            age = DateTime(do.age),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Service):
        return ServiceDO(
            name = None if x.name is None else x.name.get_value(),
            service_type = None if x.service_type is None else x.service_type.get_value(),
            cluster_ip = None if x.cluster_ip is None else x.cluster_ip.get_value(),
            external_ip = None if x.external_ip is None else x.external_ip.get_value(),
            port_info = None if x.port_info is None else x.port_info.get_value(),
            age = None if x.age is None else x.age.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )