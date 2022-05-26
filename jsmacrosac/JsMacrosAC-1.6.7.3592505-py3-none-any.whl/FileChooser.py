from typing import overload
from typing import TypeVar
from .OverlayContainer import OverlayContainer
from .IOverlayParent import IOverlayParent
from .FileChooser_fileObj import FileChooser_fileObj

Consumer = TypeVar["java.util.function.Consumer_java.io.File_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
File = TypeVar["java.io.File"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class FileChooser(OverlayContainer):
	root: File

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, directory: File, selected: File, parent: IOverlayParent, setFile: Consumer, editFile: Consumer) -> None:
		pass

	@overload
	def setDir(self, dir: File) -> None:
		pass

	@overload
	def selectFile(self, f: File) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def addFile(self, f: File) -> None:
		pass

	@overload
	def addFile(self, f: File, btnText: str) -> None:
		pass

	@overload
	def updateFilePos(self) -> None:
		pass

	@overload
	def confirmDelete(self, f: FileChooser_fileObj) -> None:
		pass

	@overload
	def delete(self, f: FileChooser_fileObj) -> None:
		pass

	@overload
	def onScrollbar(self, page: float) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


