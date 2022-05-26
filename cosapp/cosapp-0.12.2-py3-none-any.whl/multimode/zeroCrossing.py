import enum
import re
from typing import Dict, NamedTuple
from cosapp.utils.helpers import check_arg


@enum.unique
class EventDirection(enum.Enum):
    """Enum covering zero-crossing directions"""
    UP = {
        'desc': "Upward zero-crossing",
        'func': (lambda prev, curr: curr > prev and curr * prev <= 0),
    }
    DOWN = {
        'desc': "Downward zero-crossing",
        'func': (lambda prev, curr: curr < prev and curr * prev <= 0),
    }
    UPDOWN = {
        'desc': "Up- or downward zero-crossing",
        'func': (lambda prev, curr: curr != prev and prev * curr <= 0),
    }

    def zero_detected(self, prev, curr) -> bool:
        detector = self.value['func']
        return detector(prev, curr)


class ZeroCrossing(NamedTuple):
    expression: str
    direction: EventDirection

    @classmethod
    def up(cls, expression: str) -> "ZeroCrossing":
        return cls(expression, EventDirection.UP)
 
    @classmethod
    def down(cls, expression: str) -> "ZeroCrossing":
        return cls(expression, EventDirection.DOWN)
 
    @classmethod
    def updown(cls, expression: str) -> "ZeroCrossing":
        return cls(expression, EventDirection.UPDOWN)
 
    @classmethod
    def from_comparison(cls, expression: str) -> "ZeroCrossing":
        """Interpret an expression of the kind 'lhs <op> rhs'
        as a `ZeroCrossing` object, where <op> is one of
        comparison operators:
        - `<`, `<=`
        - `==`
        - `>`, `>=`
        """
        check_arg(expression, "expression", str)
        operators = cls.operators()
        not_in_sides = list(operators) + ["="]

        def side_ok(side: str) -> bool:
            return not any(nope in side for nope in not_in_sides) and side.strip()

        for operator, direction in operators.items():
            try:
                lhs, rhs = expression.split(operator, maxsplit=1)
            except:
                continue
            if side_ok(lhs) and side_ok(rhs):
                return cls(f"{lhs.strip()} - ({rhs.strip()})", direction)

        raise ValueError(
            f"Expected a comparison between two expressions involving one of {tuple(operators)}"
            f"; got {expression!r}."
        )

    @classmethod
    def operators(cls) -> Dict[str, EventDirection]:
        return {
            "<" : EventDirection.DOWN,
            "<=": EventDirection.DOWN,
            "==": EventDirection.UPDOWN,
            ">=": EventDirection.UP,
            ">" : EventDirection.UP,
        }
