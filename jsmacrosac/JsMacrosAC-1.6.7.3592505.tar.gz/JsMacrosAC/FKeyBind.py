from typing import overload
from typing import TypeVar
from typing import Mapping
from typing import Set
from .BaseLibrary import BaseLibrary

InputUtil_Key = TypeVar["net.minecraft.client.util.InputUtil.Key"]

class FKeyBind(BaseLibrary):
	"""Functions for getting and modifying key pressed states.

An instance of this class is passed to scripts as the 'KeyBind' variable.
	"""
	pressedKeys: Set[str]

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getKeyCode(self, keyName: str) -> InputUtil_Key:
		"""Dont use this one... get the raw minecraft keycode class.

		Args:
			keyName: 

		Returns:
			the raw minecraft keycode class 
		"""
		pass

	@overload
	def getKeyBindings(self) -> Mapping[str, str]:
		"""
		Since: 1.2.2 

		Returns:
			A Map of all the minecraft keybinds. 
		"""
		pass

	@overload
	def setKeyBind(self, bind: str, key: str) -> None:
		"""Sets a minecraft keybind to the specified key.\n
		Since: 1.2.2 

		Args:
			bind: 
			key: 
		"""
		pass

	@overload
	def key(self, keyName: str, keyState: bool) -> None:
		"""Set a key-state for a key.

		Args:
			keyState: 
			keyName: 
		"""
		pass

	@overload
	def keyBind(self, keyBind: str, keyState: bool) -> None:
		"""Set a key-state using the name of the keybind rather than the name of the key.

This is probably the one you should use.\n
		Since: 1.2.2 

		Args:
			keyBind: 
			keyState: 
		"""
		pass

	@overload
	def getPressedKeys(self) -> Set[str]:
		"""
		Since: 1.2.6 (turned into set instead of list in 1.6.5) 

		Returns:
			a set of currently pressed keys. 
		"""
		pass

	pass


