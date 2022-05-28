import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import RecipeRun as MDRecipeRun
from github.com.metaprov.modelaapi.services.reciperun.v1.reciperun_pb2_grpc import RecipeRunServiceStub
from github.com.metaprov.modelaapi.services.reciperun.v1.reciperun_pb2 import CreateRecipeRunRequest, \
    UpdateRecipeRunRequest, \
    DeleteRecipeRunRequest, GetRecipeRunRequest, ListRecipeRunsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class RecipeRun(Resource):
    def __init__(self, item: MDRecipeRun = MDRecipeRun(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class RecipeRunClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: RecipeRunServiceStub = stub

    def create(self, reciperun: RecipeRun) -> bool:
        request = CreateRecipeRunRequest()
        request.reciperun.CopyFrom(reciperun.raw_message)
        try:
            response = self.__stub.CreateRecipeRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, reciperun: RecipeRun) -> bool:
        request = UpdateRecipeRunRequest()
        request.reciperun.CopyFrom(reciperun.raw_message)
        try:
            self.__stub.UpdateRecipeRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[RecipeRun, bool]:
        request = GetRecipeRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetRecipeRun(request)
            return RecipeRun(response.reciperun, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteRecipeRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteRecipeRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[RecipeRun], bool]:
        request = ListRecipeRunsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListRecipeRuns(request)
            return [RecipeRun(item, self) for item in response.reciperuns.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


