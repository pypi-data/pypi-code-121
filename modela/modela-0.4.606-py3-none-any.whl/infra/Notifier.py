import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Notifier as MDNotifier
from github.com.metaprov.modelaapi.services.notifier.v1.notifier_pb2_grpc import NotifierServiceStub
from github.com.metaprov.modelaapi.services.notifier.v1.notifier_pb2 import CreateNotifierRequest, \
    UpdateNotifierRequest, \
    DeleteNotifierRequest, GetNotifierRequest, ListNotifiersRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Notifier(Resource):
    def __init__(self, item: MDNotifier = MDNotifier(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class NotifierClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: NotifierServiceStub = stub

    def create(self, notifier: Notifier) -> bool:
        request = CreateNotifierRequest()
        request.notifier.CopyFrom(notifier.raw_message)
        try:
            response = self.__stub.CreateNotifier(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, notifier: Notifier) -> bool:
        request = UpdateNotifierRequest()
        request.notifier.CopyFrom(notifier.raw_message)
        try:
            self.__stub.UpdateNotifier(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Notifier, bool]:
        request = GetNotifierRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetNotifier(request)
            return Notifier(response.notifier, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteNotifierRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteNotifier(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Notifier], bool]:
        request = ListNotifiersRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListNotifiers(request)
            return [Notifier(item, self) for item in response.notifiers.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


