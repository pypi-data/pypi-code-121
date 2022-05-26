from typing import overload
from typing import TypeVar

Text = TypeVar["net.minecraft.text.Text"]

class AutoCompleteSuggestion:
	startIndex: int
	suggestion: str
	displayText: Text

	@overload
	def __init__(self, startIndex: int, suggestion: str) -> None:
		pass

	@overload
	def __init__(self, startIndex: int, suggestion: str, displayText: Text) -> None:
		pass

	pass


