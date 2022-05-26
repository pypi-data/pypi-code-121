from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .IFilter import IFilter

T = TypeVar("T")

class GroupFilter(IFilter, Generic[T]):
	"""
	Since: 1.6.5 
	"""

	@overload
	def add(self, filter: IFilter) -> "GroupFilter":
		pass

	@overload
	def add(self, filters: List[IFilter]) -> "GroupFilter":
		pass

	@overload
	def remove(self, filter: IFilter) -> "GroupFilter":
		pass

	@overload
	def remove(self, filters: List[IFilter]) -> "GroupFilter":
		pass

	@overload
	def getFilters(self) -> List[IFilter]:
		pass

	pass


