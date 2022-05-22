import json
import time
import traceback
from typing import Dict
from copy import deepcopy
from decimal import Decimal

from zesty.id_handler import create_zesty_id, create_zesty_filesystem_id

from ..actions import ZBSAction
from .BlockDevice import BlockDevice
from .Usage import Usage

GB_IN_BYTES = 1024**3


class FileSystem:
    """
    This object interacts with DynamoDB representing a FileSystem.

    As per the data model migration ZES-2884,
    these will be backwards compatible and awkward in appearance until
    the code is brought up to date.
    """
    def __init__(
            self,
            fs_id: str,
            account_id: str = None,
            account_uuid: str = None,
            agent_update_required: bool = None,
            btrfs_version: str = None,
            cloud: str = None,
            cloud_vendor: str = None,
            cycle_period: int = None,
            delete_on_termination: bool = None,
            devices: Dict[str, BlockDevice] = None,
            encrypted: dict = None,
            existing_actions: Dict[str, ZBSAction] = None,
            expiredAt: int = None,
            fs_cost: float = None,
            fs_devices_to_count: int = None,
            fs_size: int = None,
            fs_type: str = None,
            fs_usage: int = None,
            has_unallocated_space: bool = None,
            inodes: Dict[str, Usage] = None,
            instance_id: str = None,
            instance_type: str = None,
            is_ephemeral: bool = None,
            is_partition: bool = None,
            is_zesty_disk: bool = None,
            label: str = None,
            last_update: int = None,
            LV: str = None,
            lvm_path: str = None,
            mount_path: str = None,
            name: str = None,
            org_id: str = None,
            partition_id: str = None,
            partition_number: int = None,
            platform: str = None,
            potential_savings: float = None,
            region: str = None,
            resizable: bool = None,
            space: Dict[str, Usage] = None,
            tags: Dict[str, str] = None,
            unallocated_chunk: int = None,
            update_data_ts: int = 0,
            VG: str = None,
            wrong_fs_alert: bool = None,
            zesty_disk_iops: int = None,
            zesty_disk_vol_type: str = None,
            max_utilization_in_72_hrs: int = None,
            package_version: str = None,
            autoupdate_last_execution_time: str = None,
            statvfs_raw_data: Dict[str, str] = None,
            pvc_id: str = None,
            mount_options: list = None,
            leading_device: str = None
            ):

        # Initialize empty dict not as default arg
        existing_actions = {} if existing_actions is None else existing_actions
        devices = {} if devices is None else devices
        inodes = {} if inodes is None else inodes
        space = {} if space is None else space
        tags = {} if tags is None else tags

        self.account_id = account_id
        self.account_uuid = account_uuid
        self.agent_update_required = agent_update_required
        self.btrfs_version = btrfs_version
        if cloud is None and cloud_vendor is None:
            self.cloud = 'Amazon'
            self.cloud_vendor = 'Amazon'
        elif cloud:
            self.cloud = cloud
            self.cloud_vendor = cloud
        elif cloud_vendor:
            self.cloud = cloud_vendor
            self.cloud_vendor = cloud_vendor
        self.cycle_period = cycle_period
        self.devices = self.init_devices(devices)
        self.delete_on_termination = delete_on_termination
        self.encrypted = encrypted
        self.existing_actions = existing_actions
        self.expiredAt = expiredAt
        self.fs_cost = fs_cost
        self.fs_devices_to_count = fs_devices_to_count
        try:
            self.fs_id = create_zesty_filesystem_id(
                cloud=self.cloud_vendor,
                fs_id=fs_id
            )
        except Exception as e:
            self.fs_id = fs_id
        self.fs_size = fs_size
        self.fs_type = fs_type
        self.fs_usage = fs_usage
        self.has_unallocated_space = has_unallocated_space
        self.inodes = Usage(inodes)
        self.instance_id = instance_id
        self.instance_type = instance_type
        self.is_ephemeral = is_ephemeral
        self.is_partition = is_partition
        self.is_zesty_disk = is_zesty_disk
        self.label = label
        if last_update is None:
            self.last_update = int(time.time()) - 60
        else:
            self.last_update = last_update
        self.LV = LV
        self.lvm_path = lvm_path
        self.mount_path = mount_path
        self.name = name
        self.org_id = org_id
        self.partition_id = partition_id
        self.partition_number = partition_number
        self.platform = platform
        self.potential_savings = potential_savings
        self.region = region
        self.resizable = resizable
        self.space = Usage(space)
        self.tags = tags
        self.unallocated_chunk = unallocated_chunk
        self.update_data_ts = update_data_ts
        self.VG = VG
        self.wrong_fs_alert = wrong_fs_alert
        self.zesty_disk_iops = zesty_disk_iops
        self.zesty_disk_vol_type = zesty_disk_vol_type
        self.max_utilization_in_72_hrs = max_utilization_in_72_hrs
        self.package_version = package_version
        self.autoupdate_last_execution_time = autoupdate_last_execution_time
        self.statvfs_raw_data = statvfs_raw_data
        self.pvc_id = pvc_id
        self.mount_options = mount_options
        self.leading_device = leading_device

    @staticmethod
    def init_devices(devices: Dict[str, BlockDevice]):
        if not devices:
            return {}
        else:
            devices = deepcopy(devices)
            for dev in devices:
                if isinstance(devices[dev], BlockDevice):
                    continue
                devices[dev] = BlockDevice(
                    **devices.get(dev, {})
                )
            return devices

    def as_dict(self) -> dict:
        return_dict = json.loads(json.dumps(self, default=self.object_dumper))
        return {k: v for k, v in return_dict.items() if v is not None}

    @staticmethod
    def object_dumper(obj) -> dict:
        try:
            return obj.__dict__
        except AttributeError as e:
            if isinstance(obj, Decimal):
                return int(obj)
            print(f"Got exception in object_dumper value: {obj} | type : {type(obj)}")
            print(traceback.format_exc())
            return obj

    def serialize(self) -> dict:
        return self.as_dict()
    
    def __repr__(self) -> str:
        return f"FileSystem:{self.fs_id}"

