import os, json
from typing import List, Optional
from ddd_objects.infrastructure.repository_impl import RepositoryImpl
from ddd_objects.infrastructure.repository_impl import (
    RepositoryImpl, 
    return_list, 
    default_log_fun,
)
from ddd_objects.infrastructure.ao import exception_class_dec
from ddd_objects.domain.exception import NotExistsError, ParameterError, OperationError, ValueError
from ddd_objects.lib import Logger, get_md5
from ..domain.repository import VPCRepository
from .ao import VPCController
from .converter import(
    CommandResultConverter,
    CommandSettingConverter,
    ConditionConverter,
    InstanceInfoConverter,
    InstanceTypeUserSettingConverter,
    InstanceTypeWithStatusConverter,
    InstanceUserSettingConverter,
    OSSOperationInfoConverter
)
from ..domain.entity import(
    CommandResult,
    CommandSetting,
    Condition,
    InstanceInfo,
    InstanceTypeUserSetting,
    InstanceTypeWithStatus,
    InstanceUsageInfo,
    InstanceUserSetting,
    OSSOperationInfo
)
logger = Logger()
logger.set_labels(file_name=__file__)
from ..domain.entity import (
    Condition,
    CommandResult,
    DNSRecord,
)
from ..domain.value_obj import (
    DomainName,
    RecordID,
    Subdomain,
    Usage,
    Name,
    Number,
    Command,
    RegionID,
    Size
)
from .converter import (
    DNSRecordConverter,
    ConditionConverter,
    CommandResultConverter,
)
from ..domain.repository import (
    DNSRepository
)
instance_info_converter = InstanceInfoConverter()
condition_converter = ConditionConverter()
instance_user_setting_converter = InstanceUserSettingConverter()
oss_operation_info_converter = OSSOperationInfoConverter()
command_setting_converter = CommandSettingConverter()
command_result_converter = CommandResultConverter()
instance_type_status_converter = InstanceTypeWithStatusConverter()
instance_type_user_converter = InstanceTypeUserSettingConverter()
dns_record_converter = DNSRecordConverter()


class VPCRepositoryImpl(VPCRepository, RepositoryImpl):
    def __init__(self, ip, port, token, log_func=None):
        self.ao = VPCController(ip, port, token)
        super().__init__(log_func=log_func)

    def _extract_cpu_usage_info(self, result_output:str):
        lines = result_output.split('\n')
        values = [v for v in lines[0].split(' ') if v]
        cpu_num = values[-2].split('\t')[-1].replace('(', '').strip()
        cpu_free = [v for v in lines[3].split(' ') if v][-1]
        _, _, io_out, io_in, _, _ = [v for v in lines[6].split(' ') if v]
        cpu_usage = 1-float(cpu_free)/100
        return int(cpu_num), cpu_usage, float(io_in), float(io_out)

    def _extract_memory_usage_info(self, result_output: str):
        lines = result_output.split('\n')
        _, total, usage, _, _, _, _ = [v for v in lines[1].split(' ') if v]
        return total, usage

    def _extract_flow_info(self, result_output: str):
        lines = result_output.split('\n')
        line = [line for line in lines if line.startswith('eth')][0]
        _, _, _, _, _, _, flow_in, _, flow_out = [v for v in line.split(' ') if v]
        flow_in = flow_in.replace('K', '000')
        flow_out = flow_out.replace('K', '000')
        flow_in = flow_in.replace('M', '000000')
        flow_out = flow_out.replace('M', '000000')
        flow_in = flow_in.replace('G', '000000000')
        flow_out = flow_out.replace('G', '000000000')
        return float(flow_in)/1000, float(flow_out)/1000

    def _extract_disk_info(self, result_output: str):
        lines = result_output.split('\n')
        line = [line for line in lines 
            if line.startswith('/dev/vda') and line.strip().endswith('/')][0]
        _, size, used, avail, usage, _ = [v for v in line.split(' ') if v]
        size = int(size[:-1])
        usage = float(usage[:-1])/100
        return size, usage

    @return_list(log_func=default_log_fun, return_raw=True)
    @exception_class_dec(max_try=1)
    def new_instance(
        self, 
        condition: Condition, 
        setting: InstanceUserSetting,
        force: bool = False
    ) -> List[InstanceInfo]:
        if not force:
            region_id = setting.region_id.get_value()
            name = setting.name.get_value()
            _result = self.ao.get_instance_by_name(region_id, name)
            if _result.succeed:
                infos = _result.get_value()
            else:
                self.log_func('Fail to fetch existing instance infos when creating instance')
                self.log_func(_result.error_traceback)
                return None
            if infos:
                return infos
        condition = condition_converter.to_do(condition)
        setting = instance_user_setting_converter.to_do(setting)
        _result = self.ao.new_instance(condition, setting)
        if _result.succeed:
            instance_infos = _result.get_value()
            if instance_infos:
                return [instance_info_converter.to_entity(info) for info in instance_infos]
            else:
                return None
        else:
            self.log_func('Fail to creating instance')
            self.log_func(_result.error_traceback)
            return None

    @return_list(log_func=default_log_fun, return_raw=True)
    @exception_class_dec()
    def oss_operate(
        self, 
        instance_infos:List[InstanceInfo], 
        oss_operation_info: OSSOperationInfo,
        command_setting: CommandSetting
    ) -> List[CommandResult]:
        instance_infos = [instance_info_converter.to_do(info) for info in instance_infos]
        oss_operation_info = oss_operation_info_converter.to_do(oss_operation_info)
        command_setting = command_setting_converter.to_do(command_setting)
        result = self.ao.oss_operate(instance_infos, oss_operation_info, command_setting)
        if result.succeed:
            return [command_result_converter.to_entity(r) for r in result.get_value()]
        else:
            self.log_func('Fail to operate oss')
            self.log_func(result.error_traceback)
            return None

    @return_list(log_func=default_log_fun, return_raw=True)
    @exception_class_dec()
    def run_command(
        self,
        instance_infos: List[InstanceInfo],
        command_setting: CommandSetting
    ) -> List[CommandResult]:
        instance_infos = [instance_info_converter.to_do(info) for info in instance_infos]
        command_setting = command_setting_converter.to_do(command_setting)
        _result = self.ao.run_command(instance_infos, command_setting)
        if _result.succeed:
            results = _result.get_value()
            return [command_result_converter.to_entity(r) if r else None for r in results]
        else:
            self.log_func(f'Fail to run command: {command_setting.command}')
            self.log_func(_result.error_traceback)
            return None

    def _get_instance_by_name(self, region_id: RegionID, name: Name) -> List[InstanceInfo]:
        region_id = region_id.get_value()
        name = name.get_value()
        result = self.ao.get_instance_by_name(region_id, name)
        if result.succeed:
            return [instance_info_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(f'Fail to fetch instance info')
            self.log_func(result.error_traceback)
            return None

    def get_instance_by_name(self, region_id: RegionID, name: Name) -> List[InstanceInfo]:
        key = f'{region_id.get_value()}:{name.get_value()}:instances'
        return self.find_entity_helper(
            self._get_instance_by_name,
            key,
            converter=None,
            force_update=False,
            verbose = False,
            region_id=region_id,
            name = name
        )

    def _get_instance_type_status(
        self, 
        user_settings: List[InstanceTypeUserSetting],
    ) -> List[InstanceTypeWithStatus]:
        user_settings = [instance_type_user_converter.to_do(x) for x in user_settings]
        result = self.ao.get_instance_type_status(user_settings)
        if result.succeed:
            return [instance_type_status_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(f'Fail to fetch instance type status info')
            self.log_func(result.error_traceback)
            return None

    def get_instance_type_status(
        self, 
        user_settings: List[InstanceTypeUserSetting],
    ) -> List[InstanceTypeWithStatus]:
        region_ids = [setting.region_id.get_value() for setting in user_settings]
        zone_ids = [setting.zone_id.get_value() for setting in user_settings]
        instance_types = [setting.instance_type_id.get_value() for setting in user_settings]
        region_ids_string = ''.join(region_ids)
        zone_ids_string = ''.join(zone_ids)
        instance_types_string = ''.join(instance_types)
        key = f'{get_md5(region_ids_string)}:{get_md5(zone_ids_string)}:{get_md5(instance_types_string)}'
        return self.find_entity_helper(
            self._get_instance_type_status,
            key,
            converter=None,
            user_settings=user_settings
        )

    def _get_instance_usage(
        self,
        instance_infos: List[InstanceInfo]
    )->Optional[List[InstanceUsageInfo]]:
        if not instance_infos:
            return None
        usage_info = {}
        for info in instance_infos:
            usage_info[info.id.get_value()] = {}
        # cpu usage and io
        command = CommandSetting(Command('iostat'))
        results1 = self.run_command(instance_infos, command)
        # memory
        command = CommandSetting(Command('free -m'))
        results2 = self.run_command(instance_infos, command)
        # flow io
        command = CommandSetting(Command('ifstat'))
        results3 = self.run_command(instance_infos, command)
        set_sampling = True
        # disk
        command = CommandSetting(Command('df -hl'))
        results4 = self.run_command(instance_infos, command)
        if not results1 or not results2 or not results3 or not results4:
            return None
        for r1, r2, r3, r4 in zip(results1, results2, results3, results4):
            if r1:
                cpu_num, cpu_usage, io_in, io_out = self._extract_cpu_usage_info(r1.output.get_value())
                _id = r1.instance_id.get_value()
                usage_info[_id]['cpu_num'] = cpu_num
                usage_info[_id]['cpu_usage'] = cpu_usage
                usage_info[_id]['io_in'] = io_in
                usage_info[_id]['io_out'] = io_out
            if r2:
                total_mem, usage_mem = self._extract_memory_usage_info(r2.output.get_value())
                _id = r2.instance_id.get_value()
                usage_info[_id]['total_mem'] = total_mem
                usage_info[_id]['usage_mem'] = usage_mem
            if r3:
                flow_in, flow_out = self._extract_flow_info(r3.output.get_value())
                _id = r3.instance_id.get_value()
                usage_info[_id]['flow_in'] = flow_in
                usage_info[_id]['flow_out'] = flow_out
                if flow_in==0 or flow_out==0:
                    set_sampling = False
            if r4:
                disk_size, disk_usage = self._extract_disk_info(r4.output.get_value())
                usage_info[_id]['disk_size'] = disk_size
                usage_info[_id]['disk_usage'] = disk_usage
        if not set_sampling:
            command = CommandSetting(
                Command('ifstat -d 1')
            )
            self.run_command(instance_infos, command)
            command = CommandSetting(
                Command('ifstat')
            )
            results3 = self.run_command(instance_infos, command)
            for r3 in results3:
                if r3:
                    flow_in, flow_out = self._extract_flow_info(r3.output.get_value())
                    _id = r3.instance_id.get_value()
                    usage_info[_id]['flow_in'] = flow_in
                    usage_info[_id]['flow_out'] = flow_out
        instance_usage_infos = []
        for info in instance_infos:
            id = info.id.get_value()
            instance_usage_infos.append(
                InstanceUsageInfo(
                    instance_id=id,
                    instance_name = info.name,
                    cpu_number= Number(usage_info[id]['cpu_num']) 
                        if id in usage_info and 'cpu_num' in usage_info[id] else None,
                    cpu_usage = Usage(usage_info[id]['cpu_usage'])
                        if id in usage_info and 'cpu_usage' in usage_info[id] else None,
                    memory_size = Size(usage_info[id]['total_mem'])
                        if id in usage_info and 'total_mem' in usage_info[id] else None,
                    memory_usage= Size(usage_info[id]['usage_mem'])
                        if id in usage_info and 'usage_mem' in usage_info[id] else None,
                    flow_in = Size(usage_info[id]['flow_in'])
                        if id in usage_info and 'flow_in' in usage_info[id] else None,
                    flow_out = Size(usage_info[id]['flow_out'])
                        if id in usage_info and 'flow_out' in usage_info[id] else None,
                    disk_size = Size(usage_info[id]['disk_size'])
                        if id in usage_info and 'disk_size' in usage_info[id] else None,
                    disk_usage= Size(usage_info[id]['disk_usage'])
                        if id in usage_info and 'disk_usage' in usage_info[id] else None,
                    io_in = Size(usage_info[id]['io_in'])
                        if id in usage_info and 'io_in' in usage_info[id] else None,
                    io_out = Size(usage_info[id]['io_out'])
                        if id in usage_info and 'io_out' in usage_info[id] else None
                )
            )
        return instance_usage_infos

    def get_instance_usage(
        self,
        instance_infos: List[InstanceInfo]
    )->List[InstanceUsageInfo]:
        instance_ids = [info.id.get_value() for info in instance_infos]
        instance_ids_string = ''.join(instance_ids)
        key = f'{get_md5(instance_ids_string)}:instance_usage'
        return self.find_entity_helper(
            self._get_instance_usage,
            key=key,
            converter=None,
            instance_infos=instance_infos
        )

    def release_instances(self, infos: List[InstanceInfo]):
        infos = [instance_info_converter.to_do(info) for info in infos]
        result = self.ao.release_instances(infos)
        if result.succeed:
            return True
        else:
            instance_names_str = ','.join([info.name for info in infos])
            self.log_func(f'Fail to release instances: {instance_names_str}')
            self.log_func(result.error_traceback)
            return False


class DNSRepositoryImpl(DNSRepository, RepositoryImpl):
    def __init__(self, ip, port, token, log_func=None):
        self.ao = VPCController(ip, port, token)
        super().__init__(log_func=log_func)

    def create_dns_record(self, record: DNSRecord)->Optional[DNSRecord]:
        record = dns_record_converter.to_do(record)
        result = self.ao.create_dns_record(record)
        if result.succeed:
            return dns_record_converter.to_entity(result.get_value())
        else:
            dn = record.domain_name
            subdomain = record.subdomain
            self.log_func(f'Fail to create dns record: {subdomain}/{dn}')
            self.log_func(result.error_traceback)
            return None

    def save_dns_record(self, record: DNSRecord)->Optional[DNSRecord]:
        domain_name = record.domain_name
        existing_records = self.get_dns_records(domain_name)
        for r in existing_records:
            if r.domain_name==record.domain_name and r.subdomain==record.subdomain \
                and r.value==record.value:
                if r==record:
                    return r
                else: 
                    record.id = r.id
                    return self.update_dns_record(record)
        return self.create_dns_record(record)

    def delete_dns_record(self, record_id: RecordID)->None:
        record_id = record_id.get_value()
        result = self.ao.delete_dns_record(record_id)
        if result.succeed:
            return None
        else:
            self.log_func(f'Fail to delete dns record: {record_id}')
            self.log_func(result.error_traceback)
            return None

    def _get_dns_records(self, domain_name: DomainName)->Optional[List[DNSRecord]]:
        domain_name = domain_name.get_value()
        result = self.ao.get_dns_records(domain_name)
        if result.succeed:
            return [dns_record_converter.to_entity(x) for x in result.get_value()]
        else:
            self.log_func(f'Fail to fetch dns record: {domain_name}')
            self.log_func(result.error_traceback)
            return None

    def get_dns_records(self, domain_name: DomainName)->Optional[List[DNSRecord]]:
        key = f'{domain_name}:dns_records'
        return self.find_entity_helper(
            self._get_dns_records,
            key=key,
            converter=None,
            domain_name=domain_name
        )

    def update_dns_record(self, record: DNSRecord)->Optional[DNSRecord]:
        records = self.get_dns_records(record.domain_name)
        for r in records:
            if record==r:
                return r
        record = dns_record_converter.to_do(record)
        result = self.ao.update_dns_record(record)
        if result.succeed:
            return dns_record_converter.to_entity(result.get_value())
        else:
            dn = record.domain_name
            sub = record.subdomain
            self.log_func(f'Fail to update dns record: {dn}/{sub}')
            self.log_func(result.error_traceback)
            return None
