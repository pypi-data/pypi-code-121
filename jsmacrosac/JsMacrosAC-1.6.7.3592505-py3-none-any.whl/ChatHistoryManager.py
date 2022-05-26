from typing import overload
from typing import List
from typing import TypeVar
from .ChatHudLineHelper import ChatHudLineHelper
from .TextHelper import TextHelper
from .MethodWrapper import MethodWrapper

ChatHud = TypeVar["net.minecraft.client.gui.hud.ChatHud"]

class ChatHistoryManager:
	"""
	Since: 1.6.0 
	"""

	@overload
	def __init__(self, hud: ChatHud) -> None:
		pass

	@overload
	def getRecvLine(self, index: int) -> ChatHudLineHelper:
		"""
		Since: 1.6.0 

		Args:
			index: 
		"""
		pass

	@overload
	def insertRecvText(self, index: int, line: TextHelper) -> None:
		"""
		Since: 1.6.0 

		Args:
			line: 
			index: 
		"""
		pass

	@overload
	def insertRecvText(self, index: int, line: TextHelper, timeTicks: int) -> None:
		"""you should probably run ChatHistoryManager#refreshVisible() after...\n
		Since: 1.6.0 

		Args:
			line: 
			timeTicks: 
			index: 
		"""
		pass

	@overload
	def insertRecvText(self, index: int, line: TextHelper, timeTicks: int, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			line: 
			timeTicks: 
			await: 
			index: 
		"""
		pass

	@overload
	def removeRecvText(self, index: int) -> None:
		"""
		Since: 1.6.0 

		Args:
			index: 
		"""
		pass

	@overload
	def removeRecvText(self, index: int, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			await: 
			index: 
		"""
		pass

	@overload
	def removeRecvTextMatching(self, text: TextHelper) -> None:
		"""
		Since: 1.6.0 

		Args:
			text: 
		"""
		pass

	@overload
	def removeRecvTextMatching(self, text: TextHelper, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			await: 
			text: 
		"""
		pass

	@overload
	def removeRecvTextMatchingFilter(self, filter: MethodWrapper) -> None:
		"""
		Since: 1.6.0 

		Args:
			filter: 
		"""
		pass

	@overload
	def removeRecvTextMatchingFilter(self, filter: MethodWrapper, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			filter: 
			await: 
		"""
		pass

	@overload
	def refreshVisible(self) -> None:
		"""this will reset the view of visible messages\n
		Since: 1.6.0 
		"""
		pass

	@overload
	def refreshVisible(self, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			await: 
		"""
		pass

	@overload
	def clearRecv(self) -> None:
		"""
		Since: 1.6.0 
		"""
		pass

	@overload
	def clearRecv(self, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			await: 
		"""
		pass

	@overload
	def getSent(self) -> List[str]:
		"""
		Since: 1.6.0 

		Returns:
			direct reference to sent message history list. modifications will affect the list. 
		"""
		pass

	@overload
	def clearSent(self) -> None:
		"""
		Since: 1.6.0 
		"""
		pass

	@overload
	def clearSent(self, await_: bool) -> None:
		"""
		Since: 1.6.0 

		Args:
			await: 
		"""
		pass

	pass


