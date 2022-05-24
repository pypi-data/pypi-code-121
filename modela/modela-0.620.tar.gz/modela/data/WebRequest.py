import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import WebRequest as MDWebRequest
from github.com.metaprov.modelaapi.services.webrequest.v1.webrequest_pb2_grpc import WebRequestServiceStub
from github.com.metaprov.modelaapi.services.webrequest.v1.webrequest_pb2 import CreateWebRequestRequest, \
    UpdateWebRequestRequest, \
    DeleteWebRequestRequest, GetWebRequestRequest, ListWebRequestsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class WebRequest(Resource):
    def __init__(self, item: MDWebRequest = MDWebRequest(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class WebRequestClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: WebRequestServiceStub = stub

    def create(self, webrequest: WebRequest) -> bool:
        request = CreateWebRequestRequest()
        request.webrequest.CopyFrom(webrequest.raw_message)
        try:
            response = self.__stub.CreateWebRequest(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, webrequest: WebRequest) -> bool:
        request = UpdateWebRequestRequest()
        request.webrequest.CopyFrom(webrequest.raw_message)
        try:
            self.__stub.UpdateWebRequest(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[WebRequest, bool]:
        request = GetWebRequestRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetWebRequest(request)
            return WebRequest(response.webrequest, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteWebRequestRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteWebRequest(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[WebRequest], bool]:
        request = ListWebRequestsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListWebRequests(request)
            return [WebRequest(item, self) for item in response.webrequests.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


