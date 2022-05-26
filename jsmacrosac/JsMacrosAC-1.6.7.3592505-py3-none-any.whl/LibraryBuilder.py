from typing import overload
from typing import List
from .ClassBuilder import ClassBuilder
from .ClassBuilder_ConstructorBuilder import ClassBuilder_ConstructorBuilder


class LibraryBuilder(ClassBuilder):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, name: str, perExec: bool, allowedLangs: List[str]) -> None:
		pass

	@overload
	def addConstructor(self) -> ClassBuilder_ConstructorBuilder:
		"""constructor, if perExec run every context, if per language run once for each lang;
params are context and language class
if not per exec, param will be skipped
ie:
BaseLibrary: no params
PerExecLibrary: context
PerExecLanguageLibrary: context, language
PerLanguageLibrary: language

Don't do other constructors...
		"""
		pass

	@overload
	def finishBuildAndFreeze(self) -> Class:
		pass

	pass


