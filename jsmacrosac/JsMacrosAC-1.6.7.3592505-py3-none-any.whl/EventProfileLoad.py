from typing import overload
from .BaseEvent import BaseEvent
from .BaseProfile import BaseProfile


class EventProfileLoad(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	profileName: str

	@overload
	def __init__(self, profile: BaseProfile, profileName: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


