from typing import overload
from typing import TypeVar
from typing import Generic

Function = TypeVar["java.util.function.Function_java.lang.Object[],java.lang.Object_"]
T = TypeVar("T")

class ProxyBuilder_ProxyReference(Generic[T]):
	self: T
	parent: Function

	@overload
	def __init__(self, self: T, parent: Function) -> None:
		pass

	pass


