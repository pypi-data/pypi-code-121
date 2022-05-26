from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from .AbstractRenderCodeCompiler import AbstractRenderCodeCompiler
from .EditorScreen import EditorScreen
from .AutoCompleteSuggestion import AutoCompleteSuggestion

Runnable = TypeVar["java.lang.Runnable"]

class DefaultCodeCompiler(AbstractRenderCodeCompiler):

	@overload
	def __init__(self, language: str, screen: EditorScreen) -> None:
		pass

	@overload
	def recompileRenderedText(self, text: str) -> None:
		pass

	@overload
	def getRightClickOptions(self, index: int) -> Mapping[str, Runnable]:
		pass

	@overload
	def getRenderedText(self) -> List[Text]:
		pass

	@overload
	def getSuggestions(self) -> List[AutoCompleteSuggestion]:
		pass

	pass


