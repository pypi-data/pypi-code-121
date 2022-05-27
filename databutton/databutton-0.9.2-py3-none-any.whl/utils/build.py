import asyncio
import importlib
import logging
import os
import shutil
import sys
from dataclasses import dataclass, field
from typing import List

import schedule
from dataclasses_json import dataclass_json

import databutton as db
from databutton.decorators.schedule import DatabuttonSchedule
from databutton.decorators.streamlit import StreamlitApp
from databutton.helpers import parse
from databutton.kubernetes.generate import generate_manifest
from databutton.utils import catch_exceptions
from databutton.version import __version__


@dataclass_json
@dataclass
class ArtifactDict:
    streamlit_apps: List[StreamlitApp] = field(default_factory=List)
    schedules: List[DatabuttonSchedule] = field(default_factory=List)


def load_schedules(artifacts: ArtifactDict):
    for sched in artifacts.schedules:
        mod = importlib.import_module(sched.module_name)
        func = getattr(mod, sched.func_name)
        unstoppable_func = catch_exceptions(cancel_on_failure=sched.cancel_on_failure)(
            func
        )
        schedule.every(sched.seconds).seconds.do(unstoppable_func)

    async def run_continously():
        while True:
            try:
                schedule.run_pending()
                await asyncio.sleep(1)
            except Exception as e:
                logging.info(e)
                # Log to sentry if configured
                if os.environ.get("SENTRY_DSN"):
                    from sentry_sdk import capture_exception

                    capture_exception(e)

    asyncio.create_task(run_continously())


def generate_artifacts_json():
    # Sort the apps so that the port proxy remains stable
    for i, st in enumerate(sorted(db._streamlit_apps, key=lambda x: x.route)):
        st.port = 8501 + i
    artifacts = ArtifactDict(
        streamlit_apps=[st for st in db._streamlit_apps],
        schedules=[sched for sched in db._schedules],
    )
    return artifacts


def write_artifacts_json(artifacts: ArtifactDict):
    with open(".databutton/artifacts.json", "w") as f:
        f.write(artifacts.to_json())


def read_artifacts_json() -> ArtifactDict:
    with open(".databutton/artifacts.json", "r") as f:
        return ArtifactDict.from_json(f.read())


def generate_components(rootdir=os.curdir):
    sys.path.append(os.curdir)
    sys.path.append(os.curdir + "/.databutton")
    # Find all directive modules and import them
    imports = parse.find_databutton_directive_modules(rootdir=rootdir)

    # Clean the existing artifacts, generate new one
    # TODO: Have a cache mechanism to improve performance
    shutil.rmtree(".databutton", ignore_errors=True)
    os.makedirs(".databutton")
    decorator_modules = {}
    for name in imports:
        decorator_modules[name] = importlib.import_module(name)

    # Write the artifacts
    # Sort the apps so that the port proxy remains stable
    artifacts = generate_artifacts_json()
    write_artifacts_json(artifacts)

    # Copy the Dockerfile
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.mkdir(".databutton/docker")
    dockerfile_path = os.path.join(dir_path, "../docker/Dockerfile")
    dest_dockerfile_path = ".databutton/docker/Dockerfile"
    with open(dockerfile_path, "r") as original:
        contents = original.read()
        with open(dest_dockerfile_path, "w") as dest:
            dest.write(
                # Overwrite image
                contents.replace("REPLACE_ME_VERSION", __version__)
            )

    # Generate a kubernetes manifest

    generate_manifest(artifacts)
    return artifacts
