from typing import overload
from typing import List
from typing import TypeVar
from .IDraw2D import IDraw2D
from .ButtonWidgetHelper import ButtonWidgetHelper
from .TextFieldWidgetHelper import TextFieldWidgetHelper
from .MethodWrapper import MethodWrapper
from .RenderCommon_Rect import RenderCommon_Rect
from .RenderCommon_Item import RenderCommon_Item
from .ItemStackHelper import ItemStackHelper

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class IScreen(IDraw2D):
	"""
	Since: 1.2.7 
	"""

	@overload
	def getScreenClassName(self) -> str:
		"""
		Since: 1.2.7 
		"""
		pass

	@overload
	def getTitleText(self) -> str:
		"""
		Since: 1.0.5 
		"""
		pass

	@overload
	def getButtonWidgets(self) -> List[ButtonWidgetHelper]:
		"""in '1.3.1' updated to work with all button widgets not just ones added by scripts.\n
		Since: 1.0.5 
		"""
		pass

	@overload
	def getTextFields(self) -> List[TextFieldWidgetHelper]:
		"""in '1.3.1' updated to work with all text fields not just ones added by scripts.\n
		Since: 1.0.5 
		"""
		pass

	@overload
	def addButton(self, x: int, y: int, width: int, height: int, text: str, callback: MethodWrapper) -> ButtonWidgetHelper:
		"""
		Since: 1.0.5 

		Args:
			x: 
			width: 
			y: 
			callback: calls your method as a Consumer ButtonWidgetHelper 
			text: 
			height: 
		"""
		pass

	@overload
	def addButton(self, x: int, y: int, width: int, height: int, zIndex: int, text: str, callback: MethodWrapper) -> ButtonWidgetHelper:
		"""
		Since: 1.4.0 

		Args:
			x: 
			width: 
			y: 
			callback: calls your method as a Consumer ButtonWidgetHelper 
			text: 
			height: 
			zIndex: 
		"""
		pass

	@overload
	def removeButton(self, btn: ButtonWidgetHelper) -> "IScreen":
		"""
		Since: 1.0.5 

		Args:
			btn: 
		"""
		pass

	@overload
	def addTextInput(self, x: int, y: int, width: int, height: int, message: str, onChange: MethodWrapper) -> TextFieldWidgetHelper:
		"""
		Since: 1.0.5 

		Args:
			onChange: calls your method as a Consumer String 
			x: 
			width: 
			y: 
			message: 
			height: 
		"""
		pass

	@overload
	def addTextInput(self, x: int, y: int, width: int, height: int, zIndex: int, message: str, onChange: MethodWrapper) -> TextFieldWidgetHelper:
		"""
		Since: 1.0.5 

		Args:
			onChange: calls your method as a Consumer String 
			x: 
			width: 
			y: 
			message: 
			height: 
			zIndex: 
		"""
		pass

	@overload
	def removeTextInput(self, inp: TextFieldWidgetHelper) -> "IScreen":
		"""
		Since: 1.0.5 

		Args:
			inp: 
		"""
		pass

	@overload
	def setOnMouseDown(self, onMouseDown: MethodWrapper) -> "IScreen":
		"""
		Since: 1.2.7 

		Args:
			onMouseDown: calls your method as a BiConsumer PositionCommon_Pos2D , Integer 
		"""
		pass

	@overload
	def setOnMouseDrag(self, onMouseDrag: MethodWrapper) -> "IScreen":
		"""
		Since: 1.2.7 

		Args:
			onMouseDrag: calls your method as a BiConsumer PositionCommon_Vec2D , Integer 
		"""
		pass

	@overload
	def setOnMouseUp(self, onMouseUp: MethodWrapper) -> "IScreen":
		"""
		Since: 1.2.7 

		Args:
			onMouseUp: calls your method as a BiConsumer PositionCommon_Pos2D , Integer 
		"""
		pass

	@overload
	def setOnScroll(self, onScroll: MethodWrapper) -> "IScreen":
		"""
		Since: 1.2.7 

		Args:
			onScroll: calls your method as a BiConsumer PositionCommon_Pos2D , Double 
		"""
		pass

	@overload
	def setOnKeyPressed(self, onKeyPressed: MethodWrapper) -> "IScreen":
		"""
		Since: 1.2.7 

		Args:
			onKeyPressed: calls your method as a BiConsumer Integer , Integer 
		"""
		pass

	@overload
	def setOnClose(self, onClose: MethodWrapper) -> "IScreen":
		"""
		Since: 1.2.7 

		Args:
			onClose: calls your method as a Consumer IScreen 
		"""
		pass

	@overload
	def close(self) -> None:
		"""
		Since: 1.1.9 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int) -> RenderCommon_Rect:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int) -> RenderCommon_Rect:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int, rotation: float) -> RenderCommon_Rect:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def removeRect(self, r: RenderCommon_Rect) -> "IScreen":
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, id: str) -> RenderCommon_Item:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, id: str, overlay: bool) -> RenderCommon_Item:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, id: str, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper) -> RenderCommon_Item:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper, overlay: bool) -> RenderCommon_Item:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def removeItem(self, i: RenderCommon_Item) -> "IScreen":
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def reloadScreen(self) -> "IScreen":
		"""calls the screen's init function re-loading it.\n
		Since: 1.2.7 
		"""
		pass

	@overload
	def onRenderInternal(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		"""DON'T TOUCH\n
		Since: 1.4.1 
		"""
		pass

	@overload
	def getOnClose(self) -> MethodWrapper:
		pass

	pass


