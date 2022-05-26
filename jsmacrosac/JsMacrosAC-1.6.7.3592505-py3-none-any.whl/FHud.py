from typing import overload
from typing import List
from typing import Set
from .BaseLibrary import BaseLibrary
from .IDraw2D import IDraw2D
from .Draw3D import Draw3D
from .ScriptScreen import ScriptScreen
from .IScreen import IScreen
from .Draw2D import Draw2D


class FHud(BaseLibrary):
	"""Functions for displaying stuff in 2 to 3 dimensions

An instance of this class is passed to scripts as the 'Hud' variable.\n
	Since: 1.0.5 
	"""
	overlays: Set[IDraw2D]
	renders: Set[Draw3D]

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def createScreen(self, title: str, dirtBG: bool) -> ScriptScreen:
		"""
		Since: 1.0.5 

		Args:
			title: 
			dirtBG: boolean of whether to use a dirt background or not. 

		Returns:
			a new IScreen Object. 
		"""
		pass

	@overload
	def openScreen(self, s: IScreen) -> None:
		"""Opens a IScreen Object.\n
		Since: 1.0.5 

		Args:
			s: 
		"""
		pass

	@overload
	def getOpenScreen(self) -> IScreen:
		"""
		Since: 1.2.7 

		Returns:
			the currently open Screen as an IScreen 
		"""
		pass

	@overload
	def getOpenScreenName(self) -> str:
		"""
		Since: 1.0.5, renamed from 'getOpenScreen' in 1.2.7 

		Returns:
			The name of the currently open screen. 
		"""
		pass

	@overload
	def isContainer(self) -> bool:
		"""
		Since: 1.1.2 

		Returns:
			a Boolean denoting if the currently open screen is a container. 
		"""
		pass

	@overload
	def createDraw2D(self) -> Draw2D:
		"""
		Since: 1.0.5 
		"""
		pass

	@overload
	def registerDraw2D(self, overlay: IDraw2D) -> None:
		"""
		Since: 1.0.5

Registers an IDraw2D to be rendered. 

		Args:
			overlay: 
		"""
		pass

	@overload
	def unregisterDraw2D(self, overlay: IDraw2D) -> None:
		"""
		Since: 1.0.5

Unregisters an IDraw2D to stop it being rendered. 

		Args:
			overlay: 
		"""
		pass

	@overload
	def listDraw2Ds(self) -> List[IDraw2D]:
		"""
		Since: 1.0.5 

		Returns:
			A list of current IDraw2D . 
		"""
		pass

	@overload
	def clearDraw2Ds(self) -> None:
		"""
		Since: 1.0.5

clears the Draw2D render list. 
		"""
		pass

	@overload
	def createDraw3D(self) -> Draw3D:
		"""
		Since: 1.0.6 

		Returns:
			a new Draw3D . 
		"""
		pass

	@overload
	def registerDraw3D(self, draw: Draw3D) -> None:
		"""
		Since: 1.0.6

Registers an Draw3D to be rendered. 

		Args:
			draw: 
		"""
		pass

	@overload
	def unregisterDraw3D(self, draw: Draw3D) -> None:
		"""
		Since: 1.0.6

Unregisters an Draw3D to stop it being rendered. 

		Args:
			draw: 
		"""
		pass

	@overload
	def listDraw3Ds(self) -> List[Draw3D]:
		"""
		Since: 1.0.6 

		Returns:
			A list of current Draw3D . 
		"""
		pass

	@overload
	def clearDraw3Ds(self) -> None:
		"""
		Since: 1.0.6

clears the Draw2D render list. 
		"""
		pass

	@overload
	def getMouseX(self) -> float:
		"""
		Since: 1.1.3 

		Returns:
			the current X coordinate of the mouse 
		"""
		pass

	@overload
	def getMouseY(self) -> float:
		"""
		Since: 1.1.3 

		Returns:
			the current Y coordinate of the mouse 
		"""
		pass

	pass


