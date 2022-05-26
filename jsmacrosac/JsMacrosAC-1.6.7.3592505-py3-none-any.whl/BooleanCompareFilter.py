from typing import overload
from .IFilter import IFilter


class BooleanCompareFilter(IFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, compareTo: bool) -> None:
		pass

	@overload
	def apply(self, bool: bool) -> bool:
		pass

	pass


