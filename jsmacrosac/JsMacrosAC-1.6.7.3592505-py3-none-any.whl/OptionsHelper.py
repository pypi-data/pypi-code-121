from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from .BaseHelper import BaseHelper

GameOptions = TypeVar["net.minecraft.client.option.GameOptions"]

class OptionsHelper(BaseHelper):
	"""
	Since: 1.1.7 
	"""

	@overload
	def __init__(self, options: GameOptions) -> None:
		pass

	@overload
	def getCloudMode(self) -> int:
		"""
		Since: 1.1.7 

		Returns:
			0: off, 2: fancy 
		"""
		pass

	@overload
	def setCloudMode(self, mode: int) -> "OptionsHelper":
		"""
		Since: 1.1.7 

		Args:
			mode: 0: off, 2: fancy 
		"""
		pass

	@overload
	def getGraphicsMode(self) -> int:
		"""
		Since: 1.1.7 
		"""
		pass

	@overload
	def setGraphicsMode(self, mode: int) -> "OptionsHelper":
		"""
		Since: 1.1.7 

		Args:
			mode: 0: fast, 2: fabulous 
		"""
		pass

	@overload
	def getResourcePacks(self) -> List[str]:
		"""
		Since: 1.1.7 

		Returns:
			list of names of resource packs. 
		"""
		pass

	@overload
	def getEnabledResourcePacks(self) -> List[str]:
		"""
		Since: 1.2.0 

		Returns:
			list of names of enabled resource packs. 
		"""
		pass

	@overload
	def setEnabledResourcePacks(self, enabled: List[str]) -> "OptionsHelper":
		"""Set the enabled resource packs to the provided list.\n
		Since: 1.2.0 

		Args:
			enabled: 
		"""
		pass

	@overload
	def isRightHanded(self) -> bool:
		"""
		Since: 1.1.7 
		"""
		pass

	@overload
	def setRightHanded(self, val: bool) -> None:
		"""
		Since: 1.1.7 

		Args:
			val: 
		"""
		pass

	@overload
	def getFov(self) -> float:
		"""
		Since: 1.1.7 
		"""
		pass

	@overload
	def setFov(self, fov: float) -> "OptionsHelper":
		"""
		Since: 1.1.7 

		Args:
			fov: 
		"""
		pass

	@overload
	def getRenderDistance(self) -> int:
		"""
		Since: 1.1.7 
		"""
		pass

	@overload
	def setRenderDistance(self, d: int) -> None:
		"""
		Since: 1.1.7 

		Args:
			d: 
		"""
		pass

	@overload
	def getWidth(self) -> int:
		"""
		Since: 1.2.6 
		"""
		pass

	@overload
	def getHeight(self) -> int:
		"""
		Since: 1.2.6 
		"""
		pass

	@overload
	def setWidth(self, w: int) -> None:
		"""
		Since: 1.2.6 

		Args:
			w: 
		"""
		pass

	@overload
	def setHeight(self, h: int) -> None:
		"""
		Since: 1.2.6 

		Args:
			h: 
		"""
		pass

	@overload
	def setSize(self, w: int, h: int) -> None:
		"""
		Since: 1.2.6 

		Args:
			w: 
			h: 
		"""
		pass

	@overload
	def getGamma(self) -> float:
		"""
		Since: 1.3.0
normal values for gamam are between '0' and '1' 
		"""
		pass

	@overload
	def setGamma(self, gamma: float) -> None:
		"""
		Since: 1.3.0
normal values for gamma are between '0' and '1' 
		"""
		pass

	@overload
	def setVolume(self, vol: float) -> None:
		"""
		Since: 1.3.1 

		Args:
			vol: 
		"""
		pass

	@overload
	def setVolume(self, category: str, volume: float) -> None:
		"""set volume by category.\n
		Since: 1.3.1 

		Args:
			volume: 
			category: 
		"""
		pass

	@overload
	def getVolumes(self) -> Mapping[str, Float]:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def setGuiScale(self, scale: int) -> None:
		"""sets gui scale, '0' for auto.\n
		Since: 1.3.1 

		Args:
			scale: 
		"""
		pass

	@overload
	def getGuiScale(self) -> int:
		"""
		Since: 1.3.1 

		Returns:
			gui scale, '0' for auto. 
		"""
		pass

	@overload
	def getVolume(self, category: str) -> float:
		"""
		Since: 1.3.1 

		Args:
			category: 
		"""
		pass

	@overload
	def getSmoothCamera(self) -> bool:
		"""
		Since: 1.5.0 
		"""
		pass

	@overload
	def setSmoothCamera(self, val: bool) -> None:
		"""
		Since: 1.5.0 

		Args:
			val: 
		"""
		pass

	@overload
	def getCameraMode(self) -> int:
		"""
		Since: 1.5.0 

		Returns:
			0 for 1st person, 2 for in front. 
		"""
		pass

	@overload
	def setCameraMode(self, mode: int) -> None:
		"""
		Since: 1.5.0 

		Args:
			mode: 0: first, 2: front 
		"""
		pass

	pass


