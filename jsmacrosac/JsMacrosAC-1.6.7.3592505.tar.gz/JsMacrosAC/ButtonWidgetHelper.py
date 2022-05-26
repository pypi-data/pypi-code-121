from typing import overload
from typing import TypeVar
from typing import Generic
from .RenderCommon_RenderElement import RenderCommon_RenderElement
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

T = TypeVar("T")
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class ButtonWidgetHelper(RenderCommon_RenderElement, Generic[T], BaseHelper):
	"""
	Since: 1.0.5 
	"""
	zIndex: int

	@overload
	def __init__(self, btn: T) -> None:
		pass

	@overload
	def __init__(self, btn: T, zIndex: int) -> None:
		pass

	@overload
	def getX(self) -> int:
		"""
		Since: 1.0.5 

		Returns:
			the 'x' coordinate of the button. 
		"""
		pass

	@overload
	def getY(self) -> int:
		"""
		Since: 1.0.5 

		Returns:
			the 'y' coordinate of the button. 
		"""
		pass

	@overload
	def setPos(self, x: int, y: int) -> "ButtonWidgetHelper":
		"""Set the button position.\n
		Since: 1.0.5 

		Args:
			x: 
			y: 
		"""
		pass

	@overload
	def getWidth(self) -> int:
		"""
		Since: 1.0.5 
		"""
		pass

	@overload
	def setLabel(self, label: str) -> "ButtonWidgetHelper":
		"""change the text.\n
		Since: 1.0.5, renamed from 'setText' in 1.3.1 

		Args:
			label: 
		"""
		pass

	@overload
	def setLabel(self, helper: TextHelper) -> "ButtonWidgetHelper":
		"""change the text.\n
		Since: 1.3.1 

		Args:
			helper: 
		"""
		pass

	@overload
	def getLabel(self) -> TextHelper:
		"""
		Since: 1.2.3, renamed fro 'getText' in 1.3.1 

		Returns:
			current button text. 
		"""
		pass

	@overload
	def getActive(self) -> bool:
		"""
		Since: 1.0.5 

		Returns:
			button clickable state. 
		"""
		pass

	@overload
	def setActive(self, t: bool) -> "ButtonWidgetHelper":
		"""set the button clickable state.\n
		Since: 1.0.5 

		Args:
			t: 
		"""
		pass

	@overload
	def setWidth(self, width: int) -> "ButtonWidgetHelper":
		"""set the button width.\n
		Since: 1.0.5 

		Args:
			width: 
		"""
		pass

	@overload
	def click(self) -> "ButtonWidgetHelper":
		"""clicks button\n
		Since: 1.3.1 
		"""
		pass

	@overload
	def click(self, await_: bool) -> "ButtonWidgetHelper":
		"""clicks button\n
		Since: 1.3.1 

		Args:
			await: should wait for button to finish clicking. 
		"""
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def getZIndex(self) -> int:
		pass

	pass


