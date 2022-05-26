import base64
import json
import logging
import os

import coloredlogs
import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko
from halo import halo

from elbo.api import ElboRestApi
from elbo.resources import ElboResources
from elbo.ui import prompt_user
from elbo.utils.file_utils import get_temp_file_path, create_tar_gz_archive, read_config
from elbo.utils.misc_utils import say_hello
from elbo.utils.net_utils import wait_for_ssh_ready, upload_file

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


def request_task_run(elbo_connector, bucket_key, file_hash, task_config, session_id):
    """
    Request the receiver to run the task.

    :param elbo_connector: The elbo connector
    :param bucket_key: The bucket key - The file path in the Bucket
    :param file_hash: The file hash. The receiver will check if the file hash on the Bucket is the same as specified
    :param task_config: The task config provided by the user in the YAML file
    :param session_id: The session id here.
    :return: None
    """
    params = {
        "session_id": session_id,
        "bucket_key": bucket_key,
        "file_hash": file_hash,
        "task_config": base64.b64encode(bytes(json.dumps(task_config), "utf-8")),
    }

    response = elbo_connector.request(ElboResources.SCHEDULE_ENDPOINT, params=params)
    return response


def run_internal(elbo_connector, config):
    if not os.path.exists(config):
        logger.error(f"is unable to find '{config}', is the path correct?")
        exit(-1)

    task_config = read_config(config)
    if task_config is None:
        exit(-2)

    if "name" in task_config:
        logger.info(f"is starting '{task_config['name']}' submission ...")
    else:
        logger.error(f"please specify a task `name` in {config} file.")
        exit(-3)

    # Archive files
    temp_file_name = get_temp_file_path(tgz=True)
    # Get directory path relative to config file
    config_directory = os.path.dirname(config)
    task_dir = os.path.join(config_directory, task_config["task_dir"])
    create_tar_gz_archive(temp_file_name, task_dir)
    logger.info(f"is uploading sources from {task_dir}...")
    file_size = os.path.getsize(temp_file_name)
    if file_size > ElboResources.LARGE_FILE_SIZE:
        logger.error(f"the code artifacts are too large - {file_size} bytes...")
        logger.error(f"please consider excluding unnecessary files from sources..")
        exit(-4)

    url_response = elbo_connector.get_upload_url(file_size=file_size)
    if url_response is None:
        logger.error(f"is unable to authenticate with server..")
        exit(-6)
    (
        upload_url,
        user_id,
        authorization_token,
        session_id,
        show_low_balance_alert,
        user_first_name,
    ) = url_response
    if user_first_name:
        say_hello(user_first_name)

    if show_low_balance_alert:
        #
        # Allow user to continue scheduling. The job will complete even if balance is low
        #
        logger.warning(
            f"The balance on your account is too low, please deposit funds 🙏"
        )

    ip = None
    password = None
    if (
        upload_url is not None
        and user_id is not None
        and authorization_token is not None
    ):
        file_name = os.path.basename(temp_file_name)
        bucket_key = os.path.join(
            ElboResources.TASK_SUBMISSION_PREFIX, user_id, file_name
        )
        bucket_key, file_hash, task_id = upload_file(
            temp_file_name, upload_url, user_id, authorization_token, bucket_key=bucket_key,
            bucket_key_for_display=bucket_key
        )
        api = ElboRestApi()
        if bucket_key is not None and file_hash is not None:
            spinner = halo.Halo(
                text="elbo.client is finding compute options (this may take a while)",
                spinner="bouncingBall",
                placement="left",
            )
            print("")
            spinner.start()
            response = request_task_run(
                elbo_connector, bucket_key, file_hash, task_config, session_id
            )
            spinner.stop()
            if response is not None:
                chosen_type = prompt_user(response)
                spinner = halo.Halo(
                    text="elbo.client is provisioning compute (usually takes ~ 4 minutes, ☕️ time!)",
                    spinner="bouncingBall",
                    placement="left",
                )
                spinner.start()
                response_json = api.provision_compute(
                    chosen_type, session_id, task_config, config
                )
                spinner.stop()
                if response_json is not None:
                    ip, password = process_compute_provisioned_response(
                        response_json, ssh_only=False
                    )
                    client = paramiko.SSHClient()
                    wait_for_ssh_ready(client, ip, password)
                else:
                    logger.error(
                        f"something went wrong with provisioning, please try again ..."
                    )
            else:
                logger.error(f"is unable to get compute options from ELBO servers")
        else:
            logger.info(
                f":(. something went wrong with upload, please send us a bug report at bugs@elbo.ai"
            )

    else:
        if user_id is None:
            logger.error(f"is unable to verify your membership.")
            logger.error(
                "please obtain your token from https://elbo.ai/welcome, and run `elbo login`"
            )
        else:
            logger.info(
                f"is unable to obtain upload url. Please report this to bugs@elbo.ai."
            )

    return ip, password


# noinspection HttpUrlsUsage
def process_compute_provisioned_response(response_json, ssh_only=False):
    """
    Process the response from the server for provisioned compute
    :param ssh_only: Is this task SSH only?
    :param response_json: The response json
    :return: None
    """
    response = response_json
    server_ip = response["ip"]
    task_id = response["task_id"]
    password = response["password"]

    logger.info(f"compute node ip {server_ip}")
    #
    # TODO: Could we route the traffic through CloudFare so we get https endpoint?
    # One problem may be the use of port 2222 for SSH which will not work if we proxy through CloudFare
    #
    if not ssh_only:
        logger.info(f"task with ID {task_id} is submitted successfully.")
        logger.info("----------------------------------------------")
        logger.info(f"ssh using - ssh root@{response['ip']} -p 2222")
        logger.info(f"scp using - scp root@{response['ip']} -p 2222")
        logger.info(f"password: {password}")
        logger.info("----------------------------------------------")
        print("")
        logger.info(f"here are URLS for task logs ...")
        logger.info(f"setup logs        - http://{server_ip}/setup")
        logger.info(f"requirements logs - http://{server_ip}/requirements")
        logger.info(f"task logs         - http://{server_ip}/task")
        print("")
        logger.info(f"TIP: 💡 see task details with command: `elbo show {task_id}`")
        print("")
        logger.info(f"⏳ It may take a minute or two for the node to be reachable.")
    else:
        logger.info("----------------------------------------------")
        logger.info(f"ssh using - ssh root@{response['ip']} -p 2222")
        logger.info(f"scp using - scp root@{response['ip']} -p 2222")
        logger.info(f"password: {password}")
        logger.info("----------------------------------------------")
        print("")
        logger.info(
            f"TIP: 💡 copy your SSH public key to the server for password less login using:"
        )
        logger.info(f"ssh-copy-id -p 2222 root@{response['ip']}")
        print("")
        logger.info(f"TIP: 💡 cancel task using command: `elbo kill {task_id}`")
        print("")
        logger.info(f"⏳ It may take a minute or two for the node to be reachable.")

    return server_ip, password
