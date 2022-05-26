from typing import overload
from typing import List
from typing import TypeVar
from .IScreen import IScreen
from .RenderCommon_Text import RenderCommon_Text
from .RenderCommon_Rect import RenderCommon_Rect
from .RenderCommon_Item import RenderCommon_Item
from .RenderCommon_Image import RenderCommon_Image
from .TextFieldWidgetHelper import TextFieldWidgetHelper
from .ButtonWidgetHelper import ButtonWidgetHelper
from .RenderCommon_RenderElement import RenderCommon_RenderElement
from .TextHelper import TextHelper
from .ItemStackHelper import ItemStackHelper
from .MethodWrapper import MethodWrapper

AbstractParentElement = TypeVar["net.minecraft.client.gui.AbstractParentElement"]
CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]
CallbackInfoReturnable = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable_java.lang.Boolean_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Style = TypeVar["net.minecraft.text.Style"]

class MixinScreen(IScreen, AbstractParentElement):
	width: int
	height: int

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def onClose(self) -> None:
		pass

	@overload
	def tick(self) -> None:
		pass

	@overload
	def shouldCloseOnEsc(self) -> bool:
		pass

	@overload
	def getWidth(self) -> int:
		pass

	@overload
	def getHeight(self) -> int:
		pass

	@overload
	def getTexts(self) -> List[RenderCommon_Text]:
		pass

	@overload
	def getRects(self) -> List[RenderCommon_Rect]:
		pass

	@overload
	def getItems(self) -> List[RenderCommon_Item]:
		pass

	@overload
	def getImages(self) -> List[RenderCommon_Image]:
		pass

	@overload
	def getTextFields(self) -> List[TextFieldWidgetHelper]:
		pass

	@overload
	def getButtonWidgets(self) -> List[ButtonWidgetHelper]:
		pass

	@overload
	def getElements(self) -> List[RenderCommon_RenderElement]:
		pass

	@overload
	def removeElement(self, e: RenderCommon_RenderElement) -> IScreen:
		pass

	@overload
	def reAddElement(self, e: RenderCommon_RenderElement) -> RenderCommon_RenderElement:
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, shadow: bool) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, zIndex: int, shadow: bool) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, zIndex: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, shadow: bool) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, zIndex: int, shadow: bool) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, zIndex: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		pass

	@overload
	def removeText(self, t: RenderCommon_Text) -> IScreen:
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int) -> RenderCommon_Image:
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int) -> RenderCommon_Image:
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.4.0 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, color: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, alpha: int, color: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def removeImage(self, i: RenderCommon_Image) -> IScreen:
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int) -> RenderCommon_Rect:
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int) -> RenderCommon_Rect:
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int, rotation: float) -> RenderCommon_Rect:
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int, rotation: float, zIndex: int) -> RenderCommon_Rect:
		pass

	@overload
	def removeRect(self, r: RenderCommon_Rect) -> IScreen:
		pass

	@overload
	def addItem(self, x: int, y: int, id: str) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, id: str) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, id: str, overlay: bool) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, id: str, overlay: bool) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, id: str, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, id: str, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, item: ItemStackHelper) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper, overlay: bool) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, item: ItemStackHelper, overlay: bool) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, item: ItemStackHelper, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		pass

	@overload
	def removeItem(self, i: RenderCommon_Item) -> IScreen:
		pass

	@overload
	def getScreenClassName(self) -> str:
		pass

	@overload
	def getTitleText(self) -> str:
		pass

	@overload
	def addButton(self, x: int, y: int, width: int, height: int, text: str, callback: MethodWrapper) -> ButtonWidgetHelper:
		pass

	@overload
	def addButton(self, x: int, y: int, width: int, height: int, zIndex: int, text: str, callback: MethodWrapper) -> ButtonWidgetHelper:
		pass

	@overload
	def removeButton(self, btn: ButtonWidgetHelper) -> IScreen:
		pass

	@overload
	def addTextInput(self, x: int, y: int, width: int, height: int, message: str, onChange: MethodWrapper) -> TextFieldWidgetHelper:
		pass

	@overload
	def addTextInput(self, x: int, y: int, width: int, height: int, zIndex: int, message: str, onChange: MethodWrapper) -> TextFieldWidgetHelper:
		pass

	@overload
	def removeTextInput(self, inp: TextFieldWidgetHelper) -> IScreen:
		pass

	@overload
	def soft$close(self) -> None:
		pass

	@overload
	def setOnMouseDown(self, onMouseDown: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnMouseDrag(self, onMouseDrag: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnMouseUp(self, onMouseUp: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnScroll(self, onScroll: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnKeyPressed(self, onKeyPressed: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnInit(self, onInit: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnFailInit(self, catchInit: MethodWrapper) -> IScreen:
		pass

	@overload
	def setOnClose(self, onClose: MethodWrapper) -> IScreen:
		pass

	@overload
	def reloadScreen(self) -> IScreen:
		pass

	@overload
	def onRenderInternal(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float, info: CallbackInfo) -> None:
		pass

	@overload
	def mouseClicked(self, mouseX: float, mouseY: float, button: int) -> bool:
		pass

	@overload
	def mouseDragged(self, mouseX: float, mouseY: float, button: int, deltaX: float, deltaY: float) -> bool:
		pass

	@overload
	def mouseReleased(self, mouseX: float, mouseY: float, button: int) -> bool:
		pass

	@overload
	def keyPressed(self, keyCode: int, scanCode: int, modifiers: int, info: CallbackInfoReturnable) -> None:
		pass

	@overload
	def mouseScrolled(self, mouseX: float, mouseY: float, amount: float) -> bool:
		pass

	@overload
	def handleCustomClickEvent(self, style: Style, cir: CallbackInfoReturnable) -> None:
		pass

	@overload
	def getOnClose(self) -> MethodWrapper:
		pass

	pass


