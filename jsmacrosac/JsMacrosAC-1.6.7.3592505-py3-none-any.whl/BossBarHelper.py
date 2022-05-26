from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

BossBar = TypeVar["net.minecraft.entity.boss.BossBar"]

class BossBarHelper(BaseHelper):
	"""
	Since: 1.2.1 
	"""

	@overload
	def __init__(self, b: BossBar) -> None:
		pass

	@overload
	def getUUID(self) -> str:
		"""
		Since: 1.2.1 

		Returns:
			boss bar uuid. 
		"""
		pass

	@overload
	def getPercent(self) -> float:
		"""
		Since: 1.2.1 

		Returns:
			percent of boss bar remaining. 
		"""
		pass

	@overload
	def getColor(self) -> str:
		"""
		Since: 1.2.1 

		Returns:
			boss bar color. 
		"""
		pass

	@overload
	def getStyle(self) -> str:
		"""
		Since: 1.2.1 

		Returns:
			boss bar notch style. 
		"""
		pass

	@overload
	def getName(self) -> TextHelper:
		"""
		Since: 1.2.1 

		Returns:
			name of boss bar 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


