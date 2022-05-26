import time
from typing import Tuple

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, filter_unhandled_paths: bool = False) -> None:
        super().__init__(app)
        self.filter_unhandled_paths = filter_unhandled_paths
        self.REQUESTS = Counter(
            "request",
            "Counter of requests by method and path.",
            ["method", "path_template"],
        )
        self.RESPONSES = Counter(
            "response",
            "Counter of responses by method, path and status codes.",
            ["method", "path_template", "status_code"],
        )
        self.REQUESTS_PROCESSING_TIME = Histogram(
            "latency_in_sec",
            "Histogram of requests processing time by path (in seconds)",
            ["method", "path_template"],
        )
        self.EXCEPTIONS = Counter(
            "exception",
            "Count of exception raised by path and exception type",
            ["method", "path_template", "exception_type"],
        )
        self.REQUESTS_IN_PROGRESS = Gauge(
            "concurrent_request",
            "Concurrent request by method and path currently being processed",
            ["method", "path_template"],
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path_template, is_handled_path = self.get_path_template(request)

        if self._is_path_filtered(is_handled_path):
            return await call_next(request)

        self.REQUESTS_IN_PROGRESS.labels(
            method=method, path_template=path_template
        ).inc()
        self.REQUESTS.labels(method=method, path_template=path_template).inc()
        before_time = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            self.EXCEPTIONS.labels(
                method=method,
                path_template=path_template,
                exception_type=type(e).__name__,
            ).inc()
            raise e from None
        else:
            status_code = response.status_code
            after_time = time.perf_counter()
            self.REQUESTS_PROCESSING_TIME.labels(
                method=method, path_template=path_template
            ).observe(after_time - before_time)
        finally:
            self.RESPONSES.labels(
                method=method, path_template=path_template, status_code=status_code
            ).inc()
            self.REQUESTS_IN_PROGRESS.labels(
                method=method, path_template=path_template
            ).dec()

        return response

    @staticmethod
    def get_path_template(request: Request) -> Tuple[str, bool]:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True

        return request.url.path, False

    def _is_path_filtered(self, is_handled_path: bool) -> bool:
        return self.filter_unhandled_paths and not is_handled_path
