from typing import overload
from typing import TypeVar
from typing import Generic

T = TypeVar("T")

class BaseHelper(Generic[T]):

	@overload
	def __init__(self, base: T) -> None:
		pass

	@overload
	def getRaw(self) -> T:
		pass

	pass


