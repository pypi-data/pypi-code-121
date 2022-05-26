from typing import overload
from typing import List
from .PerExecLibrary import PerExecLibrary
from .BaseScriptContext import BaseScriptContext
from .FileHandler import FileHandler


class FFS(PerExecLibrary):
	"""Better File-System functions.

An instance of this class is passed to scripts as the 'FS' variable.\n
	Since: 1.1.8 
	"""

	@overload
	def __init__(self, context: BaseScriptContext) -> None:
		pass

	@overload
	def list(self, path: str) -> List[str]:
		"""List files in path.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 

		Returns:
			An array of file names as String . 
		"""
		pass

	@overload
	def exists(self, path: str) -> bool:
		"""Check if a file exists.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 
		"""
		pass

	@overload
	def isDir(self, path: str) -> bool:
		"""Check if a file is a directory.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 
		"""
		pass

	@overload
	def getName(self, path: str) -> str:
		"""Get the last part (name) of a file.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 

		Returns:
			a String of the file name. 
		"""
		pass

	@overload
	def makeDir(self, path: str) -> bool:
		"""Make a directory.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 

		Returns:
			a Boolean for success. 
		"""
		pass

	@overload
	def move(self, from_: str, to: str) -> None:
		"""Move a file.\n
		Since: 1.1.8 

		Args:
			from: relative to the script's folder. 
			to: relative to the script's folder. 
		"""
		pass

	@overload
	def copy(self, from_: str, to: str) -> None:
		"""Copy a file.\n
		Since: 1.1.8 

		Args:
			from: relative to the script's folder. 
			to: relative to the script's folder. 
		"""
		pass

	@overload
	def unlink(self, path: str) -> bool:
		"""Delete a file.\n
		Since: 1.2.9 

		Args:
			path: relative to the script's folder. 

		Returns:
			a Boolean for success. 
		"""
		pass

	@overload
	def combine(self, patha: str, pathb: str) -> str:
		"""Combine 2 paths.\n
		Since: 1.1.8 

		Args:
			patha: path is relative to the script's folder. 
			pathb: 

		Returns:
			a String of the combined path. 
		"""
		pass

	@overload
	def getDir(self, path: str) -> str:
		"""Gets the directory part of a file path, or the parent directory of a folder.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 

		Returns:
			a String of the combined path. 
		"""
		pass

	@overload
	def open(self, path: str) -> FileHandler:
		"""Open a FileHandler for the file at the specified path.\n
		Since: 1.1.8 

		Args:
			path: relative to the script's folder. 

		Returns:
			a FileHandler for the file path. 
		"""
		pass

	pass


