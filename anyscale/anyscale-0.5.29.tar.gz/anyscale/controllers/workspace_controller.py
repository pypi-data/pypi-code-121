import shlex
import subprocess
from typing import List, Sequence

from ray.autoscaler.sdk import get_docker_host_mount_location

from anyscale.cli_logger import BlockLogger
from anyscale.cluster_config import get_cluster_config
from anyscale.controllers.base_controller import BaseController
from anyscale.project import get_project_session, load_project_or_throw
from anyscale.shared_anyscale_utils.util import get_container_name
from anyscale.util import get_working_dir


class WorkspaceController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log

        self.project_definition = load_project_or_throw()
        self.project_id = self.project_definition.config["project_id"]
        self.session = get_project_session(self.project_id, None, self.api_client)
        # FIXME: The get_cluster_config call repeats several of the REST calls
        # of the above calls -- the CLI can be made faster if we can dedup them.
        self.cluster_config = get_cluster_config(None, self.api_client)
        self.head_ip = self.api_client.get_session_head_ip_api_v2_sessions_session_id_head_ip_get(
            self.session.id
        ).result.head_ip

    def run_cmd(self, ssh_option: Sequence[str], cmd: str):
        ssh_user = self.cluster_config["auth"]["ssh_user"]
        key_path = self.cluster_config["auth"]["ssh_private_key"]
        container_name = get_container_name(self.cluster_config)

        command = shlex.quote(cmd)
        ssh_command = (
            ["ssh"]
            + list(ssh_option)
            + ["-tt", "-i", key_path]
            + ["{}@{}".format(ssh_user, self.head_ip)]
            + [f"docker exec -it {container_name} sh -c {command}"]
        )

        subprocess.run(ssh_command)  # noqa: B1

    def run_rsync(
        self,
        ssh_option: Sequence[str],
        local_path: str,
        *,
        down: bool,
        rsync_filters: List[str],
        rsync_excludes: List[str],
    ) -> None:
        ssh_user = self.cluster_config["auth"]["ssh_user"]
        key_path = self.cluster_config["auth"]["ssh_private_key"]

        base_ssh_command = ["ssh"] + ["-i", key_path] + list(ssh_option)

        directory_name = get_working_dir(
            self.cluster_config, self.project_id, self.api_client
        )

        source_directory = (
            get_docker_host_mount_location(self.cluster_config["cluster_name"])
            + directory_name
            + "/"
        )

        rsync_command = [
            "rsync",
            "--rsh",
            subprocess.list2cmdline(base_ssh_command),
            "-avz",
            "--delete",
        ]

        for rsync_exclude in rsync_excludes:
            rsync_command.extend(["--exclude", rsync_exclude])

        for rsync_filter in rsync_filters:
            rsync_command.extend(["--filter", "dir-merge,- {}".format(rsync_filter)])

        if down:
            rsync_command += [
                "{}@{}:{}".format(ssh_user, self.head_ip, source_directory),
                local_path,
            ]
        else:
            rsync_command += [
                local_path,
                "{}@{}:{}".format(ssh_user, self.head_ip, source_directory),
            ]

        subprocess.run(rsync_command)  # noqa: B1
