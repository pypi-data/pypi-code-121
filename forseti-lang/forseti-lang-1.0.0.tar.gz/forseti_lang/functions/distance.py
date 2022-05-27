from .base import BaseFunction
from ..exceptions import ForsetiFunctionSyntaxError

from re import search, split as re_split


class Distance(BaseFunction):
	COMMAND_FORMAT = r'\s\|[cw]?\d+\s'

	def __init__(self, command: str, text: str):
		self.left_argument = ""
		self.right_argument = ""
		self.distance = -1
		self.f_exclude_right_argument = False

		super().__init__(command, text)

	def check_command(self):
		if bool(search(self.COMMAND_FORMAT, self.command)):
			parts = re_split(self.COMMAND_FORMAT, self.command)

			if len(parts) != 2:
				raise ForsetiFunctionSyntaxError("Command doesn't support combined-condition")

			command_to_exec = search(self.COMMAND_FORMAT, self.command).group(0).strip()

			if 'c' in command_to_exec or 'w' in command_to_exec:
				_p = 2
			else:
				_p = 1

			self.distance = int(command_to_exec[_p:])
			self.left_argument, self.right_argument = parts

			if self.right_argument[0] == '-':
				self.right_argument = self.right_argument[1:]
				self.f_exclude_right_argument = True

		else:
			raise ForsetiFunctionSyntaxError("Unsupported command format. You must use: {word1} [|c{number} or |w{number}] {word2}")

	def execute(self) -> bool:
		if "|w" in self.command:
			return self._by_words()

		elif "|c" in self.command:
			return self._by_characters()

		else:
			return self._by_words()

	def _by_words(self) -> bool:
		if not self._parts_in_text():
			return False

		command_parts = re_split(self.left_argument, self.text)[1:]

		for i in command_parts:
			if search(self.right_argument, i):
				word_distance = len(re_split(self.right_argument, i)[0].split())

				if word_distance <= self.distance:
					return not self.f_exclude_right_argument

		return False

	def _by_characters(self) -> bool:
		if not self._parts_in_text():
			return False

		command_parts = re_split(self.left_argument, self.text)[1:]

		for i in command_parts:
			if search(self.right_argument, i):
				word_distance = len(re_split(self.right_argument, i)[0])

				if word_distance <= self.distance:
					return not self.f_exclude_right_argument

		return False

	def _parts_in_text(self) -> bool:
		return bool(search(self.left_argument, self.text) and search(self.right_argument, self.text))
