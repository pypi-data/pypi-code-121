import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import Entity as MDEntity
from github.com.metaprov.modelaapi.services.entity.v1.entity_pb2_grpc import EntityServiceStub
from github.com.metaprov.modelaapi.services.entity.v1.entity_pb2 import CreateEntityRequest, \
    UpdateEntityRequest, \
    DeleteEntityRequest, GetEntityRequest, ListEntitiesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Entity(Resource):
    def __init__(self, item: MDEntity = MDEntity(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class EntityClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: EntityServiceStub = stub

    def create(self, entity: Entity) -> bool:
        request = CreateEntityRequest()
        request.entity.CopyFrom(entity.raw_message)
        try:
            response = self.__stub.CreateEntity(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, entity: Entity) -> bool:
        request = UpdateEntityRequest()
        request.entity.CopyFrom(entity.raw_message)
        try:
            self.__stub.UpdateEntity(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Entity, bool]:
        request = GetEntityRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetEntity(request)
            return Entity(response.entity, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteEntityRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteEntity(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Entity], bool]:
        request = ListEntitiesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListEntitys(request)
            return [Entity(item, self) for item in response.entitys.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


