import time
from typing import Dict

from sqlalchemy import Column, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, FLOAT, \
    JSON, VARCHAR

from .BlockDevice import BlockDevice
from .Usage import Usage
from ..actions import ZBSAction

Base = declarative_base()


class ManagedFsMixin:
    fs_id = Column(VARCHAR, primary_key=True)
    account_id = Column(VARCHAR, index=True, default=None)
    account_uuid = Column(VARCHAR, index=True, default=None)
    agent_update_required = Column(BOOLEAN, default=None)
    btrfs_version = Column(VARCHAR, default=None)
    cloud = Column(VARCHAR, default=None)
    cloud_vendor = Column(VARCHAR, default=None)
    cycle_period = Column(BIGINT, default=None)
    delete_on_termination = Column(BOOLEAN, default=None)
    devices = Column(JSON, default=None)
    encrypted = Column(JSON, default=None)
    existing_actions = Column(JSON, default=None)
    expiredAt = Column(BIGINT, default=None)
    fs_cost = Column(FLOAT, default=None)
    fs_devices_to_count = Column(BIGINT, default=None)
    fs_size = Column(BIGINT, default=None)
    fs_type = Column(VARCHAR, default=None)
    fs_usage = Column(BIGINT, default=None)
    has_unallocated_space = Column(BOOLEAN, default=None)
    inodes = Column(JSON, default=None)
    instance_id = Column(VARCHAR, default=None)
    instance_type = Column(VARCHAR, default=None)
    is_ephemeral = Column(BOOLEAN, default=None)
    is_partition = Column(BOOLEAN, default=None)
    is_zesty_disk = Column(BOOLEAN, default=None)
    label = Column(VARCHAR, default=None)
    last_update = Column(BIGINT, default=None)
    LV = Column(VARCHAR, default=None)
    lvm_path = Column(VARCHAR, default=None)
    mount_path = Column(VARCHAR, default=None)
    name = Column(VARCHAR, default=None)
    org_id = Column(VARCHAR, index=True)
    partition_id = Column(VARCHAR, default=None)
    partition_number = Column(BIGINT, default=None)
    platform = Column(VARCHAR, default=None)
    potential_savings = Column(FLOAT, default=None)
    region = Column(VARCHAR, index=True)
    resizable = Column(BOOLEAN, default=None)
    space = Column(JSON, default=None)
    tags = Column(JSON, default=None)
    unallocated_chunk = Column(BIGINT, default=None)
    update_data_ts = Column(BIGINT, default=0)
    VG = Column(VARCHAR, default=None)
    wrong_fs_alert = Column(BOOLEAN, default=None)
    zesty_disk_iops = Column(BIGINT, default=None)
    zesty_disk_vol_type = Column(VARCHAR, default=None)
    max_utilization_in_72_hrs = Column(BIGINT, default=None)
    package_version = Column(VARCHAR, default=None)
    autoupdate_last_execution_time = Column(VARCHAR, default=None)

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
            statvfs_raw_data: Dict[str, str] = None
            ):
        self.fs_id = fs_id
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
        self.delete_on_termination = delete_on_termination
        self.devices = devices
        if devices:
            for dev in self.devices:
                if isinstance(self.devices[dev], BlockDevice):
                    self.devices[dev] = self.devices[dev].asdict()
                else:
                    self.devices[dev] = self.devices.get(dev, {})
        self.encrypted = encrypted
        if existing_actions:
            for action in existing_actions:
                self.existing_actions[action] = self.existing_actions[action].serialize()
        self.expiredAt = expiredAt
        self.fs_cost = fs_cost
        self.fs_devices_to_count = fs_devices_to_count
        self.fs_size = fs_size
        self.fs_type = fs_type
        self.fs_usage = fs_usage
        self.has_unallocated_space = has_unallocated_space
        self.inodes = inodes
        self.instance_id = instance_id
        self.instance_type = instance_type
        self.is_ephemeral = is_ephemeral
        self.is_partition = is_partition
        self.is_zesty_disk = is_zesty_disk
        self.label = label
        if last_update:
            self.last_update = last_update
        else:
            self.last_update = int(time.time()) - 60
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
        self.space = space
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

    def __repr__(self) -> str:
        return f"{self.__tablename__}:{self.fs_id}"

    def asdict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_dict(self) -> dict:
        return self.asdict()


class ManagedFs(ManagedFsMixin, Base):
    __tablename__ = "managed_filesystems"


def create_tables(engine: engine.base.Engine) -> None:
    Base.metadata.create_all(engine, checkfirst=True)
