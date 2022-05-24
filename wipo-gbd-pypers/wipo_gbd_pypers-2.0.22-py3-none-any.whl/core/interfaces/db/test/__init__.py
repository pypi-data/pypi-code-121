import copy


class MockDB():
    attributs = ['meta', 'client']
    func = ['get_waiter', 'wait', 'put_item', 'send_raw_email', 'delete_item', 'update_time_to_live']

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self

    def batch_writer(self, *args, **kwargs):
        return self

    def __init__(self):
        self.display_error = False
        self.updated_item = None
        for func in self.attributs:
            setattr(self, func, self)
        for func in self.func:
            setattr(self, func, self.generic)

    def get_item(self, *args, **kwargs):
        if self.updated_item is not None:
            to_return = {
                'Item': {
                    'steps_config': copy.deepcopy(self.updated_item)
                }
            }
            self.updated_item = None
            return to_return
        return {
            'Item': {
                'steps_config': {
                    'bar': {
                        'config': {}
                    }
                }
            }
        }

    def get_pipeline_config(self, *args, **kwargs):
        return {}

    def query(self, *args, **kwargs):
        return {
            'Items': []
        }

    def get_secret_value(self, *args, **kwargs):
        return {'SecretString': 'toto'}

    def list_secrets(self, *args, **kwargs):
        return {'SecretList': []}

    def update_item(self, *args, **kwargs):
        item = kwargs.get('ExpressionAttributeValues', {}).get(':val1', {})
        self.updated_item = item
        return self

    def create_table(self, *arg, **kwargs):
        if self.display_error:
            self.display_error = False
            raise Exception()
        return self

    def generic(self, *args, **kwargs):
        return self


class MockSecrets():
    def key_from_value(self, value):
        return value

    def get(self, key, default):
        return 'toto'


def mock_secrets(*args, **kwargs):
    return MockSecrets()


class MockDBLogger():
    attributs = ['meta', 'client', 'exceptions']
    func = ['get_waiter', 'wait', 'put_item', 'log_entry', 'log_report', 'batch_writer', 'update_time_to_live']


    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

    def __init__(self):
        self.ResourceInUseException = Exception
        self.display_error = False
        for func in self.attributs:
            setattr(self, func, self)
        for func in self.func:
            setattr(self, func, self.generic)

    def get_paginator(self, *args, **kwargs):
        return self

    def paginate(self, *args, **kwargs):
        return []

    def list_secrets(self, *args, **kwargs):
        return {'SecretList': []}

    def query(self, *args, **kwargs):
        return {
            'Items': []
        }

    def get_secret_value(self, *args, **kwargs):
        return {'SecretString': 'toto'}

    def get_item(self, *args, **kwargs):
        return {}

    def put_item(self, *args, **kwargs):
        print("++++++++++++++++++++++++++++++++++++++")
        print(args, kwargs)

    def update_item(self, *args, **kwargs):
        pass

    def create_table(self, *arg, **kwargs):
        if self.display_error:
            self.display_error = False
            raise Exception()
        return self

    def generic(self, *args, **kwargs):
        return self


class MockDBConfig():
    attributs = ['meta', 'client']
    func = ['get_waiter', 'wait']

    def __init__(self):
        self.display_error = False
        for func in self.attributs:
            setattr(self, func, self)
        for func in self.func:
            setattr(self, func, self.generic)

    def list_secrets(self, *args, **kwargs):
        return {'SecretList': []}

    def get_configuration(self, *args, **kwargs):
        return {
            "dag": {
                "load": "ipas_fetch"
            },
            "config": {
                "pipeline": {
                    "project_name": "vntm",
                    "description": "desc",
                    "collection": "vntm",
                    "input": {
                        "from_dir": "%s/archives",
                        "from_ftp": {
                            "ftp_server": "dataexchange.wipo.int",
                            "ftp_user": "vt",
                            "ftp_passwd": "fglhk467056bgh",
                            "ftp_dir": "/To_BrandsDatabase/CHANGES"
                        }
                    },
                    "output_dir": "%s/workspace"
                },
                "steps": {
                    "pxml": {
                        "timestamp_file": 0
                    },
                    "fetch": {
                        "file_regex": "VN_Trademarks_.*zip"
                    },
                    "clean": {
                        "remove_orig": 0
                    },
                    "merge": {
                        "to_dir": "%s/release"
                    }
                }
            }
        }

    def get_item(self, *args, **kwargs):
        return {
            'Item': {
                'json': self.get_configuration()
                }
            }

    def create_table(self, *arg, **kwargs):
        if self.display_error:
            self.display_error = False
            raise Exception()
        return self

    def generic(self, *args, **kwargs):
        return self
