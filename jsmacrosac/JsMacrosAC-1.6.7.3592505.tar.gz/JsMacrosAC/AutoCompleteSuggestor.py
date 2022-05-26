from typing import overload
from typing import Set


class AutoCompleteSuggestor:

	@overload
	def __init__(self, language: str) -> None:
		pass

	@overload
	def getSuggestions(self, start: str) -> Set[str]:
		pass

	pass


