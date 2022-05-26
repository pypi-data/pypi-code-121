from typing import overload
from .IFilter import IFilter


class CharCompareFilter(IFilter):

	@overload
	def __init__(self, compareTo: str) -> None:
		pass

	@overload
	def apply(self, character: Character) -> bool:
		pass

	pass


