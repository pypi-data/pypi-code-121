from typing import overload
from typing import List
from .BaseLibrary import BaseLibrary
from .Inventory import Inventory
from .ClientPlayerEntityHelper import ClientPlayerEntityHelper
from .BlockDataHelper import BlockDataHelper
from .EntityHelper import EntityHelper
from .MethodWrapper import MethodWrapper
from .PlayerInput import PlayerInput
from .PositionCommon_Pos3D import PositionCommon_Pos3D


class FPlayer(BaseLibrary):
	"""Functions for getting and modifying the player's state.

An instance of this class is passed to scripts as the 'Player' variable.
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def openInventory(self) -> Inventory:
		"""

		Returns:
			the Inventory handler 
		"""
		pass

	@overload
	def getPlayer(self) -> ClientPlayerEntityHelper:
		"""
		Since: 1.0.3 

		Returns:
			the player entity wrapper. 
		"""
		pass

	@overload
	def getGameMode(self) -> str:
		"""
		Since: 1.0.9 

		Returns:
			the player's current gamemode. 
		"""
		pass

	@overload
	def rayTraceBlock(self, distance: float, fluid: bool) -> BlockDataHelper:
		"""
		Since: 1.0.5 

		Args:
			distance: 
			fluid: 

		Returns:
			the block/liquid the player is currently looking at. 
		"""
		pass

	@overload
	def rayTraceEntity(self) -> EntityHelper:
		"""
		Since: 1.0.5 

		Returns:
			the entity the player is currently looking at. 
		"""
		pass

	@overload
	def writeSign(self, l1: str, l2: str, l3: str, l4: str) -> bool:
		"""Write to a sign screen if a sign screen is currently open.\n
		Since: 1.2.2 

		Args:
			l1: 
			l2: 
			l3: 
			l4: 

		Returns:
			of success. 
		"""
		pass

	@overload
	def takeScreenshot(self, folder: str, callback: MethodWrapper) -> None:
		"""
		Since: 1.2.6 

		Args:
			folder: 
			callback: calls your method as a Consumer TextHelper 
		"""
		pass

	@overload
	def takeScreenshot(self, folder: str, file: str, callback: MethodWrapper) -> None:
		"""Take a screenshot and save to a file. 
'file' is the optional one, typescript doesn't like it not being the last one that's optional\n
		Since: 1.2.6 

		Args:
			folder: 
			file: 
			callback: calls your method as a Consumer TextHelper 
		"""
		pass

	@overload
	def createPlayerInput(self) -> PlayerInput:
		"""Creates a new PlayerInput object.\n
		Since: 1.4.0 
		"""
		pass

	@overload
	def createPlayerInput(self, movementForward: float, movementSideways: float, yaw: float) -> PlayerInput:
		"""Creates a new PlayerInput object.\n
		Since: 1.4.0 
		"""
		pass

	@overload
	def createPlayerInput(self, movementForward: float, yaw: float, jumping: bool, sprinting: bool) -> PlayerInput:
		"""Creates a new PlayerInput object.\n
		Since: 1.4.0 
		"""
		pass

	@overload
	def createPlayerInput(self, movementForward: float, movementSideways: float, yaw: float, pitch: float, jumping: bool, sneaking: bool, sprinting: bool) -> PlayerInput:
		"""Creates a new PlayerInput object.\n
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
	def createPlayerInputsFromCsv(self, csv: str) -> List[PlayerInput]:
		"""Parses each row of CSV string into a 'PlayerInput' .
The capitalization of the header matters. About the columns:  
-  'movementForward' and 'movementSideways' as a number  
- 'yaw' and 'pitch' as an absolute number  
- 'jumping' , 'sneaking' and 'sprinting' have to be boolean   
The separation must be a "," it's a csv...(but spaces don't matter) Quoted values don't work\n
		Since: 1.4.0 

		Args:
			csv: CSV string to be parsed 
		"""
		pass

	@overload
	def createPlayerInputsFromJson(self, json: str) -> PlayerInput:
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
	def getCurrentPlayerInput(self) -> PlayerInput:
		"""Creates a new 'PlayerInput' object with the current inputs of the player.\n
		Since: 1.4.0 
		"""
		pass

	@overload
	def addInput(self, input: PlayerInput) -> None:
		"""Adds a new 'PlayerInput' to 'MovementQueue' to be executed\n
		Since: 1.4.0 

		Args:
			input: the PlayerInput to be executed 
		"""
		pass

	@overload
	def addInputs(self, inputs: List[PlayerInput]) -> None:
		"""Adds multiple new 'PlayerInput' to 'MovementQueue' to be executed\n
		Since: 1.4.0 

		Args:
			inputs: the PlayerInputs to be executed 
		"""
		pass

	@overload
	def clearInputs(self) -> None:
		"""Clears all inputs in the 'MovementQueue'\n
		Since: 1.4.0 
		"""
		pass

	@overload
	def setDrawPredictions(self, val: bool) -> None:
		pass

	@overload
	def predictInput(self, input: PlayerInput) -> PositionCommon_Pos3D:
		"""Predicts where one tick with a 'PlayerInput' as input would lead to.\n
		Since: 1.4.0 

		Args:
			input: the PlayerInput for the prediction 

		Returns:
			the position after the input 
		"""
		pass

	@overload
	def predictInput(self, input: PlayerInput, draw: bool) -> PositionCommon_Pos3D:
		"""Predicts where one tick with a 'PlayerInput' as input would lead to.\n
		Since: 1.4.0 

		Args:
			input: the PlayerInput for the prediction 
			draw: whether to visualize the result or not 

		Returns:
			the position after the input 
		"""
		pass

	@overload
	def predictInputs(self, inputs: List[PlayerInput]) -> List[PositionCommon_Pos3D]:
		"""Predicts where each 'PlayerInput' executed in a row would lead
without drawing it.\n
		Since: 1.4.0 

		Args:
			inputs: the PlayerInputs for each tick for the prediction 

		Returns:
			the position after each input 
		"""
		pass

	@overload
	def predictInputs(self, inputs: List[PlayerInput], draw: bool) -> List[PositionCommon_Pos3D]:
		"""Predicts where each 'PlayerInput' executed in a row would lead\n
		Since: 1.4.0 

		Args:
			inputs: the PlayerInputs for each tick for the prediction 
			draw: whether to visualize the result or not 

		Returns:
			the position after each input 
		"""
		pass

	@overload
	def moveForward(self, yaw: float) -> None:
		"""Adds a forward movement with a relative yaw value to the MovementQueue.\n
		Since: 1.4.0 

		Args:
			yaw: the relative yaw for the player 
		"""
		pass

	@overload
	def moveBackward(self, yaw: float) -> None:
		"""Adds a backward movement with a relative yaw value to the MovementQueue.\n
		Since: 1.4.0 

		Args:
			yaw: the relative yaw for the player 
		"""
		pass

	@overload
	def moveStrafeLeft(self, yaw: float) -> None:
		"""Adds sideways movement with a relative yaw value to the MovementQueue.\n
		Since: 1.4.2 

		Args:
			yaw: the relative yaw for the player 
		"""
		pass

	@overload
	def moveStrafeRight(self, yaw: float) -> None:
		"""Adds sideways movement with a relative yaw value to the MovementQueue.\n
		Since: 1.4.2 

		Args:
			yaw: the relative yaw for the player 
		"""
		pass

	pass


