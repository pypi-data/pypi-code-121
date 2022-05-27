from .distance import Distance
from .length import Length
from .nearby import Nearby
from .regex import Regex

from re import search


def execute_automatically(command: str, text: str) -> bool:
	if command == "TRUE":		# ATOM
		return True

	elif command == "FALSE": 	# ATOM
		return False

	elif "|l" in command:
		return Length(command, text).res

	elif search(Distance.COMMAND_FORMAT, command):
		return Distance(command, text).res

	elif "|nearby " in command:
		return Nearby(command, text).res

	else:
		return Regex(command, text).res
