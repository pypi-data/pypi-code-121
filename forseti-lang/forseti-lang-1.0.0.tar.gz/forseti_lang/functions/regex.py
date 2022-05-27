from .base import BaseFunction

from re import search


class Regex(BaseFunction):
	def __init__(self, command: str, text: str):
		super().__init__(command, text)

	def execute(self) -> bool:
		return bool(search(self.command, self.text))
