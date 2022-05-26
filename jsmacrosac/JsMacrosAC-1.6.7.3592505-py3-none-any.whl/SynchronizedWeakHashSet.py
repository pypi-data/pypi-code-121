from typing import overload
from typing import TypeVar
from typing import Generic

Serializable = TypeVar["java.io.Serializable"]
E = TypeVar("E")
AbstractSet = TypeVar["java.util.AbstractSet_E_"]

class SynchronizedWeakHashSet(Serializable, Generic[E], AbstractSet):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def size(self) -> int:
		pass

	@overload
	def contains(self, o: object) -> bool:
		pass

	@overload
	def add(self, o: E) -> bool:
		pass

	@overload
	def remove(self, o: object) -> bool:
		pass

	@overload
	def clear(self) -> None:
		pass

	@overload
	def iterator(self) -> iter:
		pass

	pass


