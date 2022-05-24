import json
from io import StringIO


class MockS3():
    data = None
    files = 'test'
    bucket_name = 'test'

    def create_space_if_not_exists(self):
        pass

    def reset_history(self, runid, collection):
        pass

    def save_file(self, *args, **kwargs):
        pass

    def get_file(self, *args, **kwargs):
        return self.files

    def list_files(self, *args, **kwargs):
        pass

    def list_buckets(self, *args, **kargs):
        return {'Buckets': [{'Name': self.files }]}

    def list_objects_v2(self, *args, **kargs):
        return {}

    def create_bucket(self, *args, **kwargs):
        pass

    def put_object(self, Body=None, Key=None, *args, **kwargs):
        self.data = Body
        self.files = Key

    def get_object(self, *args, **kwargs):
        f = open('./test.txt', 'rb')
        return {
            'Body':f
        }

    def list_objects(self, *args, **kwargs):
        return {
            "Contents": [
                {'Key': self.files}
            ]
        }

class MockPayload():
    pass