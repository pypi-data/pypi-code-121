from importlib import import_module as _im
from pathlib import Path as _p

from vripper.parser._def import _PARSERS

__all__ = [
    _im(f".{f.stem}", __package__)
    for f in _p(__file__).parent.glob("*.py")
    if "__" not in f.stem
]


def get_parser_object(url: str):
    for name, parser_object in _PARSERS.items():
        if name in url and parser_object.is_active:
            return parser_object
    return None
