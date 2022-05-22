import json
import traceback
from decimal import Decimal
from typing import Dict

from zesty.id_handler import create_zesty_id

GB_IN_BYTES = 1024**3


class BlockDevice:
    def __init__(
            self,
            size: int,
            btrfs_dev_id: str = None,
            cloud_vendor: str = 'Amazon',
            created: str = None,
            dev_usage: int = None,
            iops: int = None,
            throughput: int = None,
            lun: int = None,
            map: str = None,
            iops_stats: Dict[str, int] = None,
            parent: str = None,
            unlock_ts: int = 0,
            volume_id: str = None,
            volume_type: str = None,
            device: str = None,
            ):
        """
        Block Device class doc:
        :param size: Size of the device in Bytes
        :param btrfs_dev_id: ID of the device inside the BTRFS structure
        :param cloud_vendor: Cloud vendor (AWS/Azure/GCP)
        :param created: Device creation date
        :param dev_usage: How much of the device is in use (in Bytes)
        :param iops: Device IOPS amount
        :param lun: LUN number (Only for Azure)
        :param map: The mount slot of the device inside the OS
        :param iops_stats: Dict with IOPS statistics
        :param parent: If it's a partition so this one represent the parent device
        :param unlock_ts: TS when the device will be ready to be extended again
        :param volume_id: Device ID
        :param volume_type: Type of the device in the cloud
        :param device: Device mount slot from the cloud
        """
        # Init empty dict here instead of passing as default value
        iops_stats = {} if iops_stats is None else iops_stats

        self.size = size
        self.cloud_vendor = cloud_vendor
        try:
            self.volume_id = create_zesty_id(
                cloud=self.cloud_vendor,
                resource_id=volume_id
            )
        except:
            self.volume_id = volume_id
        self.btrfs_dev_id = btrfs_dev_id
        self.created = created
        self.dev_usage = dev_usage
        self.iops = iops
        self.throughput = throughput
        self.lun = lun
        self.map = map
        self.iops_stats = iops_stats
        if device:
            self.device = device
        if parent:
            self.parent = parent

        if not unlock_ts:
            self.unlock_ts = 0
        else:
            self.unlock_ts = unlock_ts

        self.volume_type = volume_type
    
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
        return str(self.as_dict())

