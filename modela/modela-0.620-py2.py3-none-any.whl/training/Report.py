import os
import time

import grpc
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import Report as MDReport
from github.com.metaprov.modelaapi.services.report.v1.report_pb2_grpc import ReportServiceStub
from github.com.metaprov.modelaapi.services.report.v1.report_pb2 import CreateReportRequest, \
    UpdateReportRequest, DeleteReportRequest, GetReportRequest, ListReportsRequest, DownloadReportRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union

from modela.training.models import ReportSpec, ReportStatus
import tempfile
import webbrowser

class Report(Resource):
    def __init__(self, item: MDReport = MDReport(), client=None, namespace="", name=""):
        """
        :param client: The Report client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        """

        super().__init__(item, client, namespace=namespace, name=name)

    @property
    def spec(self) -> ReportSpec:
        return ReportSpec().copy_from(self._object.spec)

    @property
    def status(self) -> ReportStatus:
        return ReportStatus().copy_from(self._object.status)

    def default(self):
        raise TypeError("Report {0} was not found; report resources cannot be created.".format(self.name))

    def submit(self):
        raise TypeError("Report resources cannot be created.")

    def update(self):
        raise TypeError("Report resources cannot be updated.")

    def download(self) -> bytes:
        self.ensure_client_repository()
        return self._client.download(self.namespace, self.name)

    def open_in_browser(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, '{0}.pdf'.format(self.name))
            with open(temp_file_path, 'wb+') as fh:
                fh.write(self.download())

            webbrowser.open('file://' + temp_file_path)
            time.sleep(1)



class ReportClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ReportServiceStub = stub

    def create(self, report: Report) -> bool:
        raise TypeError("Modela currently does not support the creation of custom models.")
        # request = CreateReportRequest()
        # request.report.CopyFrom(report.raw_message)
        # try:
        #     response = self.__stub.CreateReport(request)
        #     return True
        # except grpc.RpcError as err:
        #     error = err
        #
        # ModelaException.process_error(error)
        # return False

    def update(self, report: Report) -> bool:
        raise TypeError("Report resources cannot be changed after creation.")
        # request = UpdateReportRequest()
        # request.report.CopyFrom(report.raw_message)
        # try:
        #     self.__stub.UpdateReport(request)
        #     return True
        # except grpc.RpcError as err:
        #     error = err
        #
        # ModelaException.process_error(error)
        # return False

    def get(self, namespace: str, name: str) -> Union[Report, bool]:
        request = GetReportRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetReport(request)
            return Report(response.report, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteReportRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteReport(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str, labels: dict = None) -> Union[List[Report], bool]:
        request = ListReportsRequest()
        request.namespace = namespace
        if labels is not None:
            request.labels.update(labels)

        try:
            response = self.__stub.ListReports(request)
            return [Report(item, self) for item in response.reports.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def download(self, namespace: str, name: str) -> bytes:
        request = DownloadReportRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.Download(request)
            return response.raw
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)