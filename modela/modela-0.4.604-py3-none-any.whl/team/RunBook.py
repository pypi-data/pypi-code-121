import grpc
from github.com.metaprov.modelaapi.pkg.apis.team.v1alpha1.generated_pb2 import RunBook as MDRunBook
from github.com.metaprov.modelaapi.services.runbook.v1.runbook_pb2_grpc import RunBookServiceStub
from github.com.metaprov.modelaapi.services.runbook.v1.runbook_pb2 import CreateRunBookRequest, \
    UpdateRunBookRequest, \
    DeleteRunBookRequest, GetRunBookRequest, ListRunBooksRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class RunBook(Resource):
    def __init__(self, item: MDRunBook = MDRunBook(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class RunBookClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: RunBookServiceStub = stub

    def create(self, runbook: RunBook) -> bool:
        request = CreateRunBookRequest()
        request.runbook.CopyFrom(runbook.raw_message)
        try:
            response = self.__stub.CreateRunBook(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, runbook: RunBook) -> bool:
        request = UpdateRunBookRequest()
        request.runbook.CopyFrom(runbook.raw_message)
        try:
            self.__stub.UpdateRunBook(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[RunBook, bool]:
        request = GetRunBookRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetRunBook(request)
            return RunBook(response.runbook, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteRunBookRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteRunBook(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[RunBook], bool]:
        request = ListRunBooksRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListRunBooks(request)
            return [RunBook(item, self) for item in response.runbooks.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


