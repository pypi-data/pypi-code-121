import re
from typing import Callable
from inspect import getdoc, signature

from .constants import OPENAPI_FIELDS

TITLE_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


def format_field(field: dict) -> dict:
	# name: str, description: str, default: str, typ: str
	field = {
		"name": field["name"],
		"description": field.get("description", ""),
		"default": field.get("default"),
		"generated": field.get("generated", False),
	}
	for k, v in zip(("type", "format"), OPENAPI_FIELDS.get(field.get("field_type"), (field.get("field_type"),))):
		field[k] = v
	return field


def get_method_signature_data(m: Callable) -> dict:
	param_regex = re.compile(":param (.*):(.*)")
	ret = {}
	sig = signature(m)
	doc = getdoc(m)
	for p in (doc or "").split("\n"):
		r = param_regex.search(p)
		if r:
			arg_name = r.group(1)
			f = sig.parameters[arg_name]
			ret[arg_name] = format_field(
				{
					"name": arg_name,
					"description": r.group(2).strip(),
					"default": f.default.__name__ if not f.default == f.empty else None,
					"field_type": f.annotation.__name__,
				}
			)
	return ret


def title_to_snake(val: str) -> str:
	return TITLE_TO_SNAKE.sub("_", val).lower()
