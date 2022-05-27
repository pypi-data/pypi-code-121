import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import ServingSite as MDServingSite
from github.com.metaprov.modelaapi.services.servingsite.v1.servingsite_pb2_grpc import ServingSiteServiceStub
from github.com.metaprov.modelaapi.services.servingsite.v1.servingsite_pb2 import CreateServingSiteRequest, \
    UpdateServingSiteRequest, \
    DeleteServingSiteRequest, GetServingSiteRequest, ListServingSitesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class ServingSite(Resource):
    def __init__(self, item: MDServingSite = MDServingSite(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class ServingSiteClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ServingSiteServiceStub = stub

    def create(self, servingsite: ServingSite) -> bool:
        request = CreateServingSiteRequest()
        request.servingsite.CopyFrom(servingsite.raw_message)
        try:
            response = self.__stub.CreateServingSite(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, servingsite: ServingSite) -> bool:
        request = UpdateServingSiteRequest()
        request.servingsite.CopyFrom(servingsite.raw_message)
        try:
            self.__stub.UpdateServingSite(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[ServingSite, bool]:
        request = GetServingSiteRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetServingSite(request)
            return ServingSite(response.servingsite, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteServingSiteRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteServingSite(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[ServingSite], bool]:
        request = ListServingSitesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListServingSites(request)
            return [ServingSite(item, self) for item in response.servingsites.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


