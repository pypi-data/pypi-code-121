import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import License as MDLicense
from github.com.metaprov.modelaapi.services.license.v1.license_pb2_grpc import LicenseServiceStub
from github.com.metaprov.modelaapi.services.license.v1.license_pb2 import CreateLicenseRequest, \
    UpdateLicenseRequest, \
    DeleteLicenseRequest, GetLicenseRequest, ListLicensesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class License(Resource):
    def __init__(self, item: MDLicense = MDLicense(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class LicenseClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: LicenseServiceStub = stub

    def create(self, license: License) -> bool:
        request = CreateLicenseRequest()
        request.license.CopyFrom(license.raw_message)
        try:
            response = self.__stub.CreateLicense(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, license: License) -> bool:
        request = UpdateLicenseRequest()
        request.license.CopyFrom(license.raw_message)
        try:
            self.__stub.UpdateLicense(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[License, bool]:
        request = GetLicenseRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetLicense(request)
            return License(response.license, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteLicenseRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteLicense(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[License], bool]:
        request = ListLicensesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListLicenses(request)
            return [License(item, self) for item in response.licenses.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


