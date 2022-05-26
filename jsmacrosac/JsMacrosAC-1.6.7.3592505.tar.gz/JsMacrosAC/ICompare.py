from typing import overload
from typing import TypeVar

T = TypeVar("T")

class ICompare:

	@overload
	def compare(self, obj1: T, obj2: T) -> bool:
		pass

	pass


