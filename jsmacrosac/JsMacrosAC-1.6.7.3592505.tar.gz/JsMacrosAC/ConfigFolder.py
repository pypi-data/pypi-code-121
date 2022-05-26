from typing import overload
from typing import TypeVar

File = TypeVar["java.io.File"]

class ConfigFolder:

	@overload
	def getFolder(self) -> File:
		pass

	pass


