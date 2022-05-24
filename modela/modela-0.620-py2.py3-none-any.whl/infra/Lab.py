import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Lab as MDLab
from github.com.metaprov.modelaapi.services.lab.v1.lab_pb2_grpc import LabServiceStub
from github.com.metaprov.modelaapi.services.lab.v1.lab_pb2 import CreateLabRequest, \
    UpdateLabRequest, \
    DeleteLabRequest, GetLabRequest, ListLabsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Lab(Resource):
    def __init__(self, item: MDLab = MDLab(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class LabClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: LabServiceStub = stub

    def create(self, lab: Lab) -> bool:
        request = CreateLabRequest()
        request.lab.CopyFrom(lab.raw_message)
        try:
            response = self.__stub.CreateLab(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, lab: Lab) -> bool:
        request = UpdateLabRequest()
        request.lab.CopyFrom(lab.raw_message)
        try:
            self.__stub.UpdateLab(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Lab, bool]:
        request = GetLabRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetLab(request)
            return Lab(response.lab, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteLabRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteLab(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Lab], bool]:
        request = ListLabsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListLabs(request)
            return [Lab(item, self) for item in response.labs.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


