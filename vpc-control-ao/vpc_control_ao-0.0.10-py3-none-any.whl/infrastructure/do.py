from dataclasses import dataclass
from typing import List, Optional
from ddd_objects.infrastructure.do import BaseDO

@dataclass
class ConditionDO(BaseDO):
    min_cpu_num: int = None
    max_cpu_num: int = None
    min_memory_size: int = None
    max_memory_size: int = None
    min_gpu_num: int = None
    max_gpu_num: int = None
    min_gpu_memory_size: int = None
    max_gpu_memory_size: int = None

@dataclass
class InstanceUserSettingDO(BaseDO):
    name: str
    password: str
    amount: int
    image_id: str
    region_id: str
    internet_pay_type: str
    bandwidth_in: int
    bandwidth_out: int
    user_data: str
    disk_size: int
    key_name: str
    exclude_instance_types: List[str]
    inner_connection: bool = True

@dataclass
class InstanceTypeUserSettingDO(BaseDO):
    region_id: str
    zone_id: str
    instance_type_id: str

@dataclass
class InstanceTypeWithStatusDO(BaseDO):
    region_id: str
    zone_id: str
    instance_type_id: str
    cpu_number: int
    memory_size: float
    gpu_type: str
    gpu_number: int
    status: str
    status_category: str
    _life_time: int = 5

@dataclass
class InstanceInfoDO(BaseDO):
    id: str
    instance_type: str
    create_time: str
    name: str
    hostname: str
    pay_type: str
    public_ip: List[str]
    private_ip: str
    os_name: str
    price: float
    image_id: str
    region_id: str
    zone_id: str
    internet_pay_type: str
    bandwidth_in: str
    bandwidth_out: str
    security_group_id: List[str]
    expired_time: str
    auto_release_time: str
    status: str
    key_name: str
    _life_time: int = 5

@dataclass
class CommandSettingDO(BaseDO):
    command: str
    timeout: int
    forks: int
    username: str = 'root'
    port: int = 22
    password: str = None
    inner_connection: bool = True

@dataclass
class CommandResultDO(BaseDO):
    succeed: bool
    output: str
    ip: str
    instance_id: str
    instance_name: str

@dataclass
class OSSOperationInfoDO(BaseDO):
    name: str
    bucket_name: str
    local_path: str
    target_path: str
    endpoint: str
    with_tar: bool = False

@dataclass
class DNSRecordDO(BaseDO):
    domain_name: str
    subdomain: str
    value: str
    id: Optional[str]=None
    weight: Optional[int]=None
    dns_type: str='A'
    ttl: int=600
    priority: Optional[int]=None
    line: Optional[str]=None