import grpc
from github.com.metaprov.modelaapi.pkg.apis.inference.v1alpha1.generated_pb2 import DataApp as MDDataApp
from github.com.metaprov.modelaapi.services.dataapp.v1.dataapp_pb2_grpc import DataAppServiceStub
from github.com.metaprov.modelaapi.services.dataapp.v1.dataapp_pb2 import CreateDataAppRequest, \
    UpdateDataAppRequest, \
    DeleteDataAppRequest, GetDataAppRequest, ListDataAppsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class DataApp(Resource):
    def __init__(self, item: MDDataApp = MDDataApp(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class DataAppClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: DataAppServiceStub = stub

    def create(self, dataapp: DataApp) -> bool:
        request = CreateDataAppRequest()
        request.dataapp.CopyFrom(dataapp.raw_message)
        try:
            response = self.__stub.CreateDataApp(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, dataapp: DataApp) -> bool:
        request = UpdateDataAppRequest()
        request.dataapp.CopyFrom(dataapp.raw_message)
        try:
            self.__stub.UpdateDataApp(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[DataApp, bool]:
        request = GetDataAppRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDataApp(request)
            return DataApp(response.dataapp, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteDataAppRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteDataApp(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[DataApp], bool]:
        request = ListDataAppsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListDataApps(request)
            return [DataApp(item, self) for item in response.dataapps.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


