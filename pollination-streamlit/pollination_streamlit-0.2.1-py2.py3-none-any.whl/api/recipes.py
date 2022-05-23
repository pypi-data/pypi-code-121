
from pydantic import BaseConfig
from queenbee.recipe import Recipe

from ._base import APIBase

BaseConfig.allow_population_by_field_name = True


class RecipesAPI(APIBase):

    def get_recipe(self, owner: str, name: str, tag: str = 'latest') -> Recipe:
        res = self.client.get(
            path=f'/registries/{owner}/recipe/{name}/{tag}/json'
        )
        return Recipe.parse_obj(res)
