import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import VirtualBucket as MDVirtualBucket
from github.com.metaprov.modelaapi.services.virtualbucket.v1.virtualbucket_pb2_grpc import VirtualBucketServiceStub
from github.com.metaprov.modelaapi.services.virtualbucket.v1.virtualbucket_pb2 import CreateVirtualBucketRequest, \
    UpdateVirtualBucketRequest, \
    DeleteVirtualBucketRequest, GetVirtualBucketRequest, ListVirtualBucketsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class VirtualBucket(Resource):
    def __init__(self, item: MDVirtualBucket = MDVirtualBucket(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class VirtualBucketClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: VirtualBucketServiceStub = stub

    def create(self, virtualbucket: VirtualBucket) -> bool:
        request = CreateVirtualBucketRequest()
        request.virtualbucket.CopyFrom(virtualbucket.raw_message)
        try:
            response = self.__stub.CreateVirtualBucket(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, virtualbucket: VirtualBucket) -> bool:
        request = UpdateVirtualBucketRequest()
        request.virtualbucket.CopyFrom(virtualbucket.raw_message)
        try:
            self.__stub.UpdateVirtualBucket(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[VirtualBucket, bool]:
        request = GetVirtualBucketRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetVirtualBucket(request)
            return VirtualBucket(response.virtualbucket, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteVirtualBucketRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteVirtualBucket(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[VirtualBucket], bool]:
        request = ListVirtualBucketsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListVirtualBuckets(request)
            return [VirtualBucket(item, self) for item in response.virtualbuckets.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


