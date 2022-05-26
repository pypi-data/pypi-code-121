import asyncio
from collections import defaultdict
import time
from typing import Dict, List

from anyscale.authenticate import get_auth_api_client
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.client.openapi_client.models.session_command_types import (
    SessionCommandTypes,
)
from anyscale.commands.session_commands_hidden import session_upload_command_logs_impl
from anyscale.webterminal.utils import Command


KILLED_STATUS_CODE = 130
MINUTE_IN_SECONDS = 60


class CommandPersister:
    """
        CommandPersister manages persisting the
        state of all commands to our backend.
        It functions as a queue.
    """

    def __init__(self, cli_token: str, host: str, session_id: str):
        self.api_client: DefaultApi = get_auth_api_client(
            cli_token=cli_token, host=host
        ).api_client
        self.cli_token = cli_token
        self.host = host
        self.session_id = session_id
        self.queue: List[Command] = []
        self.running_commands: Dict[str, Command] = {}
        self.last_uploaded_time: Dict[str, float] = defaultdict(float)
        self.is_active = True

    def shutdown(self) -> None:
        self.is_active = False

    async def persist_commands(self) -> None:
        while self.is_active:
            for session_command in self.running_commands.values():
                self.upload_command_log(session_command)
            if len(self.queue) == 0:
                await asyncio.sleep(1)
                continue
            cmd = self.queue.pop(0)
            try:
                if cmd.exec_command:
                    # Mark exec commands as running by default so that we do not try to create this command on the
                    # backend ( it is already created).
                    # When the exec command is finished, command_persister will treat it like other WT commands.
                    self.running_commands[cmd.scid] = cmd
                if cmd.scid not in self.running_commands:
                    self.api_client.create_session_command_api_v2_sessions_session_id_create_session_command_post(
                        session_id=self.session_id,
                        external_terminal_command={
                            "scid": cmd.scid,
                            "command": cmd.command,
                            "created_at": cmd.created_at,
                            "finished_at": cmd.finished_at,
                            "status_code": cmd.status_code,
                            "web_terminal_tab_id": cmd.term_name,
                            "type": SessionCommandTypes.WEBTERMINAL,
                        },
                    )
                    if not cmd.finished:
                        self.running_commands[cmd.scid] = cmd
                elif cmd.finished:
                    self.api_client.finish_session_command_api_v2_session_commands_session_command_id_finish_post(
                        session_command_id=cmd.scid,
                        session_command_finish_options={
                            "status_code": cmd.status_code,
                            "stop": False,
                            "terminate": False,
                            "finished_at": cmd.finished_at,
                            "killed_at": cmd.finished_at
                            if cmd.status_code == KILLED_STATUS_CODE
                            else None,
                        },
                    )
                    del self.running_commands[cmd.scid]
                self.upload_command_log(cmd)
                if cmd.finished:
                    del self.last_uploaded_time[cmd.scid]
            except Exception as e:
                with open(f"/tmp/{cmd.scid}.err", "a") as err_file:
                    err_file.write(f"{str(e)}\n")
            if len(self.queue) > 0:
                # If the queue is not empty continue faster through it.
                await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(1)

    def upload_command_log(self, session_command: Command) -> None:
        """
        We upload logs to S3 if any of the below conditions is true:
        1. Session command terminates
        2. Session command runs the first time
        3. The duration from the last uploaded time is larger than the specified period
        """
        current_time_in_s = time.time()
        if (
            session_command.finished
            or current_time_in_s - self.last_uploaded_time[session_command.scid]
            > MINUTE_IN_SECONDS * 2
        ):
            session_upload_command_logs_impl(
                command_id=session_command.scid,
                cli_token=self.cli_token,
                host=self.host,
            )
            # We store the timestamp in which logs have been successfully
            # uploaded to avoid re-uploading large logs that take some time
            # to upload.
            finish_upload_time_in_s = time.time()
            self.last_uploaded_time[session_command.scid] = finish_upload_time_in_s

    def enqueue_command(self, cmd: Command) -> None:
        """
            enqueue_command adds a Command object to be persisted to our backend.
            Only enqueue the command to be peristed if it is
                - just created (therefore not in self.running_commands)
                  we need to create the entry on the backend.
                - finished
                  we need to update the entry on the backend.
        """
        if cmd.scid not in self.running_commands or cmd.finished:
            self.queue.append(cmd)

    def kill_running_commands_for_terminal(self, term_name: str) -> None:
        """
            When we exit a terminal tab, the zsh process is killed and
            all of its children process are also killed. This function then
            enqueues them to be marked as finished.
        """
        commands = list(self.running_commands.values())
        for c in commands:
            if c.term_name == term_name:
                c.finish(KILLED_STATUS_CODE)
                self.enqueue_command(c)
