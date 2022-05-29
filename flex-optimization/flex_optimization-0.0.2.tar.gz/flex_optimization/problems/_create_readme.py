import json
from typing import Any

import flex_optimization as fo


class ProblemEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, fo.OptimizationType):
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


def write_problem(problem: fo.problems.ProblemClassification) -> str:
    text = ""
    text += f"# {problem.name}\n\n"
    text += to_two_col_table(problem.__dict__)
    text += f"{problem.func.__doc__}\n\n"
    text += f"![img of {problem.name}](imgs/{problem.name}.svg)"
    return text


def main():
    text = ""
    text += "# Problems\n\n"
    text += "----\n"
    text += "----\n\n"
    text += "This directory contains collection of classic and non-classical test problems for optimization."
    text += "\n\n----\n\n"

    problems = fo.problems.ProblemClassification.population
    for problem in problems:
        text += write_problem(problem)
        text += "\n----\n\n"

    with open("README.md", "w", encoding="UTF-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
