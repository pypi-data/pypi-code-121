import grpc
from github.com.metaprov.modelaapi.pkg.apis.inference.v1alpha1.generated_pb2 import Curtain as MDCurtain
from github.com.metaprov.modelaapi.services.curtain.v1.curtain_pb2_grpc import CurtainServiceStub
from github.com.metaprov.modelaapi.services.curtain.v1.curtain_pb2 import CreateCurtainRequest, \
    UpdateCurtainRequest, \
    DeleteCurtainRequest, GetCurtainRequest, ListCurtainsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Curtain(Resource):
    def __init__(self, item: MDCurtain = MDCurtain(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class CurtainClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: CurtainServiceStub = stub

    def create(self, curtain: Curtain) -> bool:
        request = CreateCurtainRequest()
        request.curtain.CopyFrom(curtain.raw_message)
        try:
            response = self.__stub.CreateCurtain(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, curtain: Curtain) -> bool:
        request = UpdateCurtainRequest()
        request.curtain.CopyFrom(curtain.raw_message)
        try:
            self.__stub.UpdateCurtain(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Curtain, bool]:
        request = GetCurtainRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetCurtain(request)
            return Curtain(response.curtain, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteCurtainRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteCurtain(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Curtain], bool]:
        request = ListCurtainsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListCurtains(request)
            return [Curtain(item, self) for item in response.curtains.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


