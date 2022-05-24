from typing import Any, Dict

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, status
from model2api.api.fastapi_utils import configure_logging, patch_fastapi
from model2api.core import Predictor
from starlette.responses import RedirectResponse


def launch_api(opyrator_path: str, port: int = 8501, host: str = "0.0.0.0") -> None:
    import uvicorn
    from model2api.api import create_api

    app = create_api(Predictor(opyrator_path))

    uvicorn.run(app, host=host, port=port)


def create_api(predictor: Predictor) -> FastAPI:

    title = predictor.name
    if "model" not in predictor.name.lower():
        title += " - model"
    app = FastAPI(title=title, description=predictor.description)
    app.add_middleware(CorrelationIdMiddleware, header_name="x-correlation-id")
    patch_fastapi(app)

    @app.on_event("startup")
    async def on_startup():
        configure_logging()

    @app.post(
        "/predict",
        operation_id="predict",
        response_model=predictor.output_type,
        summary="Execute the predictor.",
        status_code=status.HTTP_200_OK,
    )
    def predict(input: predictor.input_type) -> Any:  # type: ignore
        """Executes this predictor."""
        return predictor(input)

    @app.get(
        "/actuators/health",
        operation_id="health",
        response_model=Dict,
        summary="health actuator",
        status_code=status.HTTP_200_OK,
    )
    def health() -> Any:  # type: ignore
        return {"status": "up"}

    # Redirect to docs
    @app.get("/", include_in_schema=False)
    def root() -> Any:
        return RedirectResponse("./docs")

    return app
