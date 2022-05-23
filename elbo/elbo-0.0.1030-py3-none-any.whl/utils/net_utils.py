import hashlib
import logging
import os
import time
import warnings
from http import HTTPStatus

import paramiko
import questionary
import requests
from cryptography.utils import CryptographyDeprecationWarning
from halo import halo
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    from paramiko.ssh_exception import (
        BadHostKeyException,
        AuthenticationException,
        SSHException,
    )
from tqdm import tqdm

import coloredlogs
from tqdm.utils import CallbackIOWrapper

from elbo.resources import ElboResources
from elbo.utils.file_utils import extract_file
from elbo.utils.misc_utils import get_task_id_from_file_name

logger = logging.getLogger("elbo.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


def wait_for_ssh_ready(client, ip, password):
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    spinner = halo.Halo(
        text="elbo.client is waiting for node to be ready ...",
        spinner="bouncingBall",
        placement="left",
    )
    print("")
    spinner.start()
    while True:
        try:
            client.connect(hostname=ip, username="root", port=2222, password=password)
            spinner.stop()
            break
        except BadHostKeyException as _:
            time.sleep(4)
        except AuthenticationException as _:
            time.sleep(2)
        except SSHException as _:
            time.sleep(4)
        except paramiko.ssh_exception.NoValidConnectionsError as _:
            time.sleep(4)


def download_file(download_url, download_directory, authorization=None, file_name=None):
    """
    TODO: This is copied over from common/utils in elbo-server Repo. Need to expose this in a common
    package

    Download the file at URL to the download directory. This stores the file in memory and writes to file system.
    This can be used for really large files which may not fit in memory.

    :param file_name:
    :param authorization: The download authorization token
    :param download_url: The download URL
    :param download_directory: The download directory
    :return: Path to file if download is successful, None otherwise
    """
    if not download_url:
        logger.error(f"No download URL")
        return

    if file_name is None:
        file_name = download_url.split("/")[-1]
        if file_name is None:
            logger.error(f"Could not infer filename from {download_url}")
            return None
    local_filename = os.path.join(download_directory, file_name)
    headers = {}
    if authorization is not None:
        headers = {"Authorization": authorization}

    try:
        with requests.get(download_url, stream=True, headers=headers) as r:
            r.raise_for_status()
            total_size_in_bytes = int(r.headers.get("content-length", 0))
            chunk_size = 8192
            progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            progress_bar.close()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            logger.warning(f"{download_url} file does not exists.")
            logger.warning(f"Perhaps the task is not complete yet?")
        else:
            logger.error(f"Unable to request {download_url} exception - {e}")
        return None

    if os.path.exists(local_filename):
        return local_filename
    else:
        return None


# TODO: Enable once we get this working
# @cli.command(name='logs')
# @click.option('--task_id',
#              required=True,
#              hide_input=False)
def logs(elbo_connector, task_id):
    """
    Show logs from the task.
    """
    # TODO:
    logger.info(f"Getting logs of - {task_id}...")
    params = {"task_id": task_id}
    response = elbo_connector.request(ElboResources.LOGS_ENDPOINT, params=params)
    if response is not None:
        logger.info(response)


def get_real_time_logs(server_ip):
    # noinspection HttpUrlsUsage
    log_address = f"http://{server_ip}/stream"
    connection_errors = 0
    while True:
        try:
            request = requests.get(log_address, stream=True)
            if request.encoding is None:
                request.encoding = "utf-8"

            for line in request.iter_lines(decode_unicode=True):
                if line and line != "0":
                    logger.info(f"{server_ip}> {line}")
            time.sleep(2)
        except requests.exceptions.ConnectionError as _:
            # Connection errors can happen when SSH is trying to get established
            print(".", end="")
            time.sleep(5)
            connection_errors = connection_errors + 1
            if connection_errors > 10:
                print("*")
                break
            pass
        except Exception as _e:
            logger.error(f"Hit {_e}")
            break


def download_task_artifacts(
    artifact_url, output_directory, artifact_auth, artifact_file
):
    local_file_name = download_file(
        artifact_url, output_directory, artifact_auth, artifact_file
    )
    if local_file_name is None:
        return None

    extracted_dir = extract_file(local_file_name)

    # Check if WandB directory exists, if it does, try to sync WandB
    workspace_dir = os.path.join(extracted_dir, ElboResources.WORKSPACE_DIRECTORY)
    files = os.listdir(workspace_dir)
    if ElboResources.WANDB_DIRECTORY in files:
        sync_wandb = questionary.confirm(
            "detected weights and biases offline data, "
            "do you want to sync them to wandb.ai?",
            qmark="elbo.client",
        ).ask()
        if sync_wandb:
            try:
                current_dir = os.getcwd()
                os.chdir(extracted_dir)
                fix_symlinks_command = (
                    f'find {extracted_dir}  -lname "*" -exec sh -c \'ln -snf '
                    f'"{extracted_dir}/$(readlink "$1")" "$1"\' sh ' + "\\{\\} \\;"
                )
                os.system(fix_symlinks_command)
                wandb_offline_dir = os.path.join(workspace_dir, "wandb/offline-run-*")
                wandb_command = f"wandb sync --include-offline {wandb_offline_dir}"
                os.system(wandb_command)
                os.chdir(current_dir)
            except Exception as _e:
                logger.error(f"unable to sync wandb -- {_e}")

    return extracted_dir


def upload_post_with_retry(file_path, file_size, upload_url, headers):
    """
    Post the upload with retry and status update
    :param file_path: The file path
    :param file_size: The file size
    :param upload_url: The upload URL
    :param headers: The headers
    :return:
    """
    with open(file_path, "rb") as f:
        with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
            wrapped_file = CallbackIOWrapper(t.update, f, "read")
            count = 0
            while True:
                try:
                    if count == 5:
                        logger.error(f"too many connection errors...")
                        break
                    upload_response = requests.post(
                        upload_url, headers=headers, data=wrapped_file
                    )
                    return upload_response
                except requests.exceptions.ConnectionError as _:
                    # This can happen if we are uploading large files, wait for some time...
                    count = count + 1
                    logger.warning(f"Connection error, retrying ...")
                    time.sleep(10)

    return None


def upload_file(file_path, upload_url, user_id, authorization_token, bucket_key=None,
                bucket_key_for_display=None):
    """
    Upload a file to the URL specified
    :param file_path: The file to upload
    :param upload_url: The upload URL
    :param user_id: The user id
    :param authorization_token: The auth token
    :param bucket_key: The user bucket key
    :param bucket_key_for_display: The bucket key that we should show to user
    :return: The bucket key and the SHA256 hash of the uploaded file
    """
    content_type = "application/tar+gzip"
    file_name = os.path.basename(file_path)
    file_size = os.stat(file_path).st_size
    upload_response = None
    file_hash = None
    if file_size > ElboResources.LARGE_FILE_SIZE:
        # Large file, use part upload
        size_of_part = ElboResources.LARGE_FILE_UPLOAD_CHUNK_SIZE
        total_bytes_sent = 0

        part_no = 1
        pbar = tqdm(total=file_size, unit="B", unit_scale=True)
        while total_bytes_sent < file_size:
            if (
                file_size - total_bytes_sent
            ) < ElboResources.LARGE_FILE_UPLOAD_CHUNK_SIZE:
                size_of_part = file_size - total_bytes_sent

            with open(file_path, "rb") as fd:
                fd.seek(total_bytes_sent)
                file_data = fd.read(size_of_part)

            part_hash = hashlib.sha1(file_data).hexdigest()
            headers = {
                "Authorization": authorization_token,
                "X-Bz-File-Name": bucket_key,
                "Content-Type": content_type,
                "X-Bz-Part-Number": str(part_no),
                "Content-Length": str(size_of_part),
                "X-Bz-Content-Sha1": part_hash,
            }

            upload_response = requests.post(upload_url, headers=headers, data=file_data)
            if upload_response.status_code != 200:
                break
            total_bytes_sent = total_bytes_sent + size_of_part
            part_no += 1
            pbar.update(size_of_part)
        pbar.close()
    else:
        if bucket_key is None:
            bucket_key = os.path.join(user_id, file_name)

        with open(file_path, mode="rb") as fd:  # b is important -> binary
            file_contents = fd.read()

        file_hash = hashlib.sha1(file_contents).hexdigest()

        headers = {
            "Authorization": authorization_token,
            "X-Bz-File-Name": bucket_key,
            "Content-Type": content_type,
            "X-Bz-Content-Sha1": file_hash,
            "X-Bz-Info-Author": "None",
            "X-Bz-Server-Side-Encryption": "AES256",
        }

        upload_response = upload_post_with_retry(
            file_path, file_size, upload_url, headers
        )

    if upload_response is not None and upload_response.status_code == 200:
        task_id = get_task_id_from_file_name(file_name)
    else:
        logger.error(f"failed task upload - {upload_response}")
        return None

    if bucket_key_for_display is not None:
        logger.info(f"uploaded to elbo://{bucket_key_for_display}")
    else:
        logger.info(f"uploaded to elbo")

    return bucket_key, file_hash, task_id
