from typing import overload
from typing import TypeVar
from .IPlayerListHud import IPlayerListHud

Text = TypeVar["net.minecraft.text.Text"]

class MixinPlayerListHud(IPlayerListHud):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getHeader(self) -> Text:
		pass

	@overload
	def jsmacros_getFooter(self) -> Text:
		pass

	pass


