import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import ApiToken as MDApiToken
from github.com.metaprov.modelaapi.services.apitoken.v1.apitoken_pb2_grpc import ApiTokenServiceStub
from github.com.metaprov.modelaapi.services.apitoken.v1.apitoken_pb2 import CreateApiTokenRequest, \
    UpdateApiTokenRequest, \
    DeleteApiTokenRequest, GetApiTokenRequest, ListApiTokensRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class ApiToken(Resource):
    def __init__(self, item: MDApiToken = MDApiToken(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class ApiTokenClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ApiTokenServiceStub = stub

    def create(self, apitoken: ApiToken) -> bool:
        request = CreateApiTokenRequest()
        request.apitoken.CopyFrom(apitoken.raw_message)
        try:
            response = self.__stub.CreateApiToken(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, apitoken: ApiToken) -> bool:
        request = UpdateApiTokenRequest()
        request.apitoken.CopyFrom(apitoken.raw_message)
        try:
            self.__stub.UpdateApiToken(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[ApiToken, bool]:
        request = GetApiTokenRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetApiToken(request)
            return ApiToken(response.apitoken, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteApiTokenRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteApiToken(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[ApiToken], bool]:
        request = ListApiTokensRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListApiTokens(request)
            return [ApiToken(item, self) for item in response.apitokens.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


