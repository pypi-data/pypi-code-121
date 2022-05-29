from ._operators import *

registry = {}

registry["scheme"] = {
        "rungekutta": rungeKuttaSolver
        }
