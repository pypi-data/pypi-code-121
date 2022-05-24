import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Connection as MDConnection
from github.com.metaprov.modelaapi.services.connection.v1.connection_pb2_grpc import ConnectionServiceStub
from github.com.metaprov.modelaapi.services.connection.v1.connection_pb2 import CreateConnectionRequest, \
    UpdateConnectionRequest, \
    DeleteConnectionRequest, GetConnectionRequest, ListConnectionsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Connection(Resource):
    def __init__(self, item: MDConnection = MDConnection(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class ConnectionClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ConnectionServiceStub = stub

    def create(self, connection: Connection) -> bool:
        request = CreateConnectionRequest()
        request.connection.CopyFrom(connection.raw_message)
        try:
            response = self.__stub.CreateConnection(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, connection: Connection) -> bool:
        request = UpdateConnectionRequest()
        request.connection.CopyFrom(connection.raw_message)
        try:
            self.__stub.UpdateConnection(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Connection, bool]:
        request = GetConnectionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetConnection(request)
            return Connection(response.connection, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteConnectionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteConnection(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Connection], bool]:
        request = ListConnectionsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListConnections(request)
            return [Connection(item, self) for item in response.connections.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


