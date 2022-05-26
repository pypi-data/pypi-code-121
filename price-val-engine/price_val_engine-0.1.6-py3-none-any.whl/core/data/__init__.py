import os
import fsspec
from price_val_engine.conf import settings

class FSObject:
    
    def __init__(self, file_path) -> None:
        print(file_path)
        self.file_path = file_path
    
    def get_storage_options(self, protocol):
        storage_options = {}
        if protocol == 's3':
            key = settings.AWS_ACCESS_KEY_ID or os.environ.get('AWS_ACCESS_KEY_ID')
            secret = settings.AWS_SECRET_ACCESS_KEY or os.environ.get('AWS_SECRET_ACCESS_KEY')
            token = settings.AWS_SESSION_TOKEN or os.environ.get('AWS_SESSION_TOKEN')
            storage_options = { 'key': key, 'secret': secret }     
            if token:
                storage_options['token'] = token
        elif protocol == 'gcs':
            token = settings.GCS_TOKEN or os.environ.get('GCS_TOKEN') or 'anon'
            storage_options['token'] = token 
        return storage_options
    
    def get_fs(self) -> fsspec.filesystem:
        protocol, path = fsspec.core.split_protocol(self.file_path)
        storage_options = self.get_storage_options(protocol=protocol)
        return fsspec.filesystem(protocol, **storage_options)
    