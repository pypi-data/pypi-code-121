import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import ModelaSystem as MDModelaSystem
from github.com.metaprov.modelaapi.services.modelasystem.v1.modelasystem_pb2_grpc import ModelaSystemServiceStub
from github.com.metaprov.modelaapi.services.modelasystem.v1.modelasystem_pb2 import CreateModelaSystemRequest, \
    UpdateModelaSystemRequest, \
    DeleteModelaSystemRequest, GetModelaSystemRequest, ListModelaSystemsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class ModelaSystem(Resource):
    def __init__(self, item: MDModelaSystem = MDModelaSystem(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class ModelaSystemClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ModelaSystemServiceStub = stub

    def create(self, modelasystem: ModelaSystem) -> bool:
        request = CreateModelaSystemRequest()
        request.modelasystem.CopyFrom(modelasystem.raw_message)
        try:
            response = self.__stub.CreateModelaSystem(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, modelasystem: ModelaSystem) -> bool:
        request = UpdateModelaSystemRequest()
        request.modelasystem.CopyFrom(modelasystem.raw_message)
        try:
            self.__stub.UpdateModelaSystem(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[ModelaSystem, bool]:
        request = GetModelaSystemRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetModelaSystem(request)
            return ModelaSystem(response.modelasystem, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteModelaSystemRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteModelaSystem(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[ModelaSystem], bool]:
        request = ListModelaSystemsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListModelaSystems(request)
            return [ModelaSystem(item, self) for item in response.modelasystems.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


