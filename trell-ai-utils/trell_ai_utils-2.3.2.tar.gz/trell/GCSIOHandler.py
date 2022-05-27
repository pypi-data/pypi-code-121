from google.cloud import storage
import os
from trell.utils import logger

class GCSIOHandler():

    def __init__(self, service_account_file_path=None):
        self.storage_client = storage.Client.from_service_account_json(service_account_file_path)


    def upload_to_bucket(self, blob_name=None, path_to_file=None, bucket_name=None):
        """ Upload data to a bucket"""

        try:
            bucket = self.storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(path_to_file)
            return True
        except Exception as e:
            print(str(e))
            print("Upload to gcs bucket was not Successfull")
            return  False

            
