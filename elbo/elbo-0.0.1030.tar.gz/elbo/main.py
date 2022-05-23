import atexit
import logging
import os
import os.path
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path
from traceback import format_exception

import click
import coloredlogs
import halo
import pandas as pd
import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko
import questionary
import tabulate
from git import Repo
from tinynetrc import Netrc

from elbo.actions.run import run_internal, process_compute_provisioned_response
from elbo.connector import ElboConnector
from elbo.api import ElboRestApi
from elbo.resources import ElboResources
from elbo.utils.date_utils import transform_date, format_time, format_date
from elbo.utils.file_utils import get_temp_file_path, create_tar_gz_archive
from elbo.utils.misc_utils import say_hello, exit_handler
from elbo.utils.net_utils import wait_for_ssh_ready, download_task_artifacts
from elbo.ui import prompt_user
from elbo.actions.cp import cp_from_elbo, cp_to_elbo

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


@click.group()
def cli():
    """elbo.ai - Train more, pay less"""
    pass


def internal_login(token):
    """
    Login the user with the given token
    """
    net_rc_file = os.path.join(os.path.expanduser("~"), ".netrc")
    if not os.path.exists(net_rc_file):
        # Create file if it doesn't exist
        logger.info(f"Creating {net_rc_file}")
        Path(net_rc_file).touch()
    netrc = Netrc()
    host_name = ElboConnector.get_elbo_host()
    netrc[host_name]["password"] = token
    netrc.save()

    logger.info(f"ELBO token saved to ~/.netrc")


@cli.command(name="login")
@click.option(
    "--token",
    prompt="Please enter or paste your token from https://elbo.ai/welcome",
    hide_input=True,
)
def login(token):
    """
    Login to the ELBO service.
    """
    internal_login(token)


@cli.command(name="status")
def status():
    """
    Get ELBO server status.
    """
    member_status = "❌"
    db_status = "❌"
    server_status = "❌"

    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.STATUS_ENDPOINT)
    if response is not None:
        db_status = "✅" if response.get("db") is True else db_status
        member_status = "✅" if response.get("membership") is True else db_status
        server_status = "✅" if response.get("server") is True else db_status

    logger.info(f"Membership: {member_status}")
    logger.info(f"Database  : {db_status}")
    logger.info(f"Server    : {server_status}")


@cli.command(name="ps")
@click.option("-r", "--running", help="Show only running tasks", flag_value="Running")
@click.option(
    "-c", "--completed", help="Show only completed tasks", flag_value="Completed"
)
def ps(running, completed):
    """
    List of all your tasks.
    """
    if running:
        logger.info(f"looking up running tasks ...")
    else:
        logger.info(f"looking up your tasks ...")

    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.TASKS_ENDPOINT)
    if response is None:
        logger.error(f"is unable to get tasks list")
        return

    tasks_list = response["records"]
    if len(tasks_list) == 0:
        logger.info(
            f"no tasks found, how about starting an instance with `elbo create` ?"
        )
        return

    df = pd.DataFrame(tasks_list)
    df = df.fillna("")
    if "Artifacts URL" in df:
        del df["Artifacts URL"]
    if "Logs URL" in df:
        del df["Logs URL"]
    if "SSH" in df:
        del df["SSH"]
    if "Source URL" in df:
        del df["Source URL"]
    if "last" in df:
        del df["last"]

    time_columns = [
        "Run Time",
        "Start Time",
        "Submission Time",
        "Completion Time",
        "Billed Upto Time",
        "Created Time",
    ]

    for column in time_columns:
        if column in df.columns:
            # Format time to local time zone
            df[column] = df[column].apply(transform_date())

    df = df.sort_values(by=["Task ID"])
    df = df.set_index("Task ID")
    if running == "Running":
        df = df.loc[df["Status"] == running]
    elif completed == "Completed":
        df = df.loc[df["Status"] == completed]
    if len(df) == 0:
        logger.info(f"no running tasks...")
    else:
        print(tabulate.tabulate(df, headers="keys", tablefmt="pretty"))

    if len(df) > 0:
        print("")
        print("")
        print(f"Related task commands: \n")
        print("\telbo show [task_id]")
        print("\telbo kill [task_id]")
        print("\telbo ssh [task_id]")
        print("\telbo download [task_id]\n")


@cli.command(name="kill")
@click.argument("task_id")
def cancel(task_id):
    """
    Stop the task.
    """
    logger.info(f"Stopping task - {task_id}")
    params = {"task_id": task_id}
    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.CANCEL_ENDPOINT, params=params)
    if response is not None:
        logger.info(f"Task with id = {task_id} is marked for cancellation.")


@cli.command(name="show")
@click.argument("task_id")
def show(task_id):
    """
    Show the task.
    """
    logger.info(f"Fetching task - {task_id}")
    params = {"task_id": task_id}
    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.SHOW_ENDPOINT, params=params)
    if response is not None:
        logger.info(f"Task with id = {task_id}:")
        record = response["records"]
        is_running = record["Status"].lower() == "running"
        for k, v in response["records"].items():
            # TODO: Present these fields in a better way
            if "Authorization" in k:
                continue
            if k == "SSH":
                if not is_running:
                    continue
            if "Run Time" in k:
                v = format_time(v)
            elif "Time" in k:
                v = format_date(v)
            if "URL" not in k and k != "last":
                print(f"{k:<24}: {v}")


@cli.command(name="balance")
def balance():
    """
    Check your account balance.
    """
    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.BALANCE_ENDPOINT, params={})
    if response is not None:
        account_balance = response["Balance"]
        deposit_url = response["URL"]
        logger.info(
            f"Your account balance is ${account_balance}. Deposit funds using {deposit_url}."
        )


@cli.command(name="rm")
@click.argument("file_path")
def rm(file_path):
    """
    Permanently delete the file in elbo storage. This operation cannot be reverted.
    """
    if file_path.startswith('/') or file_path.startswith('.'):
        logger.error(f"invalid path - {file_path}")
        return

    if not file_path.startswith("elbo://"):
        file_path = f"elbo://{file_path}"

    confirmed_remove = questionary.confirm(
        f"🛑 The file cannot be recovered after deletion. Are you sure you want to delete {file_path}?",
        qmark="elbo.client").ask()
    if confirmed_remove:
        logger.info(f"deleting {file_path}")
    params = {"file_or_dir_path": file_path}
    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.REMOVE_ENDPOINT, params=params)
    if response is not None and response is True:
        logger.info(f"file deleted.")
    elif response is False:
        logger.warning(f"file not found, please check the path - {file_path}")
        logger.info(f"TIP: Use `elbo ls` to see your files.")
    else:
        logger.error(f"something went wrong, please try again. Response - {response}")


@cli.command(name="download")
@click.argument("task_id")
def download(task_id):
    """
    Download the artifacts for the task.
    """
    logger.info(f"downloading artifacts for task - {task_id}")
    params = {"task_id": task_id}

    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.RESOURCE_ENDPOINT, params=params)
    if response is None:
        logger.info(f"Could not retrieve artifact download URL for {task_id}")
        return

    artifact_auth = response["client_artifact_auth"]
    artifact_url = urllib.parse.unquote(response["client_url"])
    temp_dir = tempfile.mkdtemp()
    local_dir_name = download_task_artifacts(
        artifact_url, temp_dir, artifact_auth, None
    )
    if local_dir_name is not None and os.path.exists(local_dir_name):
        logger.info(f"artifacts downloaded to temporary directory: {local_dir_name}")


@cli.command(name="ssh")
@click.argument("task_id")
def ssh_task(task_id):
    """
    SSH into the machine running the task.
    """
    logger.info(f"Trying to SSH into task - {task_id}...")
    params = {"task_id": task_id}

    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.SHOW_ENDPOINT, params=params)

    if response is not None and response["records"] is not None:
        ssh_command = response["records"]["SSH"]
        password = response["records"]["Password"]
        logger.info(f"Running Command : {ssh_command}")
        logger.info(f"Enter this password when prompted: {password}")
        os.system(ssh_command)
    else:
        logger.warning(
            f"SSH information not found for task - {task_id}, is it still running?"
        )


@cli.command(name="cp")
@click.argument("file_path")
@click.argument("destination_dir")
def cp(file_path, destination_dir):
    """
    Copy the file at the given path to your ELBO storage. If the give file path is a
    directory, then all files in this directory will be copied recursively.
    """
    elbo_connector = ElboConnector()
    if file_path.startswith("elbo://"):
        # Download files
        cp_from_elbo(elbo_connector, file_path, destination_dir)
    else:
        cp_to_elbo(elbo_connector, file_path, destination_dir)


@cli.command(name="ls")
@click.option("--path", "-p", default="/")
def ls(path):
    """
    List files in your elbo storage.
    """
    if path.startswith("elbo://"):
        path = path.replace("elbo://", "")

    params = {"object_name": path}

    elbo_connector = ElboConnector()
    response = elbo_connector.request(ElboResources.OBJECT_INFO, params=params)
    if response is None:
        logger.warning(f"no information found for {path}")
    else:
        path_info = response
        index = list(range(1, len(path_info) + 1))
        df = pd.DataFrame(path_info, index=index)
        time_columns = ["mod_time_millis", "upload_time"]
        for column in time_columns:
            if column in df.columns:
                # Format time to local time zone
                df[column] = df[column].apply(transform_date())
        if "folder" in df.columns:
            del df["folder"]
        df.columns = [
            "Encryption",
            "Name",
            "Modification Time",
            "Size (bytes)",
            "Upload Time",
        ]
        print(
            tabulate.tabulate(
                df, headers="keys", tablefmt="pretty", stralign="left", numalign="right"
            )
        )


@cli.command(name="create")
@click.option(
    "--open-port",
    "-p",
    type=int,
    multiple=True,
    help="The port that should be opened on the instance.",
)
@click.option(
    "--copy-dir",
    "-c",
    type=str,
    help="The directory to copy to the remote machine"
)
def create(open_port, copy_dir):
    """
    Create an instance and get SSH access to it.
    """
    if copy_dir is not None and len(copy_dir) > 0:
        if not os.path.exists(copy_dir):
            logger.error(f"unable to find {copy_dir}, please check the path...")
            return

    if len(open_port) > 0:
        logger.info(f"creating instance with open port(s) - {open_port}")
    else:
        logger.info(f"creating instance ...")

    sources_path = None
    if copy_dir is not None:
        logger.info(f"zipping {copy_dir} for transfer ...")
        temp_file_name = get_temp_file_path(tgz=True)
        create_tar_gz_archive(temp_file_name, copy_dir)
        destination_dir = "sources"
        sources_path = f"{destination_dir}/{os.path.basename(temp_file_name)}"
        logger.info(f"is copying sources from {copy_dir} to elbo://{sources_path} ...")
        elbo_connector = ElboConnector()
        cp_to_elbo(elbo_connector, temp_file_name, destination_dir)

    spinner = halo.Halo(
        text="elbo.client is finding compute options (this may take a while)",
        spinner="bouncingBall",
        placement="left",
    )
    print("")
    spinner.start()
    elbo_api = ElboRestApi()
    response = elbo_api.request_machine_create()
    if not response:
        logger.error(f"Unable to get compute type options")
        return

    options = response["results"]
    session_id = response["session_id"]
    user_first_name = response["user_first_name"]
    spinner.stop()
    say_hello(user_first_name)
    ip = None
    password = None
    if options is not None:
        chosen_type = prompt_user(options)
        spinner = halo.Halo(
            text="elbo.client is provisioning compute (usually takes ~ 4 minutes, ☕️ time!)",
            spinner="bouncingBall",
            placement="left",
        )
        spinner.start()
        response_json = elbo_api.provision_machine_create_compute(
            chosen_type, session_id, open_ports=list(open_port),
            sources_path=sources_path
        )
        spinner.stop()
        if response_json is not None:
            ip, password = process_compute_provisioned_response(
                response_json, ssh_only=True
            )
            client = paramiko.SSHClient()
            wait_for_ssh_ready(client, ip, password)
        else:
            logger.error(
                f"something went wrong with provisioning, please try again ..."
            )
    else:
        logger.error(f"is unable to get compute options from ELBO servers")

    return ip, password


@cli.command(name="notebook")
def notebook():
    """
    Start a Jupyter Lab session.
    """
    note_book_git_url = "https://github.com/elbo-ai/elbo-examples"
    notebook_token_command = (
        "/opt/conda/bin/jupyter-lab list | grep token | cut -d'=' -f2 | cut -d' ' -f1"
    )
    logger.info(f"creating notebook using config at project {note_book_git_url} ...")
    temp_dir = tempfile.mkdtemp()
    logger.info(f"cloning {note_book_git_url} to {temp_dir} ...")
    Repo.clone_from(note_book_git_url, temp_dir)
    config_file_path = os.path.join(temp_dir, "notebook/elbo.yaml")
    logger.info(f"Submitting notebook run config : {config_file_path}")
    elbo_connector = ElboConnector()
    ip, password = run_internal(elbo_connector, config_file_path)
    client = paramiko.SSHClient()
    wait_for_ssh_ready(client, ip, password)

    counter = 0
    token = None
    logger.info(f"node started ..")
    spinner = halo.Halo(
        text="elbo.client is waiting for jupyter notebook to start ...",
        spinner="bouncingBall",
        placement="left",
    )
    print("")
    spinner.start()
    while True:
        if counter > 30:
            # 5 minutes
            spinner.stop()
            break
        stdin, stdout, stderr = client.exec_command(notebook_token_command)
        output = stdout.readlines()
        if len(output) > 0:
            token = output[0].rstrip()
            spinner.stop()
            logger.info(f"Notebook URL = http://{ip}:8080/?token={token}")
            break
        counter = counter + 1
        time.sleep(10)

    if token is None:
        logger.warning(
            f"sorry, unable to find token, please SSH into {ip} port 2222 with password {password}."
        )
        logger.warning(f"and run command -> {notebook_token_command}")


@cli.command(name="run")
@click.option(
    "--config",
    type=click.Path(),
    default="elbo.yaml",
    help="The path of the ELBO yaml configuration file",
)
def run(config):
    """
    Submit a task specified by the config file.
    """
    elbo_connector = ElboConnector()
    run_internal(elbo_connector, config)


atexit.register(exit_handler)


def elbo_except_hook(exception_type, value, traceback):
    report = "".join(format_exception(exception_type, value, traceback, 50))
    print(report)
    params = {"exception_report": str(report)}
    elbo_connector = ElboConnector()
    _ = elbo_connector.request(
        ElboResources.EXCEPTION_REPORT_ENDPOINT, params=params, method="POST"
    )
    sys.__excepthook__(exception_type, value, traceback)


# noinspection SpellCheckingInspection
sys.excepthook = elbo_except_hook

if __name__ == "__main__":
    cli()
