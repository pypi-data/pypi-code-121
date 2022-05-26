from typing import overload
from typing import TypeVar
from .ButtonWidgetHelper import ButtonWidgetHelper

TextFieldWidget = TypeVar["net.minecraft.client.gui.widget.TextFieldWidget"]

class TextFieldWidgetHelper(ButtonWidgetHelper):
	"""F\n
	Since: 1.0.5 
	"""

	@overload
	def __init__(self, t: TextFieldWidget) -> None:
		pass

	@overload
	def __init__(self, t: TextFieldWidget, zIndex: int) -> None:
		pass

	@overload
	def getText(self) -> str:
		"""
		Since: 1.0.5 

		Returns:
			the currently entered String . 
		"""
		pass

	@overload
	def setText(self, text: str) -> "TextFieldWidgetHelper":
		"""
		Since: 1.0.5 

		Args:
			text: 
		"""
		pass

	@overload
	def setText(self, text: str, await_: bool) -> "TextFieldWidgetHelper":
		"""set the currently entered String .\n
		Since: 1.3.1 

		Args:
			await: 
			text: 
		"""
		pass

	@overload
	def setEditableColor(self, color: int) -> "TextFieldWidgetHelper":
		"""
		Since: 1.0.5 

		Args:
			color: 
		"""
		pass

	@overload
	def setEditable(self, edit: bool) -> "TextFieldWidgetHelper":
		"""
		Since: 1.0.5 

		Args:
			edit: 
		"""
		pass

	@overload
	def setUneditableColor(self, color: int) -> "TextFieldWidgetHelper":
		"""
		Since: 1.0.5 

		Args:
			color: 
		"""
		pass

	pass


