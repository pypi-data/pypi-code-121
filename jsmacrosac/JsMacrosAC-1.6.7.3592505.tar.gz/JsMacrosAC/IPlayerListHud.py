from typing import overload
from typing import TypeVar

Text = TypeVar["net.minecraft.text.Text"]

class IPlayerListHud:

	@overload
	def jsmacros_getHeader(self) -> Text:
		pass

	@overload
	def jsmacros_getFooter(self) -> Text:
		pass

	pass


