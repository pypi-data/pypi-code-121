from typing import overload
from typing import Mapping
from .Library import Library
from .BaseLibrary import BaseLibrary
from .PerLanguageLibrary import PerLanguageLibrary
from .BaseLanguage import BaseLanguage
from .BaseScriptContext import BaseScriptContext


class LibraryRegistry:
	libraries: Mapping[Library, BaseLibrary]
	perExec: Mapping[Library, Class]
	perLanguage: Mapping[Class, Mapping[Library, PerLanguageLibrary]]
	perExecLanguage: Mapping[Class, Mapping[Library, Class]]

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getLibraries(self, language: BaseLanguage, context: BaseScriptContext) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def getOnceLibraries(self, language: BaseLanguage) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def getPerExecLibraries(self, language: BaseLanguage, context: BaseScriptContext) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def addLibrary(self, clazz: Class) -> None:
		pass

	pass


