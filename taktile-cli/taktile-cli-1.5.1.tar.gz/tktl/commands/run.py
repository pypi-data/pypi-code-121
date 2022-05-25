from typing import Dict, Optional

from tktl.commands.validate import build_image, get_docker_manager
from tktl.core.loggers import LOG, stream_blocking_logs


def run_container(
    path: str,
    cache: bool,
    prune: bool,
    background: bool,
    auth_enabled: bool,
    reload: bool,
    color_logs: bool,
    secrets: Optional[Dict[str, str]] = None,
):
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)

    LOG.log("Waiting for service to start...")
    arrow_container, rest_container = dm.run_containers(
        image, detach=True, auth_enabled=auth_enabled, reload=reload, secrets=secrets
    )

    if background:
        return arrow_container, rest_container
    stream_blocking_logs(arrow_container, rest_container, color_logs=color_logs)
