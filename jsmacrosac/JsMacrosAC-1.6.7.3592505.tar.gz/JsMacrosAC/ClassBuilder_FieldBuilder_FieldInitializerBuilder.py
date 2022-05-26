from typing import overload
from typing import List
from .ClassBuilder_FieldBuilder import ClassBuilder_FieldBuilder


class ClassBuilder_FieldBuilder_FieldInitializerBuilder:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def setInt(self, value: int) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setLong(self, value: float) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setFloat(self, value: float) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setDouble(self, value: float) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setChar(self, value: str) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setString(self, value: str) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setBoolean(self, value: bool) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setByte(self, value: float) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def setShort(self, value: float) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def compile(self, code: str) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def initClass(self, clazz: Class, code_arg: List[str]) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def callStaticMethod(self, clazz: Class, methodName: str, code_arg: List[str]) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def callStaticMethodInThisClass(self, methodName: str, code_arg: List[str]) -> "ClassBuilder_FieldBuilder":
		pass

	pass


