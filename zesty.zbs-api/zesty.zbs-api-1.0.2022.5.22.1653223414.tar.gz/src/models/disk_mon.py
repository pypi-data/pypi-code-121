import warnings

from .hf_interface import IDeviceHF
from zesty.id_handler import create_zesty_filesystem_id

from .FileSystem import FileSystem

GB_IN_BYTES = 1024**3


class DiskMonitor:
    def __init__(self, disk_mon_data, cloud_vendor="Amazon"):
        self.filesystems = {}
        self.unused_devices = {}
        self.cloud_vendor = cloud_vendor

        for fs in disk_mon_data.get('filesystems', {}):
            self.filesystems[
                create_zesty_filesystem_id(cloud=self.cloud_vendor, fs_id=fs)
                ] = FileSystem(
                    **{
                        **disk_mon_data.get('filesystems', {}).get(fs, {}),
                        'fs_id': fs,
                        'cloud_vendor': self.cloud_vendor
                    }
            )

        for unused_dev in disk_mon_data.get('unused_devices', {}):
            self.unused_devices[unused_dev] = self.UnusedDevice(disk_mon_data.get('unused_devices', {}).get(unused_dev, {}))

    class UnusedDevice:
        def __init__(self, block_device_data):
            self.size = block_device_data.get('size')
            self.map = block_device_data.get('map')
