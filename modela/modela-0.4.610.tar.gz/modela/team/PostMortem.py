import grpc
from github.com.metaprov.modelaapi.pkg.apis.team.v1alpha1.generated_pb2 import PostMortem as MDPostMortem
from github.com.metaprov.modelaapi.services.postmortem.v1.postmortem_pb2_grpc import PostMortemServiceStub
from github.com.metaprov.modelaapi.services.postmortem.v1.postmortem_pb2 import CreatePostMortemRequest, \
    UpdatePostMortemRequest, \
    DeletePostMortemRequest, GetPostMortemRequest, ListPostMortemsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class PostMortem(Resource):
    def __init__(self, item: MDPostMortem = MDPostMortem(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class PostMortemClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: PostMortemServiceStub = stub

    def create(self, postmortem: PostMortem) -> bool:
        request = CreatePostMortemRequest()
        request.postmortem.CopyFrom(postmortem.raw_message)
        try:
            response = self.__stub.CreatePostMortem(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, postmortem: PostMortem) -> bool:
        request = UpdatePostMortemRequest()
        request.postmortem.CopyFrom(postmortem.raw_message)
        try:
            self.__stub.UpdatePostMortem(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[PostMortem, bool]:
        request = GetPostMortemRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetPostMortem(request)
            return PostMortem(response.postmortem, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeletePostMortemRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeletePostMortem(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[PostMortem], bool]:
        request = ListPostMortemsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListPostMortems(request)
            return [PostMortem(item, self) for item in response.postmortems.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


