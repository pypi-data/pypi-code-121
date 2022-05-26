from typing import overload
from typing import List
from typing import TypeVar
from typing import Any
from typing import Mapping
from .BaseEvent import BaseEvent
from .SelectCursor import SelectCursor
from .EditorScreen import EditorScreen
from .TextHelper import TextHelper
from .AutoCompleteSuggestion import AutoCompleteSuggestion
from .MethodWrapper import MethodWrapper
from .TextBuilder import TextBuilder
from .StringHashTrie import StringHashTrie

Prism4j_Node = TypeVar["io.noties.prism4j.Prism4j.Node"]

class CodeCompileEvent(BaseEvent):
	""""hidden" event for script based code style compiling / linting tasks.
remember to 'consumer.autoWrap()' everything.\n
	Since: 1.3.1 
	"""
	cursor: SelectCursor
	code: str
	language: str
	screen: EditorScreen
	textLines: List[TextHelper]
	autoCompleteSuggestions: List[AutoCompleteSuggestion]
	rightClickActions: MethodWrapper

	@overload
	def __init__(self, code: str, language: str, screen: EditorScreen) -> None:
		pass

	@overload
	def genPrismNodes(self) -> List[Prism4j_Node]:
		"""

		Returns:
			Prism4j's
    node list you don't have to use it but if you're not compiling your own...
    peek at the code of TextStyleCompiler for the default impl for walking the node tree. 
		"""
		pass

	@overload
	def createMap(self) -> Mapping[Any, Any]:
		"""Easy access to the Map object for use with CodeCompileEvent#rightClickActions

		Returns:
			specifically a LinkedHashMap 
		"""
		pass

	@overload
	def createTextBuilder(self) -> TextBuilder:
		"""more convenient access to TextBuilder

		Returns:
			new instance for use with CodeCompileEvent#textLines 
		"""
		pass

	@overload
	def createSuggestion(self, startIndex: int, suggestion: str) -> AutoCompleteSuggestion:
		pass

	@overload
	def createSuggestion(self, startIndex: int, suggestion: str, displayText: TextHelper) -> AutoCompleteSuggestion:
		"""

		Args:
			displayText: how the text should be displayed in the dropdown, default is suggestion text 
			startIndex: index that is where the suggestion starts from before the already typed part 
			suggestion: complete suggestion including the already typed part 

		Returns:
			a new suggestion object 
		"""
		pass

	@overload
	def createPrefixTree(self) -> StringHashTrie:
		"""prefix tree data structure written for you, it's a bit intensive to add things to, especially how I wrote it, but
lookup times are much better at least on larger data sets,
so create a single copy of this for your static autocompletes and don't be re-creating this every time, store it
in 'globalvars' , probably per language

or just don't use it, I'm not forcing you to.

		Returns:
			a new StringHashTrie 
		"""
		pass

	@overload
	def getThemeData(self) -> Mapping[str, List[float]]:
		"""

		Returns:
			'key -> hex integer' values for theme data points, this can be used with the prism data for
    coloring, just have to use TextBuilder#withColor(int,int,int) on 1.15 and older versions the integer values with be the default color's index so you can directly pass it
    to TextBuilder#withColor(int) 
		"""
		pass

	pass


