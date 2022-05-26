from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

SuggestionsBuilder = TypeVar["com.mojang.brigadier.suggestion.SuggestionsBuilder"]

class SuggestionsBuilderHelper(BaseHelper):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, base: SuggestionsBuilder) -> None:
		pass

	@overload
	def getInput(self) -> str:
		pass

	@overload
	def getStart(self) -> int:
		pass

	@overload
	def getRemaining(self) -> str:
		pass

	@overload
	def getRemainingLowerCase(self) -> str:
		pass

	@overload
	def suggest(self, suggestion: str) -> "SuggestionsBuilderHelper":
		pass

	@overload
	def suggest(self, value: int) -> "SuggestionsBuilderHelper":
		pass

	@overload
	def suggestWithTooltip(self, suggestion: str, tooltip: TextHelper) -> "SuggestionsBuilderHelper":
		pass

	@overload
	def suggestWithTooltip(self, value: int, tooltip: TextHelper) -> "SuggestionsBuilderHelper":
		pass

	pass


