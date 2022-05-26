from typing import overload
from typing import TypeVar
from typing import Generic
from .BasicFilter import BasicFilter
from .IFilter import IFilter

T = TypeVar("T")

class NotFilter(Generic[T], BasicFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, filter: IFilter) -> None:
		pass

	@overload
	def apply(self, obj: T) -> bool:
		pass

	@overload
	def getFilter(self) -> IFilter:
		pass

	pass


