from typing import overload
from .BaseLibrary import BaseLibrary


class FTime(BaseLibrary):
	"""Functions for getting and using raw java classes, methods and functions.

An instance of this class is passed to scripts as the 'Time' variable.
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def time(self) -> float:
		"""

		Returns:
			current time in MS. 
		"""
		pass

	@overload
	def sleep(self, millis: float) -> None:
		"""Sleeps the current thread for the specified time in MS.

		Args:
			millis: 
		"""
		pass

	pass


