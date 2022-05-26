##
# File: main.py
# Date: 11-Aug-2020
#
# Template/skeleton web service application
#
##
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.security.utils import get_authorization_scheme_param

# pylint: disable=wrong-import-position
# This environment must be set before JWTAuthBearer is imported
HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
os.environ["CACHE_PATH"] = os.environ.get("CACHE_PATH", os.path.join("rcsb", "app", "data"))
os.environ["CONFIG_FILE"] = os.environ.get("CONFIG_FILE", os.path.join("rcsb", "app", "config", "config.yml"))

from . import ConfigProvider
from . import LogFilterUtils
from . import downloadRequest  # This triggers JWTAuthBearer
from . import serverStatus
from . import uploadRequest
from . import fileStatus
from .JWTAuthBearer import JWTAuthBearer

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
# The following mimics the default Gunicorn logging format
formatter = logging.Formatter("%(asctime)s [%(process)d] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s", "[%Y-%m-%d %H:%M:%S %z]")
# The following mimics the default Uvicorn logging format
# formatter = logging.Formatter("%(levelname)s:     %(asctime)s-%(module)s.%(funcName)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = True
# Apply logging filters -
lu = LogFilterUtils.LogFilterUtils()
lu.addFilters()
# ---

app = FastAPI()


@app.on_event("startup")
async def startupEvent():
    # Note that this will run every time a test is performed via, "with TestClient(app) as...",
    # but in production will only run once at startup
    #
    cachePath = os.environ.get("CACHE_PATH")
    configFilePath = os.environ.get("CONFIG_FILE")
    #
    logger.debug("Startup - running application startup placeholder method using %r", cachePath)
    # logger.info("cachePath %s ", cachePath)
    # logger.info("configFilePath %s ", configFilePath)
    cp = ConfigProvider.ConfigProvider(cachePath, configFilePath)
    _ = cp.getConfig()
    _ = cp.getData()
    #


@app.on_event("shutdown")
def shutdownEvent():
    logger.debug("Shutdown - running application shutdown placeholder method")


app.include_router(
    uploadRequest.router,
    prefix="/file-v1",
)

app.include_router(
    downloadRequest.router,
    prefix="/file-v1",
)

app.include_router(
    fileStatus.router,
    prefix="/file-v1",
)

app.include_router(serverStatus.router)


@app.middleware("http")
async def checkToken(request: Request, callNext):
    authorization: str = request.headers.get("Authorization", None)
    if not authorization:
        return Response(status_code=403, content=b'{"detail":"Not authenticated"}', headers={"content-type": "application/json"})
    scheme, credentials = get_authorization_scheme_param(authorization)
    if scheme != "Bearer":
        return Response(status_code=403, content=b'{"detail":"Missing Bearer details"}', headers={"content-type": "application/json"})
    valid = JWTAuthBearer().validateToken(credentials)
    if not valid:
        return Response(status_code=403, content=b'{"detail":"Invalid or expired token"}', headers={"content-type": "application/json"})
        # logger.info("HTTPException %r ",  HTTPException(status_code=403, detail="Invalid or expired token"))  # How to get this to log in the main app output?
        # return HTTPException(status_code=403, detail="Invalid or expired token")
    else:
        response = await callNext(request)
        return response
