from fastapi import FastAPI

from .metrics_router import metrics_router
from .prometheus_middleware import PrometheusMiddleware


def app():
    _app = FastAPI()
    _app.add_middleware(PrometheusMiddleware)
    _app.add_route("/metrics", metrics_router)

    return _app
