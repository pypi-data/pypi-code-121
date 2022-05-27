from .functions.auto_execute import execute_automatically
from .parse import parse_items
from .checkers.all_ import check_all

from typing import List, Union


def execute_condition(condition: str, text: str) -> bool:
	check_all(condition)
	condition = condition.replace(" И ", " AND ").replace(" ИЛИ ", " OR ")
	condition_parts = parse_items(condition)
	res = execute_condition_parts(condition_parts, text)

	return res


def execute_condition_parts(condition_parts: List[List[Union[str, int]]], text: str) -> bool:
	text = text.lower()
	result = False

	for i in range(len(condition_parts) - 1, -1, -1):
		part = condition_parts[i]
		condition = part[0] if len(part) == 1 else "".join(part)

		_res = "TRUE" if execute_condition_part(condition, text) else "FALSE"		# Converts to atomic

		if i > 0:		# I'm not sure about this condition
			condition_part_id = find_place_to_insert_result(condition_parts, i)
			atom_id = condition_parts[condition_part_id].index(i)

			condition_parts[condition_part_id][atom_id] = _res

		else:
			result = True if _res == "TRUE" else False

	return result


def execute_condition_part(condition: str, text: str):
	res = True

	if " AND " in condition:
		condition_parts = condition.split(" AND ")

		for part in condition_parts:
			res &= execute_condition_part(part, text)

		return res

	if "NOT " in condition:
		condition_part = condition.split("NOT ")[1]
		return not execute_condition_part(condition_part, text)

	if " OR " in condition:
		condition_parts = condition.split(" OR ")
		res = False

		for part in condition_parts:
			res |= execute_condition_part(part, text)

		return res

	return execute_automatically(condition, text)


def find_place_to_insert_result(condition_parts: List[List[str]], command_id: int):
	for i in range(len(condition_parts)):
		if command_id in condition_parts[i]:
			return i

	raise IndexError("Can't find command with this id")
