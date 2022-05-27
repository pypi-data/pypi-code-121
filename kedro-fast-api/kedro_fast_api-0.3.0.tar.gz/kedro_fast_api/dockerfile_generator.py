import shutil
import os
from kedro_fast_api.utils import project_path


def create_dockerfile() -> None:
    dockerfile = project_path("docker_files/Dockerfile")
    dockerignore = project_path("docker_files/.dockerignore")
    credentials = project_path("docker_files/create_credentials_in_kedro.py")

    shutil.copy(dockerfile, ".")
    shutil.copy(dockerignore, ".")
    shutil.copy(credentials, ".")