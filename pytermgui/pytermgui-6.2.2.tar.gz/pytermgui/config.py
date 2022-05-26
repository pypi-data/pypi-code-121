from __future__ import annotations

import yaml
from pathlib import Path
from typing import Protocol, Any
from dataclasses import dataclass

from .window_manager import Window

from .parser import tim

_WIDGET_TRACKER: list["Widget"] = []


from pytermgui.pretty import print


class ConfigLoader(Protocol):
    def __call__(self, path: Path | str) -> None:
        ...


_KNOWN_WIDGETS: dict[str, "Widget"] = {}


def register_if_not_known(t_widget: Type["Widget"]) -> bool:
    name = t_widget.__name__
    if name in _KNOWN_WIDGETS:
        return False

    _KNOWN_WIDGETS[name] = t_widget


register_if_not_known(Window)


def start_tracking(widget: "Widget") -> None:
    _WIDGET_TRACKER.append(widget)


def stop_tracking(widget: "Widget") -> None:
    _WIDGET_TRACKER.remove(widget)


def build_selectors(query: str) -> list[Callable[[Widget], bool]]:
    ...


def query(target: str) -> list[Widget]:

    matches = []
    for widget in _WIDGET_TRACKER:
        if type(widget).__name__ == target:
            matches.append(widget)

    if len(matches) == 0:
        print(f"No matches for {target!r}")

    return matches


def expand_key(base: object, key: str) -> tuple[Any, str]:
    parts = key.split(".")

    if len(parts) == 1:
        return base, key

    obj = getattr(base, parts[0])
    attr = parts.pop()

    for part in parts[1:]:
        obj = getattr(obj, part)

    return obj, attr


def load_yaml(path: Path | str, manager: ptg.WindowManager) -> None:
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    for key, value in data.get("markup", {}).items():
        tim.alias(key, value)

    for item in data.get("layout", []):
        key, value = list(item.keys())[0], list(item.values())[0]
        if key == "<break>":
            manager.layout.add_break()
            continue

        manager.layout.add_slot(key, **value)

    for key, value in data.get("config", {}).items():
        widgets = query(key)

        for i_key, i_value in value.items():
            for widget in widgets:
                base, attr = expand_key(widget, i_key)

                setattr(base, attr, i_value)
