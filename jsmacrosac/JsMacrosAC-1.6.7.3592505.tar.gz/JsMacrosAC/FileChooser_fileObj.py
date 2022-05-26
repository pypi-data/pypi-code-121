from typing import overload
from typing import TypeVar
from .Button import Button

File = TypeVar["java.io.File"]

class FileChooser_fileObj:
	file: File
	btn: Button

	@overload
	def __init__(self, file: File, btn: Button) -> None:
		pass

	pass


