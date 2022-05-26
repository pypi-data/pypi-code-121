from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper
from .ItemStackHelper import ItemStackHelper

Recipe = TypeVar["net.minecraft.recipe.Recipe__"]

class RecipeHelper(BaseHelper):
	"""
	Since: 1.3.1 
	"""

	@overload
	def __init__(self, base: Recipe, syncId: int) -> None:
		pass

	@overload
	def getId(self) -> str:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def getOutput(self) -> ItemStackHelper:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def craft(self, craftAll: bool) -> None:
		"""
		Since: 1.3.1 

		Args:
			craftAll: 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


