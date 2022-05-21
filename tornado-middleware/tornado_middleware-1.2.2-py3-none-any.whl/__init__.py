from typing import Awaitable, Callable, Iterator, List, Literal, Union, Optional
from tornado.web import RequestHandler, OutputTransform, HTTPError
from functools import reduce

version = 'v1.2.2'

class MiddlewareHandler(RequestHandler):
    """
    Middleware support RequestHandler
    to create a middleware you must declare an async function where receive a next function and must start
    with 'middleware' or '_middleware' to be user
    """

    def _get_middlewares(
        self,
    ) -> Iterator[Callable[[Callable], Union[None, Awaitable[None]]]]:
        """
        Get all middlewares declared in the class
        """
        middlewares_name = filter(
            lambda x: x.startswith(("_middleware", "middleware")), sorted(dir(self))
        )
        return reversed(
            list(
                filter(
                    lambda fn: callable(fn),
                    map(lambda x: getattr(self, x), middlewares_name),
                )
            )
        )

    def __make_next(
        self,
        next: Callable[[], Awaitable[bool]],
        callback: Callable[[Callable], Union[None, Awaitable[None]]],
    ) -> Callable[[], Awaitable[bool]]:
        """
        Wraps a middleware in a next middleware function
        """

        async def next_wrapper() -> Awaitable[bool]:
            res = callback(next)
            if res is not None:
                await res

            return self._finished

        return next_wrapper

    async def __next_execute(self) -> Awaitable[Literal[True]]:
        """
        Wraps self._execute function into a next middleware function
        """
        res = super(MiddlewareHandler, self)._execute(
            self._transforms,
            *self._execute_args,
            **self._execute_kwargs,
        )

        if res is not None:
            await res

        return True

    def write_middleware_error(self, err: HTTPError):
        """
        Write an HTTPError into a HMTL error page
        """
        self.set_status(err.status_code)
        self.finish(
            "<html><title>%(code)d: %(message)s</title>"
            "<body>%(code)d: %(message)s</body></html>"
            % {"code": err.status_code, "message": err.log_message}
        )

    async def _execute(
        self, transforms: List[OutputTransform], *args: bytes, **kwargs: bytes
    ) -> Union[None]:
        self._transforms = transforms
        self._execute_args = args
        self._execute_kwargs = kwargs

        middleware_executor = reduce(
            self.__make_next, self._get_middlewares(), self.__next_execute
        )

        try:
            await middleware_executor()
        except HTTPError as err:
            self.write_middleware_error(err)


class OrderedMiddlewareHandler(MiddlewareHandler):
    """
    Apply ordering into a Middleware
    """

    _middleware_order: Optional[List[str]] = None

    def _get_middlewares(
        self,
    ) -> Iterator[Callable[[Callable], Union[None, Awaitable[None]]]]:
        if self._middleware_order is None or len(self._middleware_order) == 0:
            return super(OrderedMiddlewareHandler, self)._get_middlewares()
        else:
            return reversed(
                list(map(lambda x: getattr(self, x), self._middleware_order))
            )
