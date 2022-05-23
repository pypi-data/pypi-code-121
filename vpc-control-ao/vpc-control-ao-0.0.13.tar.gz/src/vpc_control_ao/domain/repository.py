from typing import List, Optional
from ddd_objects.domain.repository import Repository
from .entity import(
    Condition,
    InstanceTypeUserSetting,
    InstanceTypeWithStatus,
    InstanceUsageInfo,
    InstanceUserSetting,
    InstanceInfo,
    OSSOperationInfo,
    CommandSetting,
    CommandResult
)
from .value_obj import(
    RegionID,
    Name
)
from ..domain.entity import (
    Condition,
    CommandResult,
    DNSRecord,
)
from ..domain.value_obj import (
    Name,
    DomainName,
    RecordID,
)


class VPCRepository(Repository):
    def new_instance(
        self, 
        condition: Condition, 
        setting: InstanceUserSetting
    )->List[InstanceInfo]:
        raise NotImplementedError

    def oss_operate(
        self, 
        instance_infos: List[InstanceInfo],
        oss_operation_info: OSSOperationInfo,
        command_setting: CommandSetting
    )->List[CommandResult]:
        raise NotImplementedError

    def run_command(
        self,
        instance_infos: List[InstanceInfo],
        command_setting: CommandSetting
    )->List[CommandResult]:
        raise NotImplementedError

    def get_instance_by_name(
        self,
        region_id: RegionID,
        name: Name
    )-> List[InstanceInfo]:
        raise NotImplementedError

    def release_instances(self, infos: List[InstanceInfo]):
        raise NotImplementedError

    def get_instance_type_status(
        self, 
        user_settings: List[InstanceTypeUserSetting],
    ) -> List[InstanceTypeWithStatus]:
        raise NotImplementedError

    def get_instance_usage(
        self,
        instance_infos: List[InstanceInfo]
    )->List[InstanceUsageInfo]:
        raise NotImplementedError


class DNSRepository(Repository):

    def create_dns_record(self, record: DNSRecord)->Optional[DNSRecord]:
        raise NotImplementedError

    def save_dns_record(self, record: DNSRecord)->Optional[DNSRecord]:
        raise NotImplementedError

    def delete_dns_record(self, record_id: RecordID)->None:
        raise NotImplementedError

    def get_dns_records(self, domain_name: DomainName)->Optional[List[DNSRecord]]:
        raise NotImplementedError

    def update_dns_record(self, record: Optional[List[DNSRecord]])->Optional[DNSRecord]:
        raise NotImplementedError

