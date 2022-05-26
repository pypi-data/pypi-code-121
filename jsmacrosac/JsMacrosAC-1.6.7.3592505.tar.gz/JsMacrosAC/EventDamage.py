from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .EntityHelper import EntityHelper

DamageSource = TypeVar["net.minecraft.entity.damage.DamageSource"]

class EventDamage(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	attacker: EntityHelper
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


