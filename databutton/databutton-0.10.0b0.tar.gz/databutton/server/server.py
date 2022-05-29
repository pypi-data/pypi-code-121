import os
import shutil
import sys
import time

import click
from databutton_web import get_static_file_path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from databutton.server.processes import _streamlit_processes, start_processes
from databutton.utils.build import (
    generate_components,
    load_schedules,
    write_artifacts_json,
)
from databutton.utils.log_status import log_devserver_screen

start_time = time.time()
app = FastAPI()
sys.path.insert(0, os.curdir)
sys.path.append(os.curdir + "/.databutton")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create .databutton if not exists
if not os.path.exists(".databutton"):
    os.mkdir(".databutton")

shutil.rmtree(".databutton/app", ignore_errors=True)
shutil.rmtree(".databutton/data", ignore_errors=True)

artifacts = generate_components()

write_artifacts_json(artifacts)
load_schedules(artifacts)

app.mount("/static", StaticFiles(directory=".databutton"), name=".databutton")

app_dir = get_static_file_path()


@app.on_event("startup")
async def start_servers():
    await start_processes(app, artifacts.streamlit_apps)

    @app.get("/")
    async def index():
        return RedirectResponse(url="/index.html")

    app.mount("/", StaticFiles(directory=app_dir), name="app")
    time_spent_starting = int((time.time() - start_time) * 1000)
    log_devserver_screen(components=artifacts, time_spent_starting=time_spent_starting)


@app.on_event("shutdown")
async def shutdown_event():
    # close connections here
    click.echo()
    click.echo(click.style("stopping...", fg="green"))
    for process in _streamlit_processes.values():
        process.stop()
