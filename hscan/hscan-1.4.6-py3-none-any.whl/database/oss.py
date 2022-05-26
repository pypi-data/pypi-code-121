import oss2


class OSS:
    def __init__(self, **kwargs):
        self.oss_type = kwargs.get('type') or 'oss'
        self.acc_id = kwargs.get('acc_id')
        self.acc_sec = kwargs.get('acc_sec')
        self.region = kwargs.get('region')
        self.bucket = kwargs.get('bucket')
        self.oss_conn = self.connection()

    def connection(self):
        auth = oss2.Auth(self.acc_id, self.acc_sec)
        oss_con = oss2.Bucket(auth, self.region, self.bucket)
        return oss_con


__all__ = OSS

