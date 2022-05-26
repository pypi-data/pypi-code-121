from typing import overload
from .TextHelper import TextHelper
from .ItemStackHelper import ItemStackHelper
from .EntityHelper import EntityHelper
from .MethodWrapper import MethodWrapper


class TextBuilder:
	"""usage: 'builder.append("hello,").withColor(0xc).append(" World!").withColor(0x6)'\n
	Since: 1.3.0 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def append(self, text: object) -> "TextBuilder":
		"""move on to next section and set it's text.\n
		Since: 1.3.0 

		Args:
			text: a String , TextHelper or TextBuilder 
		"""
		pass

	@overload
	def withColor(self, color: int) -> "TextBuilder":
		"""set current section's color by color code as hex, like '0x6' for gold
and '0xc' for red.\n
		Since: 1.3.0 

		Args:
			color: 
		"""
		pass

	@overload
	def withColor(self, r: int, g: int, b: int) -> "TextBuilder":
		"""Add text with custom colors.\n
		Since: 1.3.1 

		Args:
			r: red '0-255' 
			b: blue '0-255' 
			g: green '0-255' 
		"""
		pass

	@overload
	def withFormatting(self, underline: bool, bold: bool, italic: bool, strikethrough: bool, magic: bool) -> "TextBuilder":
		"""set other formatting options for the current section\n
		Since: 1.3.0 

		Args:
			magic: 
			underline: 
			bold: 
			strikethrough: 
			italic: 
		"""
		pass

	@overload
	def withShowTextHover(self, text: TextHelper) -> "TextBuilder":
		"""set current section's hover event to show text\n
		Since: 1.3.0 

		Args:
			text: 
		"""
		pass

	@overload
	def withShowItemHover(self, item: ItemStackHelper) -> "TextBuilder":
		"""set current section's hover event to show an item\n
		Since: 1.3.0 

		Args:
			item: 
		"""
		pass

	@overload
	def withShowEntityHover(self, entity: EntityHelper) -> "TextBuilder":
		"""set current section's hover event to show an entity\n
		Since: 1.3.0 

		Args:
			entity: 
		"""
		pass

	@overload
	def withCustomClickEvent(self, action: MethodWrapper) -> "TextBuilder":
		"""custom click event.\n
		Since: 1.3.0 

		Args:
			action: 
		"""
		pass

	@overload
	def withClickEvent(self, action: str, value: str) -> "TextBuilder":
		"""normal click events like: 'open_url' , 'open_file' , 'run_command' , 'suggest_command' , 'change_page' , and 'copy_to_clipboard'\n
		Since: 1.3.0 

		Args:
			action: 
			value: 
		"""
		pass

	@overload
	def build(self) -> TextHelper:
		"""Build to a TextHelper\n
		Since: 1.3.0 
		"""
		pass

	pass


