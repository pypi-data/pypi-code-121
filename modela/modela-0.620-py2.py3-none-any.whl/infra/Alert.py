import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Alert as MDAlert
from github.com.metaprov.modelaapi.services.alert.v1.alert_pb2_grpc import AlertServiceStub
from github.com.metaprov.modelaapi.services.alert.v1.alert_pb2 import CreateAlertRequest, \
    UpdateAlertRequest, \
    DeleteAlertRequest, GetAlertRequest, ListAlertsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Alert(Resource):
    def __init__(self, item: MDAlert = MDAlert(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class AlertClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: AlertServiceStub = stub

    def create(self, alert: Alert) -> bool:
        request = CreateAlertRequest()
        request.alert.CopyFrom(alert.raw_message)
        try:
            response = self.__stub.CreateAlert(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, alert: Alert) -> bool:
        request = UpdateAlertRequest()
        request.alert.CopyFrom(alert.raw_message)
        try:
            self.__stub.UpdateAlert(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Alert, bool]:
        request = GetAlertRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetAlert(request)
            return Alert(response.alert, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteAlertRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteAlert(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Alert], bool]:
        request = ListAlertsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListAlerts(request)
            return [Alert(item, self) for item in response.alerts.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


