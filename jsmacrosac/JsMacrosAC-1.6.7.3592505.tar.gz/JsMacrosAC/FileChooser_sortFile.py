from typing import overload
from typing import TypeVar

File = TypeVar["java.io.File"]
Comparator = TypeVar["java.util.Comparator_java.io.File_"]

class FileChooser_sortFile(Comparator):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def compare(self, a: File, b: File) -> int:
		pass

	pass


