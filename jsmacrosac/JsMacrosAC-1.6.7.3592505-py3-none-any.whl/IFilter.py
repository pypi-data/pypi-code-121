from typing import overload
from typing import TypeVar
from typing import Generic

Function = TypeVar["java.util.function.Function_T,java.lang.Boolean_"]
T = TypeVar("T")

class IFilter(Function, Generic[T]):
	"""
	Since: 1.6.5 
	"""

	@overload
	def apply(self, t: T) -> bool:
		pass

	pass


