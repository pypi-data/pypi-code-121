from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .BasicFilter import BasicFilter
from .IFilter import IFilter

T = TypeVar("T")

class ClassWrapperFilter(Generic[T], BasicFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def getFilter(self, clazz: Class, methodName: str, args: List[object]) -> IFilter:
		pass

	@overload
	def apply(self, t: T) -> bool:
		pass

	pass


