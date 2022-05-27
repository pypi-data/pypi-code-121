from fastapi.requests import Request
from fastapi.responses import JSONResponse


class LinePayException(Exception):
    def __init__(self, error: str, detail: str = "") -> None:
        super().__init__(error)
        self.error = error
        self.detail = detail


def linepay_exception_handler(request: Request, exc: LinePayException) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": exc.error, "detail": exc.detail},
    )
