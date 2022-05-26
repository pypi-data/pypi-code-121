from typing import overload
from typing import List
from typing import TypeVar

ChatHudLine = TypeVar["net.minecraft.client.gui.hud.ChatHudLine_net.minecraft.text.Text_"]
Text = TypeVar["net.minecraft.text.Text"]
Predicate = TypeVar["java.util.function.Predicate_net.minecraft.client.gui.hud.ChatHudLine_net.minecraft.text.Text__"]

class IChatHud:

	@overload
	def jsmacros_addMessageBypass(self, message: Text) -> None:
		pass

	@overload
	def jsmacros_getMessages(self) -> List[ChatHudLine]:
		pass

	@overload
	def jsmacros_removeMessageById(self, messageId: int) -> None:
		pass

	@overload
	def jsmacros_addMessageAtIndexBypass(self, message: Text, index: int, time: int) -> None:
		pass

	@overload
	def jsmacros_removeMessage(self, index: int) -> None:
		pass

	@overload
	def jsmacros_removeMessageByText(self, text: Text) -> None:
		pass

	@overload
	def jsmacros_removeMessagePredicate(self, textfilter: Predicate) -> None:
		pass

	pass


