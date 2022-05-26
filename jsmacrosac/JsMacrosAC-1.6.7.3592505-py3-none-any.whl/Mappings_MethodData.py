from typing import overload
from typing import TypeVar

Supplier = TypeVar["java.util.function.Supplier_java.lang.String_"]

class Mappings_MethodData:
	name: str
	sig: Supplier

	@overload
	def __init__(self, name: str, sig: Supplier) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


