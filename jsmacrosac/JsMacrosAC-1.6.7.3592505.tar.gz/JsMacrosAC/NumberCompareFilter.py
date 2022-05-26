from typing import overload
from .IFilter import IFilter


class NumberCompareFilter(IFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, operation: str, compareTo: object) -> None:
		pass

	@overload
	def apply(self, t: Number) -> bool:
		pass

	pass


