import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import SqlQuery as MDSqlQuery
from github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2_grpc import SqlQueryServiceStub
from github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2 import CreateSqlQueryRequest, \
    UpdateSqlQueryRequest, \
    DeleteSqlQueryRequest, GetSqlQueryRequest, ListSqlQuerysRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class SqlQuery(Resource):
    def __init__(self, item: MDSqlQuery = MDSqlQuery(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class SqlQueryClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: SqlQueryServiceStub = stub

    def create(self, sqlquery: SqlQuery) -> bool:
        request = CreateSqlQueryRequest()
        request.sqlquery.CopyFrom(sqlquery.raw_message)
        try:
            response = self.__stub.CreateSqlQuery(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, sqlquery: SqlQuery) -> bool:
        request = UpdateSqlQueryRequest()
        request.sqlquery.CopyFrom(sqlquery.raw_message)
        try:
            self.__stub.UpdateSqlQuery(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[SqlQuery, bool]:
        request = GetSqlQueryRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetSqlQuery(request)
            return SqlQuery(response.sqlquery, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteSqlQueryRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteSqlQuery(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[SqlQuery], bool]:
        request = ListSqlQuerysRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListSqlQuerys(request)
            return [SqlQuery(item, self) for item in response.sqlquerys.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


