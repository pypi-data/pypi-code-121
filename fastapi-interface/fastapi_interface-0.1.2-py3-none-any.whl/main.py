from fastapi.responses import ORJSONResponse


app_defaults = {
    "redoc_url": "/docs2",
    "default_response_class": ORJSONResponse,
}
