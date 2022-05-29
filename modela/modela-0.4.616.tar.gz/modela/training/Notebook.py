import grpc
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import Notebook as MDNotebook
from github.com.metaprov.modelaapi.services.notebook.v1.notebook_pb2_grpc import NotebookServiceStub
from github.com.metaprov.modelaapi.services.notebook.v1.notebook_pb2 import CreateNotebookRequest, \
    UpdateNotebookRequest, \
    DeleteNotebookRequest, GetNotebookRequest, ListNotebooksRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Notebook(Resource):
    def __init__(self, item: MDNotebook = MDNotebook(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class NotebookClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: NotebookServiceStub = stub

    def create(self, notebook: Notebook) -> bool:
        request = CreateNotebookRequest()
        request.notebook.CopyFrom(notebook.raw_message)
        try:
            response = self.__stub.CreateNotebook(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, notebook: Notebook) -> bool:
        request = UpdateNotebookRequest()
        request.notebook.CopyFrom(notebook.raw_message)
        try:
            self.__stub.UpdateNotebook(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Notebook, bool]:
        request = GetNotebookRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetNotebook(request)
            return Notebook(response.notebook, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteNotebookRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteNotebook(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Notebook], bool]:
        request = ListNotebooksRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListNotebooks(request)
            return [Notebook(item, self) for item in response.notebooks.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


