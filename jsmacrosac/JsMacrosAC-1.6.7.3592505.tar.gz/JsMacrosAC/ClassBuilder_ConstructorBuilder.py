from typing import overload
from typing import List
from .ClassBuilder_MethodBuilder import ClassBuilder_MethodBuilder
from .ClassBuilder import ClassBuilder
from .MethodWrapper import MethodWrapper
from .ClassBuilder_BodyBuilder import ClassBuilder_BodyBuilder


class ClassBuilder_ConstructorBuilder("ClassBuilder_MethodBuilder"):

	@overload
	def __init__(self, params: List[CtClass], clInit: bool) -> None:
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

	pass


