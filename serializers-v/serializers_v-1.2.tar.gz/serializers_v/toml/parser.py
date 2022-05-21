from serializers_v.src.constants import TYPE
from serializers_v.json.parser import json_parser


def parser_to_toml(item):
    result = f"{item[TYPE]} = "
    quote = False
    for char in str(item):
        if char == '\'':
            quote = not quote
        if char == ":" and not quote:
            result += "="
            continue
        if char == "{" and not quote:
            result += "["
            continue
        if char == "}" and not quote:
            result += "]"
            continue
        if char == "[" and not quote:
            result += "("
            continue
        if char == "]" and not quote:
            result += ")"
            continue
        result += char

    return result


def parser_to_dict(item):
    result = ""
    depth = 0
    quote = False
    for char in item:
        if char == "[" and not quote:
            result += "{"
            depth += 1
            continue
        elif char == "]" and not quote:
            result += "}"
            depth -= 1
            continue
        elif char == "(" and not quote:
            result += "["
            depth += 1
            continue
        elif char == ")" and not quote:
            result += "]"
            depth -= 1
            continue
        elif char == "=" and not quote and depth != 0:
            result += ":"
            continue
        if depth != 0:
            result += char
