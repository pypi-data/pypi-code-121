import pathlib
import time
from typing import Dict, Optional

import docker  # type: ignore
import requests
from requests.exceptions import RequestException

from tktl.commands.health import check_grpc_health, check_rest_health
from tktl.core.config import settings
from tktl.core.exceptions import MissingDocker
from tktl.core.loggers import LOG

TESTING_DOCKERFILE = "Dockerfile.taktile-cli-testing"
MULTI_STAGE_BUILD_STEP_NAME = "build_step"


class DockerManager:
    def __init__(self, path):
        try:
            self._client = docker.from_env()
            self._path = pathlib.Path(path)
        except docker.errors.DockerException as err:
            raise MissingDocker from err

    def get_docker_file(self) -> str:
        with open(self._path / ".buildfile") as fp:
            return fp.read()

    def stream_logs(self, container) -> None:
        for line in container.logs(stream=True):
            LOG.log(f"> {line.decode()}".strip())

    def remove_image(self, image):
        self._client.images.remove(image, force=True)

    def build_image(
        self,
        dockerfile: str,
        cache: bool,
        prune: bool,
        buildargs: Optional[Dict] = None,
    ) -> str:

        if prune:
            try:
                image = self._client.images.get("taktile-cli-test:latest")
                self._client.images.remove(image.id)
            except docker.errors.ImageNotFound:
                pass

        if not cache:
            LOG.log("Building without Docker cache. This may take some time...")

        LOG.log(
            f"Multistage dockerfile, building target {MULTI_STAGE_BUILD_STEP_NAME}..."
        )
        image, stream = self._client.images.build(
            path=str(self._path),
            dockerfile=dockerfile,
            tag="taktile-cli-test",
            nocache=not cache,
            target=MULTI_STAGE_BUILD_STEP_NAME,
            buildargs=buildargs,
            forcerm=True,
        )

        for chunk in stream:
            if "stream" in chunk:
                for line in chunk["stream"].splitlines():
                    LOG.trace("> " + line)

        return image.id

    def test_import(self, image_id: str, secrets: Optional[Dict[str, str]] = None):
        if secrets is None:
            secrets = {}
        client_name = "tktl" if not settings.FUTURE_ENDPOINTS else "client"
        command = f"python -c 'from src.endpoints import {client_name}'"
        try:
            container = self._client.containers.run(
                image_id,
                command,
                detach=True,
                environment={
                    "TAKTILE_GIT_SHA": "local-run",
                    "TAKTILE_GIT_REF": "local-run",
                    **secrets,
                },
            )
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def test_endpoint_sample(
        self,
        image_id: str,
        secrets: Optional[Dict[str, str]] = None,
    ):
        if secrets is None:
            secrets = {}
        try:
            command = f"python /app/scripts/endpoint_sample_test{'_future' if settings.FUTURE_ENDPOINTS else ''}.py"
            container = self._client.containers.run(
                image_id,
                command,
                detach=True,
                environment={
                    "TAKTILE_GIT_SHA": "local-run",
                    "TAKTILE_GIT_REF": "local-run",
                    **secrets,
                },
            )
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def test_unittest(self, image_id: str, secrets: Optional[Dict[str, str]] = None):
        if secrets is None:
            secrets = {}
        try:
            container = self._client.containers.run(
                image_id,
                "python -m pytest ./user_tests/",
                detach=True,
                environment={
                    "TAKTILE_GIT_SHA": "local-run",
                    "TAKTILE_GIT_REF": "local-run",
                    **secrets,
                },
            )
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def run_rest_container(
        self,
        image_id: str,
        detach: bool = True,
        auth_enabled: bool = True,
        reload: bool = False,
        secrets: Optional[Dict[str, str]] = None,
    ):
        if secrets is None:
            secrets = {}
        assets_path = (self._path / "assets").resolve()
        src_path = (self._path / "src").resolve()
        return self._client.containers.run(
            image_id,
            entrypoint="/start-reload.sh" if reload else "/start-rest.sh",
            detach=detach,
            environment={
                "AUTH_ENABLED": auth_enabled,
                "TAKTILE_GIT_SHA": "local-run",
                "TAKTILE_GIT_REF": "local-run",
                **secrets,
            },
            ports={"80/tcp": 8080},
            remove=True,
            stderr=True,
            stdout=True,
            volumes=[
                f"{assets_path}:/app/assets",
                f"{src_path}:/app/src",
            ]
            if reload
            else [],
        )

    def run_arrow_container(
        self,
        image_id: str,
        detach: bool = True,
        auth_enabled: bool = True,
        secrets: Optional[Dict[str, str]] = None,
    ):
        if secrets is None:
            secrets = {}
        return self._client.containers.run(
            image_id,
            detach=detach,
            entrypoint="/start-flight.sh",
            environment={
                "AUTH_ENABLED": auth_enabled,
                "TAKTILE_GIT_SHA": "local-run",
                "TAKTILE_GIT_REF": "local-run",
                **secrets,
            },
            ports={"5005/tcp": 5005},
            remove=True,
            stderr=True,
            stdout=True,
        )

    def run_containers(
        self,
        image_id: str,
        detach: bool = True,
        auth_enabled: bool = True,
        reload: bool = False,
        secrets: Optional[Dict[str, str]] = None,
    ):
        arrow_container = self.run_arrow_container(
            image_id=image_id, detach=detach, auth_enabled=auth_enabled, secrets=secrets
        )
        rest_container = self.run_rest_container(
            image_id=image_id,
            detach=detach,
            auth_enabled=auth_enabled,
            reload=reload,
            secrets=secrets,
        )
        return arrow_container, rest_container

    def run_profiling_container(self):
        try:
            image_name = f"taktile/taktile-profiler:{_get_profiling_version()}"
            LOG.debug(f"Using Profiling Image {image_name}")
            container = self._client.containers.run(
                image_name,
                entrypoint="profiler profile -l",
                network_mode="host",
                detach=True,
            )
            self.stream_logs(container)
            status = container.wait()
            return status, container
        finally:
            container.remove()

    def run_and_check_health(
        self,
        image_id: str,
        kill_on_success: bool = False,
        auth_enabled: bool = True,
        timeout: int = 7,
        retries: int = 7,
        secrets: Optional[Dict[str, str]] = None,
    ):
        if secrets is None:
            secrets = {}
        arrow_container, rest_container = self.run_containers(
            image_id=image_id, detach=True, auth_enabled=auth_enabled, secrets=secrets
        )

        try:
            while True:
                try:
                    time.sleep(timeout)
                    check_grpc_health()
                    check_rest_health()
                    return arrow_container, rest_container
                except Exception:
                    if retries > 0:
                        retries -= 1
                    else:
                        raise

        finally:
            if kill_on_success:
                arrow_container.kill()
                rest_container.kill()


def _get_profiling_version() -> str:
    if settings.TAKTILE_PROFILING_VERSION:
        return settings.TAKTILE_PROFILING_VERSION
    else:
        try:
            res = requests.get(f"{settings.LOCAL_REST_ENDPOINT}/info").json()
            if isinstance(res, list):  # Not Future
                profiling_version = "latest"
            else:  # Future
                profiling_version = res.get("profiling", "latest")
        except RequestException as e:
            LOG.debug(f"Failed to fetch profiling version from Info {e}")
            profiling_version = "latest"
        return profiling_version
