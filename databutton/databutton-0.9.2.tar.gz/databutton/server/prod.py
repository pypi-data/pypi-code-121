import logging
import os

import sentry_sdk
from databutton_web import get_static_file_path
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from databutton.version import __version__

from databutton.server.processes import StreamlitProcess
from databutton.utils import get_databutton_config
from databutton.utils.build import (
    load_schedules,
    read_artifacts_json,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

components = read_artifacts_json()

load_schedules(components)
# Set up proxies for streamlit apps
# They are ran as containers somewhere
for st in components.streamlit_apps:
    p = StreamlitProcess(st.route, "", st.port)
    p.add_route_to_app(app)


@app.get("/")
async def index():
    return RedirectResponse(url="/index.html")


app_dir = get_static_file_path()
app.mount("/static", StaticFiles(directory=".databutton"), name=".databutton")
app.mount("/", StaticFiles(directory=app_dir), name="app")


@app.get("/healthz")
async def healthz():
    return Response(status_code=status.HTTP_200_OK)


if os.environ.get("SENTRY_DSN"):
    logging.info("Found SENTRY_DSN, logging errors")
    sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"))
    config = get_databutton_config()
    sentry_tags = {
        "databutton_release": os.environ.get("DATABUTTON_RELEASE", "latest"),
        "databutton_project_id": config.uid,
        "databutton_project_name": config.name,
        "databutton_version": __version__,
    }
    for k, v in sentry_tags.items():
        sentry_sdk.set_tag(k, v)

    app = SentryAsgiMiddleware(app)
