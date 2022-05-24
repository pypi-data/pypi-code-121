import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import SqlQueryRun as MDSqlQueryRun
from github.com.metaprov.modelaapi.services.sqlqueryrun.v1.sqlqueryrun_pb2_grpc import SqlQueryRunServiceStub
from github.com.metaprov.modelaapi.services.sqlqueryrun.v1.sqlqueryrun_pb2 import CreateSqlQueryRunRequest, \
    UpdateSqlQueryRunRequest, \
    DeleteSqlQueryRunRequest, GetSqlQueryRunRequest, ListSqlQueryRunsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class SqlQueryRun(Resource):
    def __init__(self, item: MDSqlQueryRun = MDSqlQueryRun(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class SqlQueryRunClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: SqlQueryRunServiceStub = stub

    def create(self, sqlqueryrun: SqlQueryRun) -> bool:
        request = CreateSqlQueryRunRequest()
        request.sqlqueryrun.CopyFrom(sqlqueryrun.raw_message)
        try:
            response = self.__stub.CreateSqlQueryRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, sqlqueryrun: SqlQueryRun) -> bool:
        request = UpdateSqlQueryRunRequest()
        request.sqlqueryrun.CopyFrom(sqlqueryrun.raw_message)
        try:
            self.__stub.UpdateSqlQueryRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[SqlQueryRun, bool]:
        request = GetSqlQueryRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetSqlQueryRun(request)
            return SqlQueryRun(response.sqlqueryrun, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteSqlQueryRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteSqlQueryRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[SqlQueryRun], bool]:
        request = ListSqlQueryRunsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListSqlQueryRuns(request)
            return [SqlQueryRun(item, self) for item in response.sqlqueryruns.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


