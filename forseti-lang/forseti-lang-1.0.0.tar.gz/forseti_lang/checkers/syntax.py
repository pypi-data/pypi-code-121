from typing import List

from ..exceptions import ForsetiSyntaxError


_OPERATORS = ("AND", "OR", "NOT", "И", "ИЛИ")
ERRORS = {
	"operator_position": "Operator '{}' is used without expression '{}'. Position {}",
}


def check_syntax(command: str):
	command = command.replace(" И ", " AND ")
	command = command.replace(" ИЛИ ", " OR ")
	command_parts = command.split()
	parts_number = len(command_parts)

	for i in range(parts_number):
		if command_parts[i] in _OPERATORS:
			word_start_symbol_num = get_word_start_symbol_num(i, command_parts)

			if i == 0:
				raise ForsetiSyntaxError(ERRORS['operator_position'].format(command_parts[i], 'левостороннего', word_start_symbol_num))

			elif i == parts_number - 1:
				raise ForsetiSyntaxError(ERRORS['operator_position'].format(command_parts[i], 'правостороннего', word_start_symbol_num))

			if command_parts[i] == "NOT":
				if command_parts[i - 1] != "AND":
					raise ForsetiSyntaxError("Operator 'NOT' cannot be used without operator 'AND'")

			if command_parts[i] in _OPERATORS:
				if command_parts[i - 1]:
					pass
		else:
			if i < parts_number - 1:
				if command_parts[i + 1].lstrip()[0] == '(' and command_parts[i] not in _OPERATORS:
					raise ForsetiSyntaxError("You can't use staples without operators")

			if i:
				if command_parts[i - 1].rstrip()[-1] == ')' and command_parts[i] not in _OPERATORS:
					raise ForsetiSyntaxError("You can't use staples without operators")


def get_word_start_symbol_num(word_position: int, split_text: List[str]):
	word_start_symbol_num = sum(map(len, split_text[:word_position])) + word_position

	return word_start_symbol_num + 1
