from typing import overload
from typing import TypeVar
from typing import Generic

T = TypeVar("T")
U = TypeVar("U")

class Pair(Generic[T, U]):

	@overload
	def __init__(self, t: T, u: U) -> None:
		pass

	@overload
	def setU(self, u: U) -> None:
		pass

	@overload
	def setT(self, t: T) -> None:
		pass

	@overload
	def getU(self) -> U:
		pass

	@overload
	def getT(self) -> T:
		pass

	pass


