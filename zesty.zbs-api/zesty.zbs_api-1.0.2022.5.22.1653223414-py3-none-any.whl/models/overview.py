from zesty.id_handler import create_zesty_id


class MachineData:
    def __init__(self, machine_data):
        self.cloud_vendor = machine_data.get('cloud', 'Amazon')
        self.os = self.OS(machine_data.get('os', {}))
        self.instance = self.Instance(machine_data.get('instance', {}), self.cloud_vendor)

    class OS:
        def __init__(self, os_data):
            self.system = os_data.get('system')
            self.name = os_data.get('name')
            self.processor = os_data.get('processor')
            self.id = os_data.get('id')
            self.os_pretty_name = os_data.get('os_pretty_name', 'N/A')

    class Instance:
        def __init__(self, instance_data, cloud_vendor="Amazon"):
            self.accountId = instance_data.get('accountId')
            self.architecture = instance_data.get('architecture')
            self.availabilityZone = instance_data.get('availabilityZone')
            self.billingProducts = instance_data.get('billingProducts')
            self.devpayProductCodes = instance_data.get('devpayProductCodes')
            self.marketplaceProductCodes = instance_data.get('marketplaceProductCodes')
            self.imageId = instance_data.get('imageId')
            self.instanceId = instance_data.get('instanceId')
            self.instanceType = instance_data.get('instanceType')
            self.kernelId = instance_data.get('kernelId')
            self.pendingTime = instance_data.get('pendingTime')
            self.privateIp = instance_data.get('privateIp')
            self.ramdiskId = instance_data.get('ramdiskId')
            self.region = instance_data.get('region')
            self.version = instance_data.get('version')

            try:
                self.instanceId = create_zesty_id(cloud=cloud_vendor, resource_id=self.instanceId)
            except Exception as e:
                print(f"Failed to create ZestyID, will stay with {self.instanceId} || ERROR : {e}")
