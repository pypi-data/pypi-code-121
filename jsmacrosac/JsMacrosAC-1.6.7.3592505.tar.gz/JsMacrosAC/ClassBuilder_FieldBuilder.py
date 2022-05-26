from typing import overload
from .ClassBuilder import ClassBuilder
from .ClassBuilder_AnnotationBuilder import ClassBuilder_AnnotationBuilder
from .ClassBuilder_FieldBuilder_FieldInitializerBuilder import ClassBuilder_FieldBuilder_FieldInitializerBuilder


class ClassBuilder_FieldBuilder:
	fieldInitializer: CtField_Initializer

	@overload
	def __init__(self, fieldType: CtClass, name: str) -> None:
		pass

	@overload
	def compile(self, code: str) -> "ClassBuilder":
		pass

	@overload
	def rename(self, name: str) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def makePrivate(self) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def makePublic(self) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def makeProtected(self) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def makePackagePrivate(self) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def toggleStatic(self) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def toggleFinal(self) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def getMods(self) -> int:
		pass

	@overload
	def getModString(self) -> str:
		pass

	@overload
	def addAnnotation(self, type: Class) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def initializer(self) -> "ClassBuilder_FieldBuilder_FieldInitializerBuilder":
		pass

	@overload
	def end(self) -> "ClassBuilder":
		pass

	pass


