import os
import subprocess
import tarfile
from fnmatch import fnmatch
from time import sleep

import requests

from databutton.utils import ProjectConfig, get_auth_token

token = None


def get_firebase(path: str):
    global token
    if token is None:
        token = get_auth_token()
    return requests.get(
        f"https://firestore.googleapis.com/v1/projects/databutton/databases/(default)/documents/{path}",
        headers={"Authorization": f"Bearer {token}"},
    )


def wait_for_firebase_existence(path, retries=10):
    res = get_firebase(path)
    if res.status_code == 404:
        # This doesn't exist (yet), try again in 1 second
        sleep(5)
        return wait_for_firebase_existence(path)
    return res


def get_deployment(deployment_id):
    return wait_for_firebase_existence(f"deployments/{deployment_id}").json()


def get_build_status(build_id: str):
    json = get_firebase(f"cloud-builds/{build_id}").json()
    return json["fields"]["status"]["stringValue"]


def listen_to_build(deployment_id: str):
    deployment = get_deployment(deployment_id)
    build_id = deployment["fields"]["buildId"]["stringValue"]
    status = get_build_status(build_id)
    while status not in ["SUCCESS", "FAILURE"]:
        sleep(5)
        status = get_build_status(build_id)
    return build_id, status


def create_archive(
    name: str, source_dir: str = os.curdir, config: ProjectConfig = None
) -> str:
    ignore_files = config.exclude
    if ".databutton" in ignore_files:
        # We need this for deploying.
        ignore_files.remove(".databutton")
    generated_requirements = False
    if os.path.exists("pyproject.toml") and not os.path.exists("requirements.txt"):
        # This is a poetry project, export requirements.txt from poetry
        subprocess.run(
            "poetry export -f requirements.txt --output requirements.txt --without-hashes",
            shell=True,
        )
        generated_requirements = True

    def exclude_filter(tarinfo: tarfile.TarInfo):
        for ignore in ignore_files:
            if fnmatch(tarinfo.name, ignore):
                return None
        return tarinfo

    archive_path = os.path.join("/tmp", name)
    with tarfile.open(archive_path, "w:gz") as tar:
        for fn in os.listdir(source_dir):
            p = os.path.join(source_dir, fn)
            tar.add(p, arcname=fn, filter=exclude_filter)
    if generated_requirements:
        os.remove("requirements.txt")

    return archive_path
