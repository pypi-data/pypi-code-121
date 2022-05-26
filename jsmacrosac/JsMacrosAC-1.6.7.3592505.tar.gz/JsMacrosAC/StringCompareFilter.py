from typing import overload
from .IFilter import IFilter


class StringCompareFilter(IFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, operation: str, compareTo: str) -> None:
		pass

	@overload
	def apply(self, val: str) -> bool:
		pass

	pass


