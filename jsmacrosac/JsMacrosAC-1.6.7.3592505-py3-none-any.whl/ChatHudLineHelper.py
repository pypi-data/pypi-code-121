from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

ChatHudLine = TypeVar["net.minecraft.client.gui.hud.ChatHudLine_net.minecraft.text.Text_"]
ChatHud = TypeVar["net.minecraft.client.gui.hud.ChatHud"]

class ChatHudLineHelper(BaseHelper):

	@overload
	def __init__(self, base: ChatHudLine, hud: ChatHud) -> None:
		pass

	@overload
	def getText(self) -> TextHelper:
		pass

	@overload
	def getId(self) -> int:
		pass

	@overload
	def getCreationTick(self) -> int:
		pass

	@overload
	def deleteById(self) -> None:
		pass

	pass


