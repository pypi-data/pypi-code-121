from types import TracebackType
from typing import TYPE_CHECKING
from typing import Generic
from typing import Optional
from typing import Pattern
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import cast

from _pytest.outcomes import fail


_E = TypeVar("_E", bound=BaseException)

if TYPE_CHECKING:
    from _pytest._code import ExceptionInfo


class RaisesContext(Generic[_E]):
    def __init__(
        self,
        expected_exception: Union["Type[_E]", Tuple["Type[_E]", ...]],
        message: str,
        match_expr: Optional[Union[str, "Pattern"]] = None,
    ) -> None:
        self.expected_exception = expected_exception
        self.message = message
        self.match_expr = match_expr
        self.excinfo: Optional["ExceptionInfo[_E]"] = None

    def __enter__(self) -> "ExceptionInfo[_E]":
        from _pytest._code import ExceptionInfo

        self.excinfo = ExceptionInfo.for_later()

        return self.excinfo

    def __exit__(
        self,
        exc_type: Optional[Type[_E]],
        exc_val: Optional[_E],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        __tracebackhide__ = True
        if exc_type is None:
            fail(self.message)
        assert self.excinfo is not None
        if not issubclass(exc_type, self.expected_exception):
            return False
        # Cast to narrow the exception type now that it's verified.
        exc_info = cast(
            Tuple["Type[_E]", _E, TracebackType], (exc_type, exc_val, exc_tb)
        )
        self.excinfo.fill_unfilled(exc_info)
        if self.match_expr is not None:
            self.excinfo.match(self.match_expr)
        return True
