from typing import overload
from typing import List
from typing import TypeVar

RecipeResultCollection = TypeVar["net.minecraft.client.gui.screen.recipebook.RecipeResultCollection"]

class IRecipeBookResults:

	@overload
	def jsmacros_getResultCollections(self) -> List[RecipeResultCollection]:
		pass

	pass


