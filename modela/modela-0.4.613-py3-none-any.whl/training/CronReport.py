import grpc
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import CronReport as MDCronReport
from github.com.metaprov.modelaapi.services.cronreport.v1.cronreport_pb2_grpc import CronReportServiceStub
from github.com.metaprov.modelaapi.services.cronreport.v1.cronreport_pb2 import CreateCronReportRequest, \
    UpdateCronReportRequest, \
    DeleteCronReportRequest, GetCronReportRequest, ListCronReportsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class CronReport(Resource):
    def __init__(self, item: MDCronReport = MDCronReport(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class CronReportClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: CronReportServiceStub = stub

    def create(self, cronreport: CronReport) -> bool:
        request = CreateCronReportRequest()
        request.cronreport.CopyFrom(cronreport.raw_message)
        try:
            response = self.__stub.CreateCronReport(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, cronreport: CronReport) -> bool:
        request = UpdateCronReportRequest()
        request.cronreport.CopyFrom(cronreport.raw_message)
        try:
            self.__stub.UpdateCronReport(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[CronReport, bool]:
        request = GetCronReportRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetCronReport(request)
            return CronReport(response.cronreport, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteCronReportRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteCronReport(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[CronReport], bool]:
        request = ListCronReportsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListCronReports(request)
            return [CronReport(item, self) for item in response.cronreports.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


