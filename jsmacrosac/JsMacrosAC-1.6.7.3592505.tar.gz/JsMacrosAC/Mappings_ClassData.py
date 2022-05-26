from typing import overload
from typing import Mapping
from .Mappings_MethodData import Mappings_MethodData


class Mappings_ClassData:
	methods: Mapping[str, Mappings_MethodData]
	fields: Mapping[str, str]
	name: str

	@overload
	def __init__(self, name: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


