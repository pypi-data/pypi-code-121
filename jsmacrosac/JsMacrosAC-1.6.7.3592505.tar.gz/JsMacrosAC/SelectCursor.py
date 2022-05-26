from typing import overload
from typing import TypeVar

Consumer = TypeVar["java.util.function.Consumer_xyz.wagyourtail.jsmacros.client.gui.editor.SelectCursor_"]
Style = TypeVar["net.minecraft.text.Style"]

class SelectCursor:
	onChange: Consumer
	defaultStyle: Style
	startLine: int
	endLine: int
	startIndex: int
	endIndex: int
	startLineIndex: int
	endLineIndex: int
	dragStartIndex: int
	arrowLineIndex: int
	arrowEnd: bool
	startCol: int
	endCol: int

	@overload
	def __init__(self, defaultStyle: Style) -> None:
		pass

	@overload
	def updateStartIndex(self, startIndex: int, current: str) -> None:
		pass

	@overload
	def updateEndIndex(self, endIndex: int, current: str) -> None:
		pass

	pass


