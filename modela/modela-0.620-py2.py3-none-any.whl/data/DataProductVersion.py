import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import DataProductVersion as MDDataProductVersion
from github.com.metaprov.modelaapi.services.dataproductversion.v1.dataproductversion_pb2_grpc import DataProductVersionServiceStub
from github.com.metaprov.modelaapi.services.dataproductversion.v1.dataproductversion_pb2 import CreateDataProductVersionRequest, \
    UpdateDataProductVersionRequest, \
    DeleteDataProductVersionRequest, GetDataProductVersionRequest, ListDataProductVersionsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union

from modela.data.models import DataProductVersionSpec


class DataProductVersion(Resource):
    def __init__(self, item: MDDataProductVersion = MDDataProductVersion(), client=None, namespace="", name="",
                baseline: bool = False, previous_version: str = None):
        """
        :param client: The Data Product Version client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param baseline: If this version is baseline, then the objects of previous version will be garbage collected.
        :param previous_version: The name of the previous version.
        """
        super().__init__(item, client, namespace=namespace, name=name)

    @property
    def spec(self) -> DataProductVersionSpec:
        return DataProductVersionSpec().copy_from(self._object.spec).set_parent(self._object.spec)

    def default(self):
        DataProductVersionSpec().apply_config(self._object.spec)



class DataProductVersionClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: DataProductVersionServiceStub = stub

    def create(self, dataproductversion: DataProductVersion) -> bool:
        request = CreateDataProductVersionRequest()
        request.dataproductversion.CopyFrom(dataproductversion.raw_message)
        try:
            response = self.__stub.CreateDataProductVersion(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, dataproductversion: DataProductVersion) -> bool:
        request = UpdateDataProductVersionRequest()
        request.dataproductversion.CopyFrom(dataproductversion.raw_message)
        try:
            self.__stub.UpdateDataProductVersion(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[DataProductVersion, bool]:
        request = GetDataProductVersionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDataProductVersion(request)
            return DataProductVersion(response.dataproductversion, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteDataProductVersionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteDataProductVersion(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[DataProductVersion], bool]:
        request = ListDataProductVersionsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListDataProductVersions(request)
            return [DataProductVersion(item, self) for item in response.dataproductversions.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


