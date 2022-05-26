import json
import logging
import os
from http import HTTPStatus

import coloredlogs
import requests
from tinynetrc import Netrc

from elbo.resources import ElboResources

# noinspection PyMethodMayBeStatic

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


class ElboConnector:
    # TODO: Add back SSL in Cloud fare after fixing HTTP error 524 -- Long polling
    # noinspection HttpUrlsUsage
    ELBO_HOST = "http://prod.elbo.ai"
    # noinspection HttpUrlsUsage
    ELBO_STAGING_HOST = "http://carry.elbo.ai"
    ELBO_TEST_HOST = "http://localhost:5007"

    def __init__(self):
        self._host_name = ElboConnector.get_elbo_host()

    @staticmethod
    def get_elbo_host():
        if os.getenv("ELBO_TEST_MODE") is not None:
            return ElboConnector.ELBO_TEST_HOST
        elif os.getenv("ELBO_STAGING_MODE") is not None:
            return ElboConnector.ELBO_STAGING_HOST
        else:
            return ElboConnector.ELBO_HOST

    def get_auth_token(self):
        """
        Get the ELBO service authentication tokens using NETRC
        :return: The auth tokens
        """
        netrc = None
        try:
            netrc = Netrc()
        except FileNotFoundError as _:
            logger.error(
                f"could not find ~/.netrc file where auth tokens are stored. "
                f"Please run `elbo login` again."
            )
            exit(-1)
        host_name = self._host_name
        tokens = netrc.get(host_name)
        if tokens["password"] is None:
            logger.error(f"please login to elbo service by running `elbo login`")
            exit(0)
        else:
            return tokens["password"]

    def request(self, end_point, params=None, host=None, method="GET"):
        """
        Call the rest API get
        """
        if not host:
            host = self._host_name
        url = host + "/" + end_point
        token = self.get_auth_token()
        headers = {
            # Flask does not like `_` in header keys
            "TOKEN": token
        }

        try:
            # Keep a high timeout
            if method == "GET":
                response = requests.get(
                    url, headers=headers, params=params, timeout=10 * 60
                )
            elif method == "POST":
                response = requests.post(
                    url, headers=headers, data=params, timeout=10 * 60
                )
            else:
                logger.error(f"{method} not found for submission of request")
                response = None
                exit(-1)

        except requests.exceptions.ConnectionError as _:
            logger.error(f"unable to connect to ELBO Server, please try again...")
            return None
        except requests.exceptions.ReadTimeout as _:
            logger.error(
                f"timed out while trying to connect to the node. "
                f"Usually the node starts execution, please"
                f" check status using `elbo show`"
            )
            return None

        if response.ok:
            response_json = response.text
            response_code = response.status_code
            if response_code == HTTPStatus.NOT_MODIFIED:
                logger.warning(f"task already cancelled or completed.")
                exit(0)
            response = json.loads(response_json)
        else:
            if response.status_code == HTTPStatus.PAYMENT_REQUIRED:
                logger.error(f"🚨 {response.text}")
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                logger.error(
                    f"🚨 we are not able to authorize you, could you try `elbo login` again?"
                )
                exit(-1)
            elif response.status_code == HTTPStatus.NOT_FOUND:
                logger.error(f"🚨 got resource not found error")
            elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                print("")
                logger.error(f"🚨 we hit a glitch --> {response.text}")
                logger.error(f"Please email contact@elbo.ai")
            else:
                logger.error(
                    f"received unknown error code - "
                    f"{response.status_code} with message - {response.text}"
                )
            response = None

        return response

    def get_upload_url(
        self, file_size, destination_file_path=None, is_training_task=True
    ):
        """
        Get the upload URL for the token
        """
        if not is_training_task:
            is_file_upload_request = 1
        else:
            is_file_upload_request = 0

        if file_size > ElboResources.LARGE_FILE_SIZE:
            # Anything greater than 1G is large file upload
            is_large_file_upload = 1
        else:
            is_large_file_upload = 0

        params = {
            "file_upload": is_file_upload_request,
            "large_file": is_large_file_upload,
        }

        if destination_file_path is not None:
            params["file_name"] = destination_file_path

        if is_training_task:
            response = self.request(ElboResources.UPLOAD_URL_ENDPOINT, params=params)
        else:
            response = self.request(ElboResources.FILE_RECEIVER, params=params)

        if response is None:
            return None

        upload_url = response.get("uploadUrl")
        user_id = response.get("user_id")
        authorization_token = response.get("authorizationToken")
        session_id = response.get("session_id")
        show_low_balance_alert = response.get("add_low_balance_alert")
        user_first_name = response.get("user_first_name")
        return (
            upload_url,
            user_id,
            authorization_token,
            session_id,
            show_low_balance_alert,
            user_first_name,
        )
