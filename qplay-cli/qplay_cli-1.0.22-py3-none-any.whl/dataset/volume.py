import subprocess
from qplay_cli.api_clients.volume_api import VolumeAPIClient
from ec2_metadata import ec2_metadata

VALID_DATASET_TYPES = ["NSE_EQ", "NSE_OPT", "NSE_FUT", "NSE_MARKET_DATA"]

class Volume:
    """Commands for listing attached volumes.
    """
    
    def __init__(self):
        pass
    
    def list_xvd_disks(self):
        """Returns a list of xvd type partitions (full disk if no partition are found)
        """
        
        command = "sudo blkid | grep 'xvd' | grep -v 'rootfs' | awk -F':' '{print $1}'"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err.decode("ASCII").strip()):
            raise Exception("Failed to list xvd type disks. Got error: {}".format(err))
            
        out_decoded = out.decode('ASCII').strip()
        
        return [] if not out else out_decoded.split("\n")
    
    def list_nvme_volumes(self, nvme_device=None):
        """Returns a dictionary mapping nvme_devices to volume ids.ArithmeticError
        
        :param nvme_device: str, pass this parameter to get the volume Id of specific nvme device, e.g. /dev/nvme0n1
        :return: dictionary mapping device to volumeid
        """
        command = "sudo nvme list"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        devices_info = out.decode("ASCII").strip().split("\n")[2:]
        result = { dev_info.split()[0] : "vol-" + dev_info.split()[1].strip("vol") for dev_info in devices_info}
        
        if nvme_device:
            if nvme_device not in result:
                raise Exception("nvme_device {} not found".format(nvme_device))
            return {nvme_device : result[nvme_device]}
        
        return result
    
    def symlink_nvme_partition_to_sd_device(self, nvme_partition, sd_device):
        """Symbollically link nvme_device partition to sd_device
        
        :param nvme_device_part: str, e.g. /dev/nvme1n1p1
        :param sd_device: str, e.g. /dev/sdf
        :raises exception if symlink was unsuccessfull.
        :return 0 if successfull
        """
        command = f"sudo ln -s {nvme_partition} {sd_device}"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err.decode("ASCII").strip()):
            raise Exception("Failed to create symbolic link from nvme_partition {} to sd_device {}. Got error: {}".format(nvme_partition, sd_device, err))
        
        print("Symbollically linked nvme_partition {} to sd_device {}".format(nvme_partition, sd_device))
        
        return 0
    
    def mount_device_to_dataset_directory(self, device, dataset_directory):
        """Mounts device to dataset directory. Creates the dataset_directory if it doesn't exist.
        
        :param device: str, e.g. /dev/nvme1n1p1, /dev/xvdf
        :param dataset_directory: str, e.g. /NSE_EQ , /NSE_OPT, /NSE_FUT
        :raises Exception if mount was unsuccessful
        :return 0 if successfull
        """
        command = f"sudo mkdir -p {dataset_directory}"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err.decode("ASCII").strip()):
            raise Exception("Failed to create directory {}. Got error: {}".format(dataset_directory, err))
        
        print("Successfully created directory {}".format(dataset_directory))
        
        command = f"sudo mount -v {device} {dataset_directory}"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err.decode("ASCII").strip()):
            raise Exception("Failed to mount device {} to dataset_directory {}. Got error: {}".format(device, dataset_directory, err))
        
        print("Successfully mounted device {} to dataset_directory {}".format(device, dataset_directory))
        
        return 0
    
    def mount_dataset_nvme_type(self, nvme_volume_ids, dataset_type):
        """Mounts given type of dataset on the local machine with nvme disks. Prints the path where
        the dataset is mounted.
        
        :param: dataset_type: str, valid types ["NSE_EQ", "NSE_OPT", "NSE_FUT"]
        :raises: exception if failed to mount the dataset or if the dataset type is invalid
        :returns: 0 if dataset is successfully mounted.
        """
        
        volumeAPIClient = VolumeAPIClient()
        

        for nvme_device, volume_id in nvme_volume_ids.items():
            vol_info = volumeAPIClient.get_volume_info(volume_id=volume_id)
            if (dataset_type and vol_info["DatasetType"] == dataset_type) or (vol_info["DatasetType"] in VALID_DATASET_TYPES):
                
                print("Valid dataset of {} present in (nvme_device, volume): {}. Will proceed to mounting".format(vol_info["DatasetType"], (nvme_device, volume_id)))
                
                #TODO: Use psutil.disk_partitions()
                dataset_directory = "/" + vol_info["DatasetType"]
                
                self.mount_device_to_dataset_directory(nvme_device, dataset_directory)
                
                print("Dataset type {} successfully mounted at path {}".format(vol_info["DatasetType"], dataset_directory))
            
            else:
                print("No valid dataset present in (nvme_device, volume): {}.".format((nvme_device, volume_id)))
                
        print("mounting process terminated for nvme disk types")
                
        return 0
    
    def mount_dataset_xvd_type(self, xvd_disks, dataset_type):
        """Mounts given type of dataset on the local machine with xvd* disks. Prints the path where
        the dataset is mounted.
        
        :param: dataset_type: str, valid types ["NSE_EQ", "NSE_OPT", "NSE_FUT"]
        :raises: exception if failed to mount the dataset or if the dataset type is invalid
        :returns: 0 if dataset is successfully mounted.
        """

        volumeAPIClient = VolumeAPIClient()
        

        for xvd_disk in xvd_disks:
            xvd_name = xvd_disk.split("/")[-1]
            vol_info = volumeAPIClient.get_volume_info(device_name=xvd_name)
            if (dataset_type and vol_info["DatasetType"] == dataset_type) or (vol_info["DatasetType"] in VALID_DATASET_TYPES):
                
                print("Valid dataset of {} present in xvd_disk: {}. Will proceed to mounting".format(vol_info["DatasetType"], xvd_disk))
                
                dataset_directory = "/" + vol_info["DatasetType"]
                
                self.mount_device_to_dataset_directory(xvd_disk, dataset_directory)
                
                print("Dataset type {} successfully mounted at path {}".format(vol_info["DatasetType"], dataset_directory))
            
            else:
                print("No valid dataset present in xvd_device: {}.".format(xvd_disk))
                
        print("mounting process terminated for xvd* disk types")
                
        return 0
    
    def mount_dataset(self, dataset_type=None):
        """Mounts given type of dataset on the local machine. Prints the path where
        the dataset is mounted.
        
        :param: dataset_type: str, valid types ["NSE_EQ", "NSE_OPT", "NSE_FUT"]
        :raises: exception if failed to mount the dataset or if the dataset type is invalid
        :returns: 0 if dataset is successfully mounted.
        """
        
        if dataset_type and dataset_type not in VALID_DATASET_TYPES:
            raise Exception("Invalid input dataset_type {}, Valid ones are {}".format(dataset_type, VALID_DATASET_TYPES))
        
        print("Looking for nvme disks")
        
        nvme_volume_ids = self.list_nvme_volumes()
        if nvme_volume_ids:
            print("NVME disks found: {}".format(nvme_volume_ids))
            self.mount_dataset_nvme_type(nvme_volume_ids, dataset_type)
        else:
            print("No nvme type disks found")
        
        
        print("Looking for xvd type disks")
        
        xvd_disks = self.list_xvd_disks()
        if xvd_disks:
            print("xvd disks found: {}".format(xvd_disks))
            self.mount_dataset_xvd_type(xvd_disks, dataset_type)
        else:
            print("No xvd type disks found")
    
    
    def unmount_datasets(self):
        nvme_volumes = self.list_nvme_volumes()
        xvd_disks = self.list_xvd_disks()

        devices_to_umount = []

        volumeAPIClient = VolumeAPIClient()

        for nvme_device, volume_id in nvme_volumes.items():
            vol_info = volumeAPIClient.get_volume_info(volume_id=volume_id)
            if vol_info["DatasetType"] in VALID_DATASET_TYPES:
                print(f"nvme {nvme_device} vol_info {vol_info}")
                devices_to_umount.append(nvme_device)

        for xvd_disk in xvd_disks:
            xvd_name = xvd_disk.split("/")[-1]
            vol_info = volumeAPIClient.get_volume_info(device_name=xvd_name)
            if vol_info["DatasetType"] in VALID_DATASET_TYPES:
                devices_to_umount.append(xvd_disk)
        
        if devices_to_umount:
            print("Unmounting devices {}".format(devices_to_umount))
        
            for device in devices_to_umount:
                command = f"sudo umount {device}"
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if len(err.decode("ASCII").strip()):
                    raise Exception("Failed to unmount device {}. Got error: {}".format(device, err))
                
                print("Successfully unmounted device {}".format(device))
        else:
            print("Nothing to unmount.")
        
        
        
        
        
