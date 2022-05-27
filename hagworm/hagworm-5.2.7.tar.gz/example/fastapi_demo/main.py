# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys
import uvicorn

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../../'))

from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health

from hagworm.frame.fastapi.base import DEFAULT_HEADERS, create_fastapi
from hagworm.extend.base import Utils
from hagworm.extend.logging import LogFileRotator

from setting import ConfigDynamic
from service.base import DataSource
from controller import router


app = create_fastapi(
    log_level=ConfigDynamic.LogLevel,
    log_file_path=ConfigDynamic.LogFilePath,
    log_file_rotation=LogFileRotator.make(ConfigDynamic.LogFileSplitSize, ConfigDynamic.LogFileSplitTime),
    log_file_retention=ConfigDynamic.LogFileBackups,
    debug=ConfigDynamic.Debug,
    routes=router.routes,
    # on_startup=[DataSource.initialize],
    # on_shutdown=[DataSource.release],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ConfigDynamic.AllowOrigins,
    allow_methods=ConfigDynamic.AllowMethods,
    allow_headers=ConfigDynamic.AllowHeaders,
    allow_credentials=ConfigDynamic.AllowCredentials,
)

# app.add_api_route(r'/health', health([DataSource.check_health]))


if __name__ == r'__main__':

    Utils.log.warning(r'THE PRODUCTION ENVIRONMENT IS STARTED USING GUNICORN')

    uvicorn.run(app, port=8080, log_config=None, headers=DEFAULT_HEADERS)
