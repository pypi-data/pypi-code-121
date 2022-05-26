from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic

T = TypeVar("T")

class WrappedClassInstance(Generic[T]):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, instance: T) -> None:
		pass

	@overload
	def __init__(self, instanceNullable: T, tClass: Class) -> None:
		pass

	@overload
	def getFieldValue(self, fieldName: str) -> object:
		pass

	@overload
	def getFieldValueAsClass(self, asClass: str, fieldName: str) -> object:
		pass

	@overload
	def setFieldValue(self, fieldName: str, fieldValue: object) -> None:
		pass

	@overload
	def setFieldValueAsClass(self, asClass: str, fieldName: str, fieldValue: object) -> None:
		pass

	@overload
	def invokeMethod(self, methodNameOrSig: str, params: List[object]) -> object:
		pass

	@overload
	def invokeMethodAsClass(self, asClass: str, methodNameOrSig: str, params: List[object]) -> object:
		pass

	@overload
	def getRawInstance(self) -> T:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def getRawClass(self) -> Class:
		"""
		Since: 1.6.5 
		"""
		pass

	pass


