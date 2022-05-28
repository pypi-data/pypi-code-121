import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import Recipe as MDRecipe
from github.com.metaprov.modelaapi.services.recipe.v1.recipe_pb2_grpc import RecipeServiceStub
from github.com.metaprov.modelaapi.services.recipe.v1.recipe_pb2 import CreateRecipeRequest, \
    UpdateRecipeRequest, \
    DeleteRecipeRequest, GetRecipeRequest, ListRecipesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Recipe(Resource):
    def __init__(self, item: MDRecipe = MDRecipe(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class RecipeClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: RecipeServiceStub = stub

    def create(self, recipe: Recipe) -> bool:
        request = CreateRecipeRequest()
        request.recipe.CopyFrom(recipe.raw_message)
        try:
            response = self.__stub.CreateRecipe(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, recipe: Recipe) -> bool:
        request = UpdateRecipeRequest()
        request.recipe.CopyFrom(recipe.raw_message)
        try:
            self.__stub.UpdateRecipe(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Recipe, bool]:
        request = GetRecipeRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetRecipe(request)
            return Recipe(response.recipe, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteRecipeRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteRecipe(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Recipe], bool]:
        request = ListRecipesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListRecipes(request)
            return [Recipe(item, self) for item in response.recipes.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


