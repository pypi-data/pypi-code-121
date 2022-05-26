from typing import overload
from typing import TypeVar
from typing import Generic
from .WrappedClassInstance import WrappedClassInstance

T = TypeVar("T")

class Mappings_MappedClass(Generic[T], WrappedClassInstance):
	"""
	Since: 1.6.0 
	"""

	@overload
	def __init__(self, instance: T) -> None:
		pass

	@overload
	def __init__(self, instance: T, type: Class) -> None:
		pass

	pass


