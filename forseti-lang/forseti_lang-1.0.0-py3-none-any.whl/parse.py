from typing import List
from .exceptions import ForsetiSyntaxError


def parse_items(condition: str) -> List[List[str]]:
	buffer = ""
	stack = [[]]
	conditions = list()
	conditions.append(stack[-1])

	for char in condition:
		if char == "(":
			if not stack:
				raise ForsetiSyntaxError("The closing bracket is met before using the opening one")

			if buffer:
				stack[-1].append(buffer[:])

			stack.append([])
			stack[-2].append(len(conditions))
			conditions.append(stack[-1])

			buffer = ""

		elif char == ")":
			if not stack:
				raise ForsetiSyntaxError("The closing bracket is met before using the opening one")

			if buffer:
				stack[-1].append(buffer[:])

			del stack[-1]

			buffer = ""

		else:
			buffer += char

	if buffer:
		conditions[0].append(buffer)

	return conditions
