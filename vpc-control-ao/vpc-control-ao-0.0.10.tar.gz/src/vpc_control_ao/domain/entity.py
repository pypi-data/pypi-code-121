from typing import List, Optional
from ddd_objects.domain.entity import Entity, ExpiredEntity
from .value_obj import (
    Port,
    Weight,
    InstanceType,
    Number,
    Status,
    Path,
    Password,
    GPUType,
    Name,
    Hostname,
    RecordID,
    InternetPayType,
    InstanceID,
    RegionID,
    Usage,
    BandWidth,
    Type,
    ID,
    IP,
    DNSLine,
    Value,
    SecurityGroupID,
    Output,
    DomainName,
    InstanceName,
    Price,
    ImageID,
    PayType,
    Size,
    Command,
    Subdomain,
    Endpoint,
    Data,
    Bool,
    Username,
    InstanceTypeStatusCategory,
    DateTime,
    DNSType,
    InstanceTypeStatus,
    ZoneID
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
        _life_time: Number = Number(30)
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

    def __eq__(self, __o: object) -> bool:
        if self.domain_name==__o.domain_name and self.subdomain==__o.subdomain \
            and self.value==__o.value  \
            and self.dns_type==__o.dns_type and self.ttl==__o.ttl \
            and (self.priority==__o.priority \
            or all(x in [Number(None), None] for x in [self.priority, __o.priority])) \
            and (self.weight==__o.weight \
            or all(x in [Weight(1), None] for x in [self.weight, __o.weight])) \
            and (self.line==__o.line \
            or all(x in [DNSLine('default'), None] for x in [self.line, __o.line])):
            return True
        else:
            return False