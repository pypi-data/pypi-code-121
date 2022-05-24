import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import VirtualVolume as MDVirtualVolume
from github.com.metaprov.modelaapi.services.virtualvolume.v1.virtualvolume_pb2_grpc import VirtualVolumeServiceStub
from github.com.metaprov.modelaapi.services.virtualvolume.v1.virtualvolume_pb2 import CreateVirtualVolumeRequest, \
    UpdateVirtualVolumeRequest, \
    DeleteVirtualVolumeRequest, GetVirtualVolumeRequest, ListVirtualVolumesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class VirtualVolume(Resource):
    def __init__(self, item: MDVirtualVolume = MDVirtualVolume(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class VirtualVolumeClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: VirtualVolumeServiceStub = stub

    def create(self, virtualvolume: VirtualVolume) -> bool:
        request = CreateVirtualVolumeRequest()
        request.virtualvolume.CopyFrom(virtualvolume.raw_message)
        try:
            response = self.__stub.CreateVirtualVolume(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, virtualvolume: VirtualVolume) -> bool:
        request = UpdateVirtualVolumeRequest()
        request.virtualvolume.CopyFrom(virtualvolume.raw_message)
        try:
            self.__stub.UpdateVirtualVolume(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[VirtualVolume, bool]:
        request = GetVirtualVolumeRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetVirtualVolume(request)
            return VirtualVolume(response.virtualvolume, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteVirtualVolumeRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteVirtualVolume(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[VirtualVolume], bool]:
        request = ListVirtualVolumesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListVirtualVolumes(request)
            return [VirtualVolume(item, self) for item in response.virtualvolumes.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


