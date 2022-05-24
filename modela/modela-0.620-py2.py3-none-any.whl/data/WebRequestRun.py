import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import WebRequestRun as MDWebRequestRun
from github.com.metaprov.modelaapi.services.webrequestrun.v1.webrequestrun_pb2_grpc import WebRequestRunServiceStub
from github.com.metaprov.modelaapi.services.webrequestrun.v1.webrequestrun_pb2 import CreateWebRequestRunRequest, \
    UpdateWebRequestRunRequest, \
    DeleteWebRequestRunRequest, GetWebRequestRunRequest, ListWebRequestRunsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class WebRequestRun(Resource):
    def __init__(self, item: MDWebRequestRun = MDWebRequestRun(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class WebRequestRunClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: WebRequestRunServiceStub = stub

    def create(self, webrequestrun: WebRequestRun) -> bool:
        request = CreateWebRequestRunRequest()
        request.webrequestrun.CopyFrom(webrequestrun.raw_message)
        try:
            response = self.__stub.CreateWebRequestRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, webrequestrun: WebRequestRun) -> bool:
        request = UpdateWebRequestRunRequest()
        request.webrequestrun.CopyFrom(webrequestrun.raw_message)
        try:
            self.__stub.UpdateWebRequestRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[WebRequestRun, bool]:
        request = GetWebRequestRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetWebRequestRun(request)
            return WebRequestRun(response.webrequestrun, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteWebRequestRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteWebRequestRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[WebRequestRun], bool]:
        request = ListWebRequestRunsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListWebRequestRuns(request)
            return [WebRequestRun(item, self) for item in response.webrequestruns.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


