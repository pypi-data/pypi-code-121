from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .BasicFilter import BasicFilter

T = TypeVar("T")

class StringifyFilter(Generic[T], BasicFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, operation: str) -> None:
		pass

	@overload
	def addOption(self, toAdd: str) -> "StringifyFilter":
		pass

	@overload
	def addOption(self, toAdd: List[str]) -> "StringifyFilter":
		pass

	@overload
	def removeOption(self, toRemove: str) -> "StringifyFilter":
		pass

	@overload
	def removeOption(self, toRemove: List[str]) -> "StringifyFilter":
		pass

	@overload
	def apply(self, obj: object) -> bool:
		pass

	pass


