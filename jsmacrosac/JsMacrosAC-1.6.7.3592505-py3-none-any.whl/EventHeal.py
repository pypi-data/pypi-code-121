from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent

DamageSource = TypeVar["net.minecraft.entity.damage.DamageSource"]

class EventHeal(BaseEvent):
	"""
	Since: 1.6.5 
	"""
	source: str
	health: float
	change: float

	@overload
	def __init__(self, source: DamageSource, health: float, change: float) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


