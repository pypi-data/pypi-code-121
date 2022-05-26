from typing import overload
from typing import List
from typing import TypeVar

Input = TypeVar["net.minecraft.client.input.Input"]

class PlayerInput:
	"""An object, that combines all possible player inputs\n
	Since: 1.4.0 
	"""
	movementForward: float
	movementSideways: float
	yaw: float
	pitch: float
	jumping: bool
	sneaking: bool
	sprinting: bool

	@overload
	def __init__(self) -> None:
		"""Creates a new 'PlayerInput' Object with all values set either to 0 or false\n
		Since: 1.4.0 
		"""
		pass

	@overload
	def __init__(self, movementForward: float, movementSideways: float, yaw: float) -> None:
		"""Creates a new 'PlayerInput' Object with all other values set either to 0 or false\n
		Since: 1.4.0 

		Args:
			movementForward: 1 = forward input (W); 0 = no input; -1 = backward input (S) 
			yaw: yaw of the player 
			movementSideways: 1 = left input (A); 0 = no input; -1 = right input (D) 
		"""
		pass

	@overload
	def __init__(self, movementForward: float, yaw: float, jumping: bool, sprinting: bool) -> None:
		"""Creates a new 'PlayerInput' Object with all other values set either to 0 or false\n
		Since: 1.4.0 

		Args:
			movementForward: 1 = forward input (W); 0 = no input; -1 = backward input (S) 
			sprinting: sprint input 
			jumping: jump input 
			yaw: yaw of the player 
		"""
		pass

	@overload
	def __init__(self, input: Input, yaw: float, pitch: float, sprinting: bool) -> None:
		"""Creates a new 'PlayerInput' Object from a minecraft input with the missing values extra\n
		Since: 1.4.0 

		Args:
			input: Minecraft Input to be converted. 
			sprinting: sprint input 
			pitch: pitch of the player 
			yaw: yaw of the player 
		"""
		pass

	@overload
	def __init__(self, movementForward: float, movementSideways: float, yaw: float, pitch: float, jumping: bool, sneaking: bool, sprinting: bool) -> None:
		"""Creates a new 'PlayerInput' Object with all double values converted to floats\n
		Since: 1.4.0 

		Args:
			movementForward: 1 = forward input (W); 0 = no input; -1 = backward input (S) 
			sprinting: sprint input 
			jumping: jump input 
			sneaking: sneak input 
			pitch: pitch of the player 
			yaw: yaw of the player 
			movementSideways: 1 = left input (A); 0 = no input; -1 = right input (D) 
		"""
		pass

	@overload
	def __init__(self, movementForward: float, movementSideways: float, yaw: float, pitch: float, jumping: bool, sneaking: bool, sprinting: bool) -> None:
		"""Creates a new 'PlayerInput' Object\n
		Since: 1.4.0 

		Args:
			movementForward: 1 = forward input (W); 0 = no input; -1 = backward input (S) 
			sprinting: sprint input 
			jumping: jump input 
			sneaking: sneak input 
			pitch: pitch of the player 
			yaw: yaw of the player 
			movementSideways: 1 = left input (A); 0 = no input; -1 = right input (D) 
		"""
		pass

	@overload
	def __init__(self, input: "PlayerInput") -> None:
		"""Creates a clone 'PlayerInput' Object\n
		Since: 1.4.0 

		Args:
			input: the 'PlayerInput' object to be cloned 
		"""
		pass

	@overload
	def fromCsv(self, csv: str) -> List["PlayerInput"]:
		"""Parses each row of CSV string into a 'PlayerInput' .
The capitalization of the header matters. About the columns:  
-  'movementForward' and 'movementSideways' as a number  
- 'yaw' and 'pitch' as an absolute number  
- 'jumping' , 'sneaking' and 'sprinting' have to be boolean   
The separation must be a "," it's a csv...(but spaces don't matter) Quoted values don't work\n
		Since: 1.4.0 

		Args:
			csv: CSV string to be parsed 

		Returns:
			'List<PlayerInput>' Each row parsed as a 'PlayerInput' 
		"""
		pass

	@overload
	def fromJson(self, json: str) -> "PlayerInput":
		"""Parses a JSON string into a 'PlayerInput' Object
For details see 'PlayerInput.fromCsv()' , on what has to be present. Capitalization of the keys matters.\n
		Since: 1.4.0 

		Args:
			json: JSON string to be parsed 

		Returns:
			The JSON parsed into a 'PlayerInput' 
		"""
		pass

	@overload
	def toString(self, varNames: bool) -> str:
		"""Converts the current object into a string.
This can be used to convert current inputs created using 'Player.getCurrentPlayerInput()' to either JSON or CSV. 
The output can be converted into a PlayerInput object again by using either 'fromCsv(String, String)' or 'fromJson(String)' .\n
		Since: 1.4.0 

		Args:
			varNames: whether to include variable Names(=JSON) or not(=CSV) 

		Returns:
			The 'PlayerInput' object as a string 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def clone(self) -> "PlayerInput":
		pass

	pass


