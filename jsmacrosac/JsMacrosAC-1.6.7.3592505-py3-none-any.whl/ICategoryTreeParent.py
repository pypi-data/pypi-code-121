from typing import overload
from typing import List
from .IContainerParent import IContainerParent


class ICategoryTreeParent(IContainerParent):

	@overload
	def selectCategory(self, category: List[str]) -> None:
		pass

	pass


