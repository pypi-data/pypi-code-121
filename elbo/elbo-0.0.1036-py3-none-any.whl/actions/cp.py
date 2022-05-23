import glob
import logging
import os
import urllib.parse

import coloredlogs

from elbo.connector import ElboConnector
from elbo.resources import ElboResources
from elbo.utils.misc_utils import remove_prefix
from elbo.utils.net_utils import upload_file, download_file

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


def cp_file_to_elbo(elbo_connector, filename, source_object, destination_dir):
    if not os.path.exists(filename):
        logger.error(f"{filename} does not exist, please check path.")
        exit(0)
    file_size = os.path.getsize(filename)

    destination_file_path = os.path.join(destination_dir, os.path.basename(filename))

    url_response = elbo_connector.get_upload_url(
        file_size, destination_file_path, is_training_task=False
    )
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
    if (
            upload_url is not None
            and user_id is not None
            and authorization_token is not None
    ):
        destination_dir = remove_prefix(destination_dir, "/")
        rel_path = os.path.relpath(filename, start=source_object)
        if rel_path == ".":
            bucket_key = os.path.join(
                user_id, destination_dir, os.path.basename(source_object)
            )
            bucket_key_for_display = os.path.join(
                destination_dir, os.path.basename(source_object)
            )
        else:
            bucket_key = os.path.join(
                user_id, destination_dir, os.path.basename(source_object), rel_path
            )
            bucket_key_for_display = os.path.join(
                destination_dir, os.path.basename(source_object), rel_path
            )

        if not bucket_key.startswith(user_id):
            logger.error(
                f"something is wrong with the destination {bucket_key}, "
                f"please email this bug report to hi@elbo.ai"
            )
            exit(0)

        logger.info(f"uploading {filename} -> elbo://{bucket_key_for_display} ...")
        _ = upload_file(
            filename, upload_url, user_id, authorization_token, bucket_key=bucket_key,
            bucket_key_for_display=bucket_key_for_display
        )


def cp_to_elbo(elbo_connector, file_path, destination_dir):
    """
    Copy the local file path to elbo storage
    :param elbo_connector: The elbo connector
    :param file_path: The local file path
    :param destination_dir: The elbo path
    :return:
    """
    if os.path.isabs(file_path):
        source_object = file_path
    else:
        source_object = os.path.join(os.getcwd(), file_path)

    if not os.path.exists(file_path):
        logger.error(f"Unable to find {file_path}, does it exist?")
        return 0

    if destination_dir == "." or destination_dir == "/":
        # User intends to copy to root
        destination_dir = ""

    if os.path.isdir(source_object):
        for filename in glob.iglob(
                os.path.join(source_object, "**/**"), recursive=True
        ):
            if os.path.isdir(filename):
                continue
            cp_file_to_elbo(elbo_connector, filename, source_object, destination_dir)
    else:
        cp_file_to_elbo(elbo_connector, file_path, source_object, destination_dir)


def cp_from_elbo(elbo_connector, file_path, destination_dir):
    """
    Copy the local file path to elbo storage
    :param elbo_connector: The elbo connector
    :param file_path: The remote elbo file path
    :param destination_dir: The local file path
    :return:
    """
    if os.path.exists(destination_dir) and not os.path.isdir(destination_dir):
        logger.error(f"{destination_dir} already exists, skipping ... ")

    os.makedirs(destination_dir, exist_ok=True)

    params = {"file_or_dir_path": file_path}

    response = elbo_connector.request(ElboResources.RESOURCE_ENDPOINT, params=params)
    if response is None:
        logger.info(f"Could not retrieve {file_path}")
        return

    artifact_auth = response["client_artifact_auth"]
    artifact_url = urllib.parse.unquote(response["client_url"])
    local_dir_name = download_file(
        artifact_url, destination_dir, artifact_auth, None
    )
    if local_dir_name is not None and os.path.exists(local_dir_name):
        logger.info(f"downloaded to: {local_dir_name}")


if __name__ == "__main__":
    _elbo_connector = ElboConnector()
    cp_from_elbo(_elbo_connector, "elbo://tox.ini", ".")
