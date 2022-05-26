from typing import overload
from typing import TypeVar
from .BaseLibrary import BaseLibrary
from .TickSync import TickSync
from .MethodWrapper import MethodWrapper
from .OptionsHelper import OptionsHelper
from .ServerInfoHelper import ServerInfoHelper

MinecraftClient = TypeVar["net.minecraft.client.MinecraftClient"]

class FClient(BaseLibrary):
	"""Functions that interact with minecraft that don't fit into their own module.

An instance of this class is passed to scripts as the 'Client' variable.\n
	Since: 1.2.9 
	"""
	tickSynchronizer: TickSync

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getMinecraft(self) -> MinecraftClient:
		"""
		Since: 1.0.0 (was in the 'jsmacros' library until 1.2.9) 

		Returns:
			the raw minecraft client class, it may be useful to use Minecraft Mappings Viewer for this. 
		"""
		pass

	@overload
	def runOnMainThread(self, runnable: MethodWrapper) -> None:
		"""Run your task on the main minecraft thread\n
		Since: 1.4.0 

		Args:
			runnable: task to run 
		"""
		pass

	@overload
	def runOnMainThread(self, runnable: MethodWrapper, watchdogMaxTime: float) -> None:
		"""
		Since: 1.6.5 

		Args:
			runnable: 
			watchdogMaxTime: max time for the watchdog to wait before killing the script 
		"""
		pass

	@overload
	def getGameOptions(self) -> OptionsHelper:
		"""
		Since: 1.1.7 (was in the 'jsmacros' library until 1.2.9) 

		Returns:
			an OptionsHelper for the game options. 
		"""
		pass

	@overload
	def mcVersion(self) -> str:
		"""
		Since: 1.1.2 (was in the 'jsmacros' library until 1.2.9) 

		Returns:
			the current minecraft version as a String . 
		"""
		pass

	@overload
	def getFPS(self) -> str:
		"""
		Since: 1.2.0 (was in the 'jsmacros' library until 1.2.9) 

		Returns:
			the fps debug string from minecraft. 
		"""
		pass

	@overload
	def loadWorld(self, folderName: str) -> None:
		"""Join singleplayer world\n
		Since: 1.6.6 

		Args:
			folderName: 
		"""
		pass

	@overload
	def connect(self, ip: str) -> None:
		"""
		Since: 1.2.3 (was in the 'jsmacros' library until 1.2.9) 

		Args:
			ip: 
		"""
		pass

	@overload
	def connect(self, ip: str, port: int) -> None:
		"""Connect to a server\n
		Since: 1.2.3 (was in the 'jsmacros' library until 1.2.9) 

		Args:
			port: 
			ip: 
		"""
		pass

	@overload
	def disconnect(self) -> None:
		"""
		Since: 1.2.3 (was in the 'jsmacros' library until 1.2.9) 
		"""
		pass

	@overload
	def disconnect(self, callback: MethodWrapper) -> None:
		"""Disconnect from a server with callback.\n
		Since: 1.2.3 (was in the 'jsmacros' library until 1.2.9) 'callback' defaults to 'null' 

		Args:
			callback: calls your method as a Consumer Boolean 
		"""
		pass

	@overload
	def shutdown(self) -> None:
		"""Closes the client (stops the game).
Waits until the game has stopped, meaning no further code is executed (for obvious reasons).
Warning: this does not wait on joined threads, so your script may stop at an undefined point.\n
		Since: 1.6.0 
		"""
		pass

	@overload
	def waitTick(self) -> None:
		"""
		Since: 1.2.4 
		"""
		pass

	@overload
	def waitTick(self, i: int) -> None:
		"""waits the specified number of client ticks.
don't use this on an event that the main thread waits on (joins)... that'll cause circular waiting.\n
		Since: 1.2.6 

		Args:
			i: 
		"""
		pass

	@overload
	def ping(self, ip: str) -> ServerInfoHelper:
		"""
		Since: 1.6.5 

		Args:
			ip: 
		"""
		pass

	@overload
	def pingAsync(self, ip: str, callback: MethodWrapper) -> None:
		"""
		Since: 1.6.5 

		Args:
			ip: 
			callback: 
		"""
		pass

	@overload
	def cancelAllPings(self) -> None:
		"""
		Since: 1.6.5 
		"""
		pass

	pass


