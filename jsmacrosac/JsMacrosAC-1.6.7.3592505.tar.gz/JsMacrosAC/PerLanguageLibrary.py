from typing import overload
from .BaseLibrary import BaseLibrary


class PerLanguageLibrary(BaseLibrary):

	@overload
	def __init__(self, language: Class) -> None:
		pass

	pass


