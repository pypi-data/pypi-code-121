from typing import overload
from typing import Mapping
from .BaseEvent import BaseEvent
from .MethodWrapper import MethodWrapper


class EventCustom(BaseEvent):
	"""Custom Events\n
	Since: 1.2.8 
	"""
	eventName: str

	@overload
	def __init__(self, eventName: str) -> None:
		"""

		Args:
			eventName: name of the event. please don't use an existing one... your scripts might not like that. 
		"""
		pass

	@overload
	def trigger(self) -> None:
		"""Triggers the event.
Try not to cause infinite looping by triggering the same EventCustom from its own listeners.\n
		Since: 1.2.8 
		"""
		pass

	@overload
	def trigger(self, callback: MethodWrapper) -> None:
		"""trigger the event listeners, then run 'callback' when they finish.\n
		Since: 1.3.1 

		Args:
			callback: used as a Runnable , so no args, no return value. 
		"""
		pass

	@overload
	def triggerJoin(self) -> None:
		"""Triggers the event and waits for it to complete.
In languages with threading issues (js/jep) this may cause circular waiting when triggered from the same thread as
the 'jsmacros.on' registration for the event\n
		Since: 1.2.8 
		"""
		pass

	@overload
	def putInt(self, name: str, i: int) -> int:
		"""Put an Integer into the event.\n
		Since: 1.2.8 

		Args:
			name: 
			i: 
		"""
		pass

	@overload
	def putString(self, name: str, str: str) -> str:
		"""put a String into the event.\n
		Since: 1.2.8 

		Args:
			str: 
			name: 
		"""
		pass

	@overload
	def putDouble(self, name: str, d: float) -> float:
		"""put a Double into the event.\n
		Since: 1.2.8 

		Args:
			d: 
			name: 
		"""
		pass

	@overload
	def putBoolean(self, name: str, b: bool) -> bool:
		"""put a Boolean into the event.\n
		Since: 1.2.8 

		Args:
			b: 
			name: 
		"""
		pass

	@overload
	def putObject(self, name: str, o: object) -> object:
		"""put anything else into the event.\n
		Since: 1.2.8 

		Args:
			name: 
			o: 
		"""
		pass

	@overload
	def getType(self, name: str) -> str:
		"""Returns the type of the defined item in the event as a string.\n
		Since: 1.2.8 

		Args:
			name: 
		"""
		pass

	@overload
	def getInt(self, name: str) -> int:
		"""Gets an Integer from the event.\n
		Since: 1.2.8 

		Args:
			name: 
		"""
		pass

	@overload
	def getString(self, name: str) -> str:
		"""Gets a String from the event\n
		Since: 1.2.8 

		Args:
			name: 
		"""
		pass

	@overload
	def getDouble(self, name: str) -> float:
		"""Gets a Double from the event.\n
		Since: 1.2.8 

		Args:
			name: 
		"""
		pass

	@overload
	def getBoolean(self, name: str) -> bool:
		"""Gets a Boolean from the event.\n
		Since: 1.2.8 

		Args:
			name: 
		"""
		pass

	@overload
	def getObject(self, name: str) -> object:
		"""Gets an Object from the event.\n
		Since: 1.2.8 

		Args:
			name: 
		"""
		pass

	@overload
	def getUnderlyingMap(self) -> Mapping[str, object]:
		"""
		Since: 1.6.4 

		Returns:
			map backing the event 
		"""
		pass

	@overload
	def registerEvent(self) -> None:
		"""registers event so you can see it in the gui\n
		Since: 1.3.0 
		"""
		pass

	pass


