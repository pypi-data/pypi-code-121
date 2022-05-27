from typing import List, Optional
from ddd_objects.domain.entity import Entity, ExpiredEntity
from .value_obj import (
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
    IngressHost,
    NodeName,
    Name,
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

class Condition(Entity):
    def __init__(
        self,
        min_cpu_num: Number,
        max_cpu_num: Number,
        min_memory_size: Size,
        max_memory_size: Size,
        min_gpu_num: Optional[Number] = None,
        max_gpu_num: Optional[Number] = None,
        min_gpu_memory_size: Optional[Size] = None,
        max_gpu_memory_size: Optional[Size] = None
    ):
        self.min_cpu_num=min_cpu_num
        self.max_cpu_num=max_cpu_num
        self.min_memory_size=min_memory_size
        self.max_memory_size=max_memory_size
        self.min_gpu_num=min_gpu_num
        self.max_gpu_num=max_gpu_num
        self.min_gpu_memory_size=min_gpu_memory_size
        self.max_gpu_memory_size=max_gpu_memory_size

class InstanceInfo(ExpiredEntity):
    def __init__(
        self,
        id: ID,
        status: Status,
        security_group_id: List[SecurityGroupID],
        instance_type: InstanceType,
        name: Name,
        hostname: Hostname,
        price: Price,
        image_id: ImageID,
        region_id: RegionID,
        zone_id: ZoneID,
        internet_pay_type: InternetPayType,
        pay_type: PayType,
        create_time: DateTime,
        os_name: Name,
        public_ip: List[IP],
        private_ip: IP,
        bandwidth_in: BandWidth,
        bandwidth_out: BandWidth,
        expired_time: DateTime,
        auto_release_time: DateTime,
        key_name: Name,
        _life_time: Number = Number(5)
    ):
        self.id=id
        self.status=status
        self.security_group_id=security_group_id
        self.instance_type=instance_type
        self.name=name
        self.hostname=hostname
        self.price=price
        self.image_id=image_id
        self.region_id=region_id
        self.zone_id=zone_id
        self.internet_pay_type=internet_pay_type
        self.pay_type=pay_type
        self.create_time=create_time
        self.os_name=os_name
        self.public_ip=public_ip
        self.private_ip=private_ip
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.expired_time=expired_time
        self.auto_release_time=auto_release_time
        self.key_name=key_name
        self._life_time=_life_time
        super().__init__(_life_time)

class InstanceUserSetting(Entity):
    def __init__(
        self,
        name: Name,
        password: Password,
        image_id: ImageID,
        region_id: RegionID,
        exclude_instance_types: List[InstanceType],
        user_data: Optional[Data] = None,
        internet_pay_type: Type = Type('PayByTraffic'),
        amount: Number = Number(1),
        bandwidth_in: BandWidth = BandWidth(200),
        bandwidth_out: BandWidth = BandWidth(1),
        disk_size: Size = Size(20),
        key_name: Name = Name('ansible'),
        inner_connection: Bool = Bool(True)
    ):
        self.name=name
        self.password=password
        self.image_id=image_id
        self.region_id=region_id
        self.exclude_instance_types=exclude_instance_types
        self.user_data=user_data
        self.internet_pay_type=internet_pay_type
        self.amount=amount
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.disk_size=disk_size
        self.key_name=key_name
        self.inner_connection=inner_connection

class CommandSetting(Entity):
    def __init__(
        self,
        command: Command = Command('echo 123'),
        forks: Number = Number(100),
        timeout: Number = Number(30),
        password: Password = None,
        username: Username = Username('root'),
        port: Port = Port(22),
        inner_connection: Bool = Bool(True)
    ):
        self.command=command
        self.forks=forks
        self.timeout=timeout
        self.password=password
        self.username=username
        self.port=port
        self.inner_connection=inner_connection

class CommandResult(Entity):
    def __init__(
        self,
        output: Output,
        instance_id: InstanceID,
        instance_name: InstanceName,
        ip: IP,
        succeed: Bool
    ):
        self.output=output
        self.instance_id=instance_id
        self.instance_name=instance_name
        self.ip=ip
        self.succeed=succeed

class OSSOperationInfo(Entity):
    def __init__(
        self,
        name: Name,
        endpoint: Endpoint,
        bucket_name: Name,
        local_path: Path,
        target_path: Path,
        with_tar: Bool = Bool(False)
    ):
        self.name=name
        self.endpoint=endpoint
        self.bucket_name=bucket_name
        self.local_path=local_path
        self.target_path=target_path
        self.with_tar=with_tar

class NodeUserSetting(Entity):
    def __init__(
        self,
        name: NodeName,
        k3s_token: Optional[Token] = None,
        region_id: RegionID = RegionID('cn-zhangjiakou'),
        disk_size: Size = Size(20),
        bandwidth_in: BandWidth = BandWidth(200),
        bandwidth_out: BandWidth = BandWidth(1),
        image_id: ImageID = ImageID('centos_8_5_x64_20G_alibase_20220303.vhd'),
        node_type: NodeType = NodeType('worker'),
        postfix: Bool = Bool(True),
        diff_instance_type: Bool = Bool(False),
        random_password: Bool = Bool(True),
        internet_pay_type: Type = Type('PayByTraffic'),
        master_ip: Optional[IP] = None,
        inner_connection: Bool = Bool(True)
    ):
        self.name=name
        self.k3s_token=k3s_token
        self.region_id=region_id
        self.disk_size=disk_size
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.image_id=image_id
        self.node_type=node_type
        self.postfix=postfix
        self.diff_instance_type=diff_instance_type
        self.random_password=random_password
        self.internet_pay_type=internet_pay_type
        self.master_ip=master_ip
        self.inner_connection=inner_connection

class NodeInfo(ExpiredEntity):
    def __init__(
        self,
        node_name: NodeName,
        node_type: NodeType,
        node_status: NodeStatus,
        instance_id: InstanceID,
        instance_type: InstanceType,
        hostname: Hostname,
        price: Price,
        image_id: ImageID,
        region_id: RegionID,
        zone_id: ZoneID,
        internet_pay_type: InternetPayType,
        pay_type: PayType,
        security_group_id: List[SecurityGroupID],
        node_label: NodeLabel,
        cpu_number: Number,
        cpu_usage: Usage,
        memory_size: Size,
        actual_memory_size: Size,
        memory_usage: Size,
        flow_in: Size,
        flow_out: Size,
        disk_size: Size,
        disk_usage: Usage,
        io_in: Number,
        io_out: Number,
        gpu_type: GPUType,
        gpu_number: Number,
        instance_type_status: InstanceTypeStatus,
        instance_type_status_category: InstanceTypeStatusCategory,
        instance_name: Name,
        instance_status: Status,
        instance_create_time: DateTime,
        os_name: Name,
        public_ip: List[IP],
        private_ip: IP,
        bandwidth_in: BandWidth,
        bandwidth_out: BandWidth,
        expired_time: DateTime,
        auto_release_time: DateTime,
        key_name: Name,
        run_time: Optional[Time] = None,
        k3s_version: Optional[Version] = None,
        _life_time: Number = Number(5)
    ):
        self.node_name=node_name
        self.node_type=node_type
        self.node_status=node_status
        self.instance_id=instance_id
        self.instance_type=instance_type
        self.hostname=hostname
        self.price=price
        self.image_id=image_id
        self.region_id=region_id
        self.zone_id=zone_id
        self.internet_pay_type=internet_pay_type
        self.pay_type=pay_type
        self.security_group_id=security_group_id
        self.node_label=node_label
        self.cpu_number=cpu_number
        self.cpu_usage=cpu_usage
        self.memory_size=memory_size
        self.actual_memory_size=actual_memory_size
        self.memory_usage=memory_usage
        self.flow_in=flow_in
        self.flow_out=flow_out
        self.disk_size=disk_size
        self.disk_usage=disk_usage
        self.io_in=io_in
        self.io_out=io_out
        self.gpu_type=gpu_type
        self.gpu_number=gpu_number
        self.instance_type_status=instance_type_status
        self.instance_type_status_category=instance_type_status_category
        self.instance_name=instance_name
        self.instance_status=instance_status
        self.instance_create_time=instance_create_time
        self.os_name=os_name
        self.public_ip=public_ip
        self.private_ip=private_ip
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.expired_time=expired_time
        self.auto_release_time=auto_release_time
        self.key_name=key_name
        self.run_time=run_time
        self.k3s_version=k3s_version
        self._life_time=_life_time
        super().__init__(_life_time)

class InstanceTypeWithStatus(ExpiredEntity):
    def __init__(
        self,
        region_id: RegionID,
        zone_id: ZoneID,
        instance_type_id: InstanceType,
        cpu_number: Number,
        memory_size: Size,
        gpu_type: GPUType,
        gpu_number: Number,
        status: InstanceTypeStatus,
        status_category: InstanceTypeStatusCategory,
        _life_time: Number = Number(5)
    ):
        self.region_id=region_id
        self.zone_id=zone_id
        self.instance_type_id=instance_type_id
        self.cpu_number=cpu_number
        self.memory_size=memory_size
        self.gpu_type=gpu_type
        self.gpu_number=gpu_number
        self.status=status
        self.status_category=status_category
        self._life_time=_life_time
        super().__init__(_life_time)

class InstanceTypeUserSetting(Entity):
    def __init__(
        self,
        region_id: RegionID,
        zone_id: ZoneID,
        instance_type_id: InstanceType
    ):
        self.region_id=region_id
        self.zone_id=zone_id
        self.instance_type_id=instance_type_id

class InstanceUsageInfo(ExpiredEntity):
    def __init__(
        self,
        instance_id: InstanceID,
        instance_name: InstanceName,
        cpu_number: Number,
        cpu_usage: Usage,
        memory_size: Size,
        memory_usage: Usage,
        flow_in: Size,
        flow_out: Size,
        disk_size: Size,
        disk_usage: Usage,
        io_in: Number,
        io_out: Number,
        _life_time: Number = Number(5)
    ):
        self.instance_id=instance_id
        self.instance_name=instance_name
        self.cpu_number=cpu_number
        self.cpu_usage=cpu_usage
        self.memory_size=memory_size
        self.memory_usage=memory_usage
        self.flow_in=flow_in
        self.flow_out=flow_out
        self.disk_size=disk_size
        self.disk_usage=disk_usage
        self.io_in=io_in
        self.io_out=io_out
        self._life_time=_life_time
        super().__init__(_life_time)

class NodeMeta(ExpiredEntity):
    def __init__(
        self,
        name: NodeName,
        status: NodeStatus,
        run_time: Time,
        k3s_version: Version,
        label: NodeLabel,
        private_ip: IP,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.status=status
        self.run_time=run_time
        self.k3s_version=k3s_version
        self.label=label
        self.private_ip=private_ip
        self._life_time=_life_time
        super().__init__(_life_time)

class Namespace(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        status: Status,
        age: TimeInterval,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.status=status
        self.age=age
        self._life_time=_life_time
        super().__init__(_life_time)

class Secret(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: TimeInterval,
        namespace: Name,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self._life_time=_life_time
        super().__init__(_life_time)

class ConfigMap(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: TimeInterval,
        namespace: Name,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self._life_time=_life_time
        super().__init__(_life_time)

class ConfigMapUserSetting(Entity):
    def __init__(
        self,
        name: Name,
        key: Key,
        value: Value,
        key_type: KeyType,
        namespace: Name
    ):
        self.name=name
        self.key=key
        self.value=value
        self.key_type=key_type
        self.namespace=namespace

class SecretUserSetting(Entity):
    def __init__(
        self,
        name: Name,
        key: Key,
        value: Value,
        namespace: Name
    ):
        self.name=name
        self.key=key
        self.value=value
        self.namespace=namespace

class Deployment(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: TimeInterval,
        namespace: Name,
        ready_info: Info,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self.ready_info=ready_info
        self._life_time=_life_time
        super().__init__(_life_time)

class Pod(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        node_name: NodeName,
        status: Status,
        age: TimeInterval,
        pod_ip: IP,
        namespace: Name,
        restarts: Number,
        readiness_info: Optional[Info],
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.node_name=node_name
        self.status=status
        self.age=age
        self.pod_ip=pod_ip
        self.namespace=namespace
        self.restarts=restarts
        self.readiness_info=readiness_info
        self._life_time=_life_time
        super().__init__(_life_time)

class PodOSSOperationInfo(Entity):
    def __init__(
        self,
        name: Name,
        cluster_name: Name,
        namespace_name: Name,
        pod_name: Name,
        container_name: Name,
        target_dir: Path,
        local_path: Path
    ):
        self.name=name
        self.cluster_name=cluster_name
        self.namespace_name=namespace_name
        self.pod_name=pod_name
        self.container_name=container_name
        self.target_dir=target_dir
        self.local_path=local_path

class ResourceOSSSetting(Entity):
    def __init__(
        self,
        cluster_name: Name,
        target_paths: List[Path]
    ):
        self.cluster_name=cluster_name
        self.target_paths=target_paths

class Ingress(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        host_info: Info,
        address_info: Info,
        port: Number,
        age: DateTime,
        namespace: Name,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.host_info=host_info
        self.address_info=address_info
        self.port=port
        self.age=age
        self.namespace=namespace
        self._life_time=_life_time
        super().__init__(_life_time)
    @property
    def hosts(self):
        return [IngressHost(h) for h in self.host_info.get_value().split(',')]
    
    @property
    def addresses(self):
        return [Value(a) for a in self.address_info.get_value().split(',')]

class DNSRecord(Entity):
    def __init__(
        self,
        domain_name: DomainName,
        subdomain: Subdomain,
        value: Value,
        id: Optional[RecordID] = None,
        weight: Optional[Weight] = None,
        dns_type: DNSType = DNSType('A'),
        ttl: Number = Number(600),
        priority: Optional[Number] = None,
        line: Optional[DNSLine] = None
    ):
        self.domain_name=domain_name
        self.subdomain=subdomain
        self.value=value
        self.id=id
        self.weight=weight
        self.dns_type=dns_type
        self.ttl=ttl
        self.priority=priority
        self.line=line

class Service(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        service_type: ServiceType,
        cluster_ip: IP,
        external_ip: Optional[IP],
        port_info: Info,
        age: DateTime,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.service_type=service_type
        self.cluster_ip=cluster_ip
        self.external_ip=external_ip
        self.port_info=port_info
        self.age=age
        self._life_time=_life_time
        super().__init__(_life_time)