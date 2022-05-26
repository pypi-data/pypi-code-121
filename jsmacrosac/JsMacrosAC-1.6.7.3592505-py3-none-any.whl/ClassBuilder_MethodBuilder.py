from typing import overload
from typing import List
from .ClassBuilder import ClassBuilder
from .MethodWrapper import MethodWrapper
from .ClassBuilder_BodyBuilder import ClassBuilder_BodyBuilder
from .ClassBuilder_AnnotationBuilder import ClassBuilder_AnnotationBuilder


class ClassBuilder_MethodBuilder:

	@overload
	def __init__(self, methodReturnType: CtClass, methodName: str, params: List[CtClass]) -> None:
		pass

	@overload
	def compile(self, code: str) -> "ClassBuilder":
		pass

	@overload
	def makePrivate(self) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def makePublic(self) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def makeProtected(self) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def makePackagePrivate(self) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def toggleStatic(self) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def rename(self, newName: str) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def exceptions(self, exceptions: List[Class]) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def body(self, code_src: str) -> "ClassBuilder":
		pass

	@overload
	def guestBody(self, methodBody: MethodWrapper) -> "ClassBuilder":
		pass

	@overload
	def buildBody(self) -> "ClassBuilder_BodyBuilder":
		pass

	@overload
	def body(self, buildBody: MethodWrapper) -> "ClassBuilder":
		pass

	@overload
	def endAbstract(self) -> "ClassBuilder":
		pass

	@overload
	def addAnnotation(self, type: Class) -> "ClassBuilder_AnnotationBuilder":
		pass

	pass


