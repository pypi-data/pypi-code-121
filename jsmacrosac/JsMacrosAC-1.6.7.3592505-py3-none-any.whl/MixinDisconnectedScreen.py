from typing import overload
from typing import TypeVar

Text = TypeVar["net.minecraft.text.Text"]

class MixinDisconnectedScreen:

	@overload
	def getReason(self) -> Text:
		pass

	pass


