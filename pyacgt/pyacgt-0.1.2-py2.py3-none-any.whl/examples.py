# import typing_extensions as TE
# from typing_extensions import typing as T
from typing import List, Tuple, Any, Text

__all__ = ["squareKnotPres"]


def __dir__() -> List[Text]:
    return __all__


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    return globals()[name]


def squareKnotPres(p: int, q: int) -> Tuple[List[str], List[str]]:
    """
    Runs acme on `template`

    Parameters
    ----------
    p,q: int
        meridional slope parameters for $$\mu_{p/q}$$.

    Return
    ------
    Tuple[List[str],Words]
        returns the generators and relators for $$G_{p/q}$$.
    """
    if q == 2 * p + 1:
        return (["a", "b"], ["abaBAB", "a" * (p + 1) + "B" * p])
    elif p == 2 and q % 4 == 1:
        n = int((q - 1) / 4)
        return (["a", "b"], ["abaBAB", "aaBB" * n + "a"])
    elif p == 2 and q % 4 == 3:
        n = int((q - 3) / 4)
        return (["a", "b"], ["abaBAB", "aaBB" * (n + 1) + "b"])
    else:
        raise NotImplementedError(f"The case {p}/{q} is not yet implemented")
