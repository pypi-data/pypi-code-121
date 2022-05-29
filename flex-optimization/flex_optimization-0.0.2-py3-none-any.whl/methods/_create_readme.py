import json
from typing import Any

import flex_optimization as fo


class MethodEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, fo.methods.MethodClassification):
            return {"_enum_": str(obj)}
        if callable(obj):
            return "Callable"
        return json.JSONEncoder.default(self, obj)


def to_two_col_table(dict_: dict, header: tuple[str] = ("key", "value")) -> str:
    text = f"|{header[0]} | {header[1]}|"
    text += "\n|" + "-" * 3 + "|" + "-" * 3 + "|\n"
    for k, v in dict_.items():
        text += f"|{k} | {v}| \n"

    return text


def write_method(method: fo.methods.MethodClassification) -> str:
    text = ""
    text += f"# {method.name}\n\n"
    text += to_two_col_table(method.__dict__)
    text += f"{method.func.__doc__}\n\n"
    # text += f"![img of {method.name}](imgs/{method.name}.svg)"
    return text


def main():
    text = ""
    text += "# Methods\n\n"
    text += "----\n"
    text += "----\n\n"
    text += "This directory contains collection of methods for optimization."
    text += "\n\n----\n\n"

    methods = fo.methods.MethodClassification.population
    for method in methods:
        text += write_method(method)
        text += "\n----\n\n"

    with open("README.md", "w", encoding="UTF-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
