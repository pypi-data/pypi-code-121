from typing import overload
from typing import List
from typing import TypeVar

File = TypeVar["java.io.File"]

class FileHandler:
	"""
	Since: 1.1.8 
	"""

	@overload
	def __init__(self, path: str) -> None:
		pass

	@overload
	def __init__(self, path: File) -> None:
		pass

	@overload
	def write(self, s: str) -> "FileHandler":
		"""writes a string to the file. this is a destructive operation that replaces the file contents.\n
		Since: 1.1.8 

		Args:
			s: 
		"""
		pass

	@overload
	def write(self, b: List[float]) -> "FileHandler":
		"""writes a byte array to the file. this is a destructive operation that replaces the file contents.\n
		Since: 1.1.8 

		Args:
			b: 
		"""
		pass

	@overload
	def read(self) -> str:
		"""
		Since: 1.1.8 
		"""
		pass

	@overload
	def readBytes(self) -> List[float]:
		"""
		Since: 1.2.6 
		"""
		pass

	@overload
	def append(self, s: str) -> "FileHandler":
		"""
		Since: 1.1.8 

		Args:
			s: 
		"""
		pass

	@overload
	def append(self, b: List[float]) -> "FileHandler":
		"""
		Since: 1.2.6 

		Args:
			b: 
		"""
		pass

	@overload
	def getFile(self) -> File:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


