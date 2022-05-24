import hashlib

import grpc
from github.com.metaprov.modelaapi.services.fileservices.v1.fileservices_pb2 import DataBlock
from github.com.metaprov.modelaapi.services.fileservices.v1.fileservices_pb2_grpc import FileServicesServiceStub

from modela.data.models import DataLocation
from modela.ModelaException import ModelaException
from tqdm import *

class DataBlockRequestIterable(object):
    BLOCK_SIZE = 200000

    def __init__(self, name: str,
                 data: bytes,
                 tenant: str,
                 data_product: str,
                 version: str,
                 bucket: str,
                 resource_type: str,
                 resource_name: str):

        self.name = name
        self.data = data
        self.tenant = tenant
        self.data_product = data_product
        self.version = version
        self.bucket = bucket
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.loc = 0
        self.pbar = tqdm(total=len(data), desc="Uploading", unit="bytes", ncols=100)

    def __iter__(self):
        return self

    def __next__(self):
        data_block = self.data[self.loc:self.loc + self.BLOCK_SIZE]
        if len(data_block) > 0:
            hash = hashlib.new('md5', (data_block if type(data_block) == bytes else str(data_block).encode('utf-8'))).hexdigest()
            if type(data_block) == str:
                data_block = bytes(data_block, encoding='utf-8')
            request = DataBlock(
                name=self.name,
                data=data_block,
                md5_hash=str(hash),
                tenant=self.tenant,
                dataProductName=self.data_product,
                dataProductVersion=self.version,
                bucket=self.bucket,
                resourceType=self.resource_type,
                resourceName=self.resource_name
            )
            self.loc += self.BLOCK_SIZE
            self.pbar.update(min(self.BLOCK_SIZE, len(self.data)))
            return request
        else:
            self.pbar.update(min(self.BLOCK_SIZE, len(self.data)))
            raise StopIteration


class FileService:
    def __init__(self, stub):
        self.__stub: FileServicesServiceStub = stub

    def upload_file(self,
                    name: str,
                    data: bytes,
                    tenant: str,
                    data_product: str,
                    version: str,
                    bucket: str,
                    resource_type: str,
                    resource_name: str) -> DataLocation:
        data_block_iterable = DataBlockRequestIterable(name, data, tenant, data_product,
                                                       version, bucket, resource_type, resource_name)
        try:
            response = self.__stub.UploadChunk(data_block_iterable, timeout=20)
            return DataLocation(BucketName=bucket, Path=response.key)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
