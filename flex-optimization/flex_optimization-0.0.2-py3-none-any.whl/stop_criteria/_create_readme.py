import json
from typing import Any

import flex_optimization as fo
from flex_optimization.core.stop_criteria import StopCriteria


def write_stop_criteria(stop_criteria: StopCriteria) -> str:
    text = ""
    text += f"# {stop_criteria.__name__}\n\n"
    text += f"{stop_criteria.__doc__}\n\n"
    return text


def main():
    text = ""
    text += "# Stopping Criteria\n\n"
    text += "----\n"
    text += "----\n\n"
    text += "This directory contains collection of stopping criteria for optimization."
    text += "\n\n----\n\n"

    stop_criterias = fo.stop_criteria.stopping_criteria
    for stop_criteria in stop_criterias.values():
        text += write_stop_criteria(stop_criteria)
        text += "\n----\n\n"

    with open("README.md", "w", encoding="UTF-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
