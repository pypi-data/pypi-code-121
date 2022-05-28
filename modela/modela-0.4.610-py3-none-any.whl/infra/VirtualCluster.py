import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import VirtualCluster as MDVirtualCluster
from github.com.metaprov.modelaapi.services.virtualcluster.v1.virtualcluster_pb2_grpc import VirtualClusterServiceStub
from github.com.metaprov.modelaapi.services.virtualcluster.v1.virtualcluster_pb2 import CreateVirtualClusterRequest, \
    UpdateVirtualClusterRequest, \
    DeleteVirtualClusterRequest, GetVirtualClusterRequest, ListVirtualClustersRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class VirtualCluster(Resource):
    def __init__(self, item: MDVirtualCluster = MDVirtualCluster(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class VirtualClusterClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: VirtualClusterServiceStub = stub

    def create(self, virtualcluster: VirtualCluster) -> bool:
        request = CreateVirtualClusterRequest()
        request.virtualcluster.CopyFrom(virtualcluster.raw_message)
        try:
            response = self.__stub.CreateVirtualCluster(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, virtualcluster: VirtualCluster) -> bool:
        request = UpdateVirtualClusterRequest()
        request.virtualcluster.CopyFrom(virtualcluster.raw_message)
        try:
            self.__stub.UpdateVirtualCluster(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[VirtualCluster, bool]:
        request = GetVirtualClusterRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetVirtualCluster(request)
            return VirtualCluster(response.virtualcluster, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteVirtualClusterRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteVirtualCluster(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[VirtualCluster], bool]:
        request = ListVirtualClustersRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListVirtualClusters(request)
            return [VirtualCluster(item, self) for item in response.virtualclusters.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


