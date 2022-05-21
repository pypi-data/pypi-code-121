import logging
import sys

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from jwtserver import __version__
from jwtserver.api.v1.routers.reg import router as v1_router

__all__ = ['app', 'create_app']

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:5000",
    "http://localhost:3000",
]
description = """[Full JWT Server docs](https://jwtserver.darkdeal.net)"""
tags_metadata = [
    {
        "name": "Authorization",
        "description": "authorization",
    },
    {
        "name": "Registration",
        "description": "registration",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://jwtserver.darkdeal.net/en/api_v1/",
        },
    },
]


def create_app(_title='JWT server', lvl_logging='INFO') -> FastAPI:
    _app = FastAPI(
        title=_title,
        description=description,
        version=__version__,
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        openapi_tags=tags_metadata,
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(v1_router)
    # _app.dependency_overrides[get_settings] = get_settings
    # _app.dependency_overrides = {
    #     get_settings: lambda: _config,
    # }
    _app.debug = True

    # def enable_logger(sink=sys.stderr, level='DEBUG'):
    #     logging.basicConfig(level=logging.DEBUG)
    #     logger.configure(handlers=[{'sink': sink, 'level': level}])
    #     logger.enable('aria2p')
    #
    # enable_logger(level=lvl_logging)
    return _app


app = create_app()
