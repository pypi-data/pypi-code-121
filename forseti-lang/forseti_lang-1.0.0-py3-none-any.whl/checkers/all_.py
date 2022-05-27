from .staples import check_staples
from .syntax import check_syntax


def check_all(condition: str):
    check_staples(condition)
    check_syntax(condition)
