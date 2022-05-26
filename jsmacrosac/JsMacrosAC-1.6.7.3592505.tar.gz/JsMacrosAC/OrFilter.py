from typing import overload
from typing import TypeVar
from typing import Generic
from .BasicFilter import BasicFilter
from .IFilter import IFilter

T = TypeVar("T")

class OrFilter(Generic[T], BasicFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, filterOne: IFilter, filterTwo: IFilter) -> None:
		pass

	@overload
	def apply(self, obj: T) -> bool:
		pass

	@overload
	def getFilterOne(self) -> IFilter:
		pass

	@overload
	def getFilterTwo(self) -> IFilter:
		pass

	pass


