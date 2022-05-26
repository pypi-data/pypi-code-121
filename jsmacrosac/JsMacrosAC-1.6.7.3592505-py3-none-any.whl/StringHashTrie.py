from typing import overload
from typing import List
from typing import TypeVar
from typing import Any
from typing import Set

T = TypeVar("T")

class StringHashTrie:
	"""Is this even faster than just iterating through a LinkedHashSet / HashSet at this point?
also should the node-length just always be 1?
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def size(self) -> int:
		pass

	@overload
	def isEmpty(self) -> bool:
		pass

	@overload
	def contains(self, o: object) -> bool:
		pass

	@overload
	def iterator(self) -> iter:
		pass

	@overload
	def toArray(self) -> List[str]:
		pass

	@overload
	def toArray(self, a: List[T]) -> List[T]:
		pass

	@overload
	def add(self, s: str) -> bool:
		pass

	@overload
	def remove(self, o: object) -> bool:
		"""this can make the StringHashTrie sparse, this can cause extra steps in lookup that are no longer needed,
at some point it would be best to rebase the StringHashTrie with 'new StringHashTrie().addAll(current.getAll())'

		Args:
			o: 
		"""
		pass

	@overload
	def containsAll(self, c: List[Any]) -> bool:
		pass

	@overload
	def containsAll(self, o: List[str]) -> bool:
		pass

	@overload
	def addAll(self, c: List[Any]) -> bool:
		pass

	@overload
	def addAll(self, o: List[str]) -> bool:
		pass

	@overload
	def removeAll(self, c: List[Any]) -> bool:
		pass

	@overload
	def removeAll(self, o: List[str]) -> bool:
		pass

	@overload
	def retainAll(self, c: List[Any]) -> bool:
		pass

	@overload
	def retainAll(self, o: List[str]) -> bool:
		pass

	@overload
	def clear(self) -> None:
		pass

	@overload
	def getAllWithPrefix(self, prefix: str) -> Set[str]:
		"""

		Args:
			prefix: prefix to search with 

		Returns:
			all elements that start with the given prefix 
		"""
		pass

	@overload
	def getAllWithPrefixCaseInsensitive(self, prefix: str) -> Set[str]:
		"""

		Args:
			prefix: prefix to search with 

		Returns:
			all elements that start with the given prefix (case insensitive) 
		"""
		pass

	@overload
	def getAll(self) -> Set[str]:
		"""all contained elements as a Set
		"""
		pass

	@overload
	def toString(self) -> str:
		"""

		Returns:
			json representation, mainly for debugging. 
		"""
		pass

	pass


