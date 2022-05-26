from typing import overload
from typing import List
from typing import TypeVar
from .IRecipeBookResults import IRecipeBookResults

RecipeResultCollection = TypeVar["net.minecraft.client.gui.screen.recipebook.RecipeResultCollection"]

class MixinRecipeBookResults(IRecipeBookResults):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getResultCollections(self) -> List[RecipeResultCollection]:
		pass

	pass


