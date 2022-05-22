class CloudVendors:
    CLOUD_NOT_DETECTED = 'Could not detect cloud vendor'

    AMAZON = 'Amazon'
    AZURE = 'Azure'

    @classmethod
    def is_valid_cloud(cls, cloud_name):
        return cloud_name in vars(cls).values() and cloud_name != cls.CLOUD_NOT_DETECTED
