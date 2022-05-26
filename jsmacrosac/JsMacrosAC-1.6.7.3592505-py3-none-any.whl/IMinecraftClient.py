from typing import overload
from typing import TypeVar

FontManager = TypeVar["net.minecraft.client.font.FontManager"]

class IMinecraftClient:

	@overload
	def jsmacros_getFontManager(self) -> FontManager:
		pass

	@overload
	def jsmacros_doItemUse(self) -> None:
		pass

	@overload
	def jsmacros_doAttack(self) -> None:
		pass

	pass


