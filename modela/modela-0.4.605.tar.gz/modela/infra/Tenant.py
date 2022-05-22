import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Tenant as MDTenant
from github.com.metaprov.modelaapi.services.tenant.v1.tenant_pb2_grpc import TenantServiceStub
from github.com.metaprov.modelaapi.services.tenant.v1.tenant_pb2 import CreateTenantRequest, \
    UpdateTenantRequest, \
    DeleteTenantRequest, GetTenantRequest, ListTenantsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Tenant(Resource):
    def __init__(self, item: MDTenant = MDTenant(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class TenantClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: TenantServiceStub = stub

    def create(self, tenant: Tenant) -> bool:
        request = CreateTenantRequest()
        request.tenant.CopyFrom(tenant.raw_message)
        try:
            response = self.__stub.CreateTenant(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, tenant: Tenant) -> bool:
        request = UpdateTenantRequest()
        request.tenant.CopyFrom(tenant.raw_message)
        try:
            self.__stub.UpdateTenant(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Tenant, bool]:
        request = GetTenantRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetTenant(request)
            return Tenant(response.tenant, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteTenantRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteTenant(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Tenant], bool]:
        request = ListTenantsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListTenants(request)
            return [Tenant(item, self) for item in response.tenants.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


