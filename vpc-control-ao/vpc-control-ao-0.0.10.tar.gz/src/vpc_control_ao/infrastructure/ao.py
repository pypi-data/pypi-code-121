from ddd_objects.infrastructure.ao import exception_class_dec
from ddd_objects.infrastructure.repository_impl import error_factory
from ddd_objects.domain.exception import return_codes
import json, requests
from typing import List
from .do import (
    ConditionDO,
    DNSRecordDO,
    InstanceInfoDO,
    InstanceTypeUserSettingDO,
    InstanceTypeWithStatusDO,
    InstanceUserSettingDO,
    CommandResultDO,
    CommandSettingDO,
    OSSOperationInfoDO
)

class VPCController:
    def __init__(self, ip:str, port:str, token:str) -> None:
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

    @exception_class_dec()
    def new_instance(self, condition:ConditionDO, setting:InstanceUserSettingDO, timeout=1200):
        data = {
            "condition": condition.to_json(),
            "setting": setting.to_json()
        }
        data = json.dumps(data)
        response=requests.post(f'{self.url}/instances', 
            headers=self.header, data=data, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        if infos is None:
            return None
        else:
            return [InstanceInfoDO(**info) for info in infos]

    @exception_class_dec()
    def modify_instance(self, instance_infos: List[InstanceInfoDO], timeout=30):
        instance_infos = [info.to_json() for info in instance_infos]
        data = json.dumps(instance_infos)
        response=requests.put(f'{self.url}/instances', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec()
    def get_instance(self, region_id: str, timeout=60):
        response=requests.get(f'{self.url}/instances/region_id/{region_id}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [InstanceInfoDO(**info) for info in infos]

    @exception_class_dec()
    def get_instance_by_name(self, region_id: str, name: str, timeout=60):
        response=requests.get(f'{self.url}/instances/region_id/{region_id}/name/{name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [InstanceInfoDO(**info) for info in infos]

    @exception_class_dec()
    def get_instance_type_status(self, settings: List[InstanceTypeUserSettingDO], timeout=60):
        data = [setting.to_json() for setting in settings]
        data = json.dumps(data)
        response=requests.get(f'{self.url}/instance_types/status', 
            headers=self.header, data=data, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [InstanceTypeWithStatusDO(**r) for r in infos]

    @exception_class_dec()
    def release_instances(self, instance_infos: List[InstanceInfoDO], timeout=60):
        instance_infos = [info.to_json() for info in instance_infos]
        data = json.dumps(instance_infos)
        response=requests.delete(f'{self.url}/instances', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec()
    def run_command(
        self, 
        instance_infos: List[InstanceInfoDO], 
        setting: CommandSettingDO
    ):
        instance_infos = [info.to_json() for info in instance_infos]
        data = {
            "instance_infos": instance_infos,
            "command_setting": setting.to_json()
        }
        data = json.dumps(data)
        timeout = setting.timeout
        response=requests.post(f'{self.url}/instances/command', 
            headers=self.header, data=data, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [CommandResultDO(**r) if r else None for r in infos]

    @exception_class_dec()
    def oss_operate(self, 
        instance_infos: List[InstanceInfoDO], 
        oss_operation_info: OSSOperationInfoDO,
        command_setting: CommandSettingDO,
        timeout=60
    ):
        instance_infos = [info.to_json() for info in instance_infos]
        data = {
            "instance_infos": instance_infos,
            "oss_operation_info": oss_operation_info.to_json(),
            "command_setting": command_setting.to_json()
        }
        data = json.dumps(data)
        response=requests.post(f'{self.url}/instances/oss', 
            headers=self.header, data=data, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [CommandResultDO(**r) for r in infos]

    @exception_class_dec()
    def create_dns_record(
        self,
        record: DNSRecordDO,
        timeout=30
    ):
        data = record.to_json()
        data = json.dumps(data)
        response = requests.post(f'{self.url}/dns_record',
            headers = self.header, data=data, timeout=timeout
        )
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return DNSRecordDO(**info)

    @exception_class_dec()
    def get_dns_records(
        self,
        domain_name: str,
        timeout=20
    ):
        response = requests.get(f'{self.url}/dns_records/domain_name/{domain_name}', 
            headers=self.header, timeout=timeout)
        infos = json.loads(response.text)
        self._check_error(response.status_code, infos)
        return [DNSRecordDO(**info) for info in infos]

    @exception_class_dec()
    def update_dns_record(self, record: DNSRecordDO, timeout=30):
        data = json.dumps(record.to_json())
        response = requests.put(f'{self.url}/dns_record', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return DNSRecordDO(**info)

    @exception_class_dec()
    def delete_dns_record(self, record_id: str, timeout=30):
        response = requests.delete(f'{self.url}/dns_record/record_id/{record_id}',
            headers=self.header, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info
repo_info = \
{
    "DNSRepository":{
        "create_dns_record":{
            "args":[["record", True, "DNSRecord", None, False, False, "dns_record_converter"]],
            "ret":["record", True, "DNSRecord", None, False, True, "dns_record_converter"]
        },
        "delete_dns_record":{
            "args":[["record_id", False]]
        },
        "get_dns_records":{
            "args":[["domain_name", False]],
            "ret":["records", True, "DNSRecord", None, True, True, "dns_record_converter"],
            "key":"{domain_name}:dns_records"
        },
        "update_dns_record":{
            "args":[["record", True, "DNSRecord", None, True, True, "dns_record_converter"]],
            "ret":["record", True, "DNSRecord", None, False, True, "dns_record_converter"]
        }
    },
    "VPCRepository":{
        "get_instance":{
            "args":[["region_id", False]],
            "ret":["instance_info", True, None, None, True, True],
            "key":"{region_id}:instances"
        },
        "get_instance_by_name":{
            "args":[["region_id", False], ["name", False, "Name", None]],
            "ret":["instance_info", True, None, None, True, True],
            "key":"{region_id}:{name}:instances"
        },
        "get_instance_type_status":{
            "args":[["settings", True, "InstanceTypeUserSetting", None, True]],
            "ret":["instance_type_with_status", True, None, None, True, True],
            "key":"{settings}:instance_type_status"
        },
        "new_instance":{
            "args":["condition", ["setting", True, "InstanceUserSetting"]],
            "ret":["instance_info", True, None, None, True, True]
        },
        "oss_operate":{
            "args":[["instance_infos", True, "InstanceInfo", None, True], ["oss_operation_info", True, "OSSOperationInfo", None, False, False, "oss_operation_info_converter"], "command_setting"],
            "ret":["command_result", True, None, None, True, True]
        },
        "release_instances":{
            "args":[["instance_infos", True, "InstanceInfo", None, True]]
        },
        "run_command":{
            "args":[["instance_infos", True, "InstanceInfo", None, True], "command_setting"],
            "ret":["command_result", True, None, None, True, True]
        }
    }
}