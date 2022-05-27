from ..exceptions import ForsetiSyntaxError


def check_staples(command: str) -> None:
	if command.count('(') != command.count(')'):
		raise ForsetiSyntaxError("No closing/opening brackets")
