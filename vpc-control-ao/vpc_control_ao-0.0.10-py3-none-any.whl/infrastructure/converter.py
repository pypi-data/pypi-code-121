from typing import List
from ddd_objects.infrastructure.converter import Converter
from ..domain.entity import (
    CommandSetting,
    InstanceTypeWithStatus,
    OSSOperationInfo,
    InstanceUserSetting,
    InstanceTypeUserSetting,
    DNSRecord,
    InstanceInfo,
    CommandResult,
    Condition
)
from ..domain.value_obj import (
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
from .do import (
    InstanceInfoDO,
    OSSOperationInfoDO,
    CommandResultDO,
    InstanceTypeUserSettingDO,
    CommandSettingDO,
    ConditionDO,
    InstanceTypeWithStatusDO,
    DNSRecordDO,
    InstanceUserSettingDO
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
