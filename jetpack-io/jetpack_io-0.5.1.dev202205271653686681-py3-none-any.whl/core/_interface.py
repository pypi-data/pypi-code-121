import inspect
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union, cast

from deprecation import deprecated

from jetpack import _utils
from jetpack.config import _symbols
from jetpack.core._errors import NotAsyncError
from jetpack.core._jetpack_function import JetpackFunction
from jetpack.core._jetpack_function_with_client import schedule as schedule

T = TypeVar("T")
__pdoc__ = {}
__pdoc__["jet"] = "Alias for jetroutine"
__pdoc__["function"] = "Alias for jetroutine"

DecoratedFunc = Callable[..., Awaitable[T]]
"""DecoratedFunc is a type alias for the type of the python function that is
being decorated with @jetroutine.

It is required to be async.
"""


# @function is our general remote work decorator. It does not specify how the
# work will be done (RPC, job, queue, etc) and instead leaves that as an
# implementation detail.
def jetroutine_decorator(
    fn: Optional[Callable[..., T]] = None,
    # The stararg forces the arguments after that to be specified with the keyword
    #
    # > Parameters after “*” [...] are keyword-only parameters and may only be passed by keyword arguments
    # https://docs.python.org/3/reference/compound_stmts.html#function-definitions
    *,
    with_checkpointing: bool = False,
    endpoint_path: Optional[str] = None,
) -> Union[DecoratedFunc[T], Callable[[Callable[..., T]], DecoratedFunc[T]]]:
    """Decorator that wraps any async Python function, and runs it as a distributed function.

    Async python functions decorated with @jetroutine will be registered with
    the runtime. Calling these functions will run them as remote distributed functions,
    instead of running them locally.

    Arguments:
        fn (Optional[Callable[..., T]): (optional) The function being decorated.
        with_checkpointing (bool): Determines whether the jetroutine's execution
            will be re-tried upon failure until it succeeds or exceeds the max
            number of retries. Also see @workflow for the canonical way user programs
            should set this.

    Returns:
        If @jetroutine is decorated without any arguments on a function whose type is DecoratedFunc,
        then the return type is DecoratedFunc itself.

        If @jetroutine([arg...]) is decorated with some arguments on a function
        whose type is DecoratedFunc, then the return type is a Callable whose
        return type is DecoratedFunc.

    Raises:
        NotAsyncError (jetpack.errors.NotAsyncError): Raised if the function being decorated
          is not async.
        ApplicationError (jetpack.errors.ApplicationError): Raised if the jetroutine's business
          logic raises an error. This is usually caused by incorrect business logic.
          `ApplicationError` is an subtype of `JetpackError` (`jetpack.errors.JetpackError`)
        SystemError (jetpack.errors.SystemError): Raised if there was a jetpack-system or
          kubernetes error during execution of the jetroutine. This is usually not an error
          caused by incorrect business logic. `SystemError` is a subtype of `JetpackError` (`jetpack.errors.JetpackError`)
    """

    def wrapper(fn: Callable[..., T]) -> DecoratedFunc[T]:
        # Use asyncio.iscoroutine() instead?
        if not inspect.iscoroutinefunction(fn):
            raise NotAsyncError(
                f"Jetpack functions must be async. {_utils.qualified_func_name(fn)} is not async."
            )
        _symbols.get_symbol_table().register(fn, endpoint_path)
        task: JetpackFunction[T] = JetpackFunction(fn, with_checkpointing)
        return task

    return wrapper(fn) if fn else wrapper


@deprecated(details="Use jetroutine instead.")
def function(
    fn: Optional[Callable[..., T]] = None, *, with_checkpointing: bool = False
) -> Union[
    Callable[..., Awaitable[T]],
    Callable[[Callable[..., T]], Callable[..., Awaitable[T]]],
]:
    # can enable this print to be more aggressive, since smarthop and other
    # customers may not have python's dev-mode on to see the @deprecated decorator's
    # warning message:
    #
    # print("WARNING: @function is deprecated. Use @jetroutine instead.")

    return jetroutine_decorator(fn, with_checkpointing=with_checkpointing)


@deprecated(details="Use jetroutine instead.")
def jet(
    fn: Optional[Callable[..., T]] = None, *, with_checkpointing: bool = False
) -> Union[
    Callable[..., Awaitable[T]],
    Callable[[Callable[..., T]], Callable[..., Awaitable[T]]],
]:
    return jetroutine_decorator(fn, with_checkpointing=with_checkpointing)


jetroutine = jetroutine_decorator


def workflow(
    fn: Optional[Callable[..., T]] = None
) -> Union[
    Callable[..., Awaitable[T]],
    Callable[[Callable[..., T]], Callable[..., Awaitable[T]]],
]:
    """workflow is syntactical sugar for @jetroutine(with_checkpointing=true).

    It is introduced as its own decorator because `with_checkpointing=true` changes the runtime semantics
    of the jetroutine being invoked. This change also applies transitively to any child jetroutines
    that are invoked by the decorated function.

    Specifically, the semantics require the function to be idempotent. This is needed
    because the function may be re-run to ensure it completes successfully.
    """
    return jetroutine_decorator(fn, with_checkpointing=True)


def endpoint(
    fn: Optional[Callable[..., T]] = None,
    path: str = "",
) -> Union[
    Callable[..., Awaitable[T]],
    Callable[[Callable[..., T]], Callable[..., Awaitable[T]]],
]:
    """endpoint is syntactical sugar for @jetroutine(path="/some/path")."""
    return jetroutine_decorator(fn, endpoint_path=path)
