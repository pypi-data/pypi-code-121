from typing import overload
from typing import TypeVar

RecipeBookResults = TypeVar["net.minecraft.client.gui.screen.recipebook.RecipeBookResults"]

class IRecipeBookWidget:

	@overload
	def jsmacros_getResults(self) -> RecipeBookResults:
		pass

	@overload
	def jsmacros_isSearching(self) -> bool:
		pass

	@overload
	def jsmacros_refreshResultList(self) -> None:
		pass

	pass


