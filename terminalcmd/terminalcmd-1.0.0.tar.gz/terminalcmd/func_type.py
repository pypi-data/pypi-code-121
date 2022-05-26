from typing import NewType, Any


class __GhostFunctionType:
    def __init__(self, func: Any) -> None:
        self.func = func

    @property
    def __name__(self) -> str:
        try:
            return self.func.__name__
        except AttributeError:
            raise TypeError(f"Object '{self.func}' is not object having an attribute '__name__'.")


func_type = NewType("Function Type", __GhostFunctionType)
