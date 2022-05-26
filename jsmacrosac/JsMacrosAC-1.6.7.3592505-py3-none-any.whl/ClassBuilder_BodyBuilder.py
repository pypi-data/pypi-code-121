from typing import overload
from .MethodWrapper import MethodWrapper
from .ClassBuilder import ClassBuilder


class ClassBuilder_BodyBuilder:

	@overload
	def appendJavaCode(self, code: str) -> "ClassBuilder_BodyBuilder":
		pass

	@overload
	def appendGuestCode(self, code: MethodWrapper, argsAsObjects: str, tokenBefore: str) -> "ClassBuilder_BodyBuilder":
		"""

		Args:
			code: 
			argsAsObjects: 
			tokenBefore: ie, "return", "Object wasd = " etc 
		"""
		pass

	@overload
	def finish(self) -> "ClassBuilder":
		pass

	pass


