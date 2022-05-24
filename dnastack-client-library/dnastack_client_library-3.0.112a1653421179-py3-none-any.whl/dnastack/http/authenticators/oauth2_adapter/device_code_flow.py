from pprint import pformat
from typing import Dict, Any, List

from imagination import container
from requests import Session
from time import time, sleep

from dnastack.configuration.models import OAuth2Authentication
from dnastack.exceptions import LoginException
from dnastack.feature_flags import in_global_debug_mode
from dnastack.common.console import Console
from dnastack.common.environments import env
from dnastack.http.authenticators.oauth2_adapter.abstract import OAuth2Adapter


class DeviceCodeFlowAdapter(OAuth2Adapter):
    __grant_type = 'urn:ietf:params:oauth:grant-type:device_code'

    def __init__(self, auth_info: OAuth2Authentication):
        super(DeviceCodeFlowAdapter, self).__init__(auth_info)
        self.__console: Console = container.get(Console)

    @staticmethod
    def get_expected_auth_info_fields() -> List[str]:
        return [
            'client_id',
            # 'client_secret',
            'device_code_endpoint',
            'grant_type',
            'resource_url',
            'token_endpoint',
        ]

    def exchange_tokens(self) -> Dict[str, Any]:
        session = Session()

        auth_info = self._auth_info
        grant_type = auth_info.grant_type
        login_url = auth_info.device_code_endpoint
        resource_url = auth_info.resource_url
        client_id = auth_info.client_id

        if grant_type != self.__grant_type:
            raise LoginException(resource_url, f'Invalid Grant Type (expected: {self.__grant_type})')

        if not login_url:
            raise LoginException(resource_url, "There is no device code URL specified.")

        device_code_params = {
            "grant_type": self.__grant_type,
            "client_id": client_id,
            "resource": resource_url,
        }

        if auth_info.scope:
            device_code_params['scope'] = auth_info.scope

        device_code_res = session.post(login_url, params=device_code_params, allow_redirects=False)
        device_code_json = device_code_res.json()

        if in_global_debug_mode:
            self._logger.debug(f'Response from {login_url}:\n{pformat(device_code_json, indent=2)}')

        if device_code_res.ok:
            device_code = device_code_json["device_code"]
            device_verify_uri = device_code_json["verification_uri_complete"]
            poll_interval = int(device_code_json["interval"])
            expiry = time() + int(env('DEVICE_CODE_TTL', required=False) or device_code_json["expires_in"])

            user_code = device_code_json['user_code']

            # NOTE: This is disabled for now until the associated auth test is improved.
            # self.__console.print('\nUser code to verify:\n')
            # self.__console.print(f"  +----{'-' * len(user_code)}----+")
            # self.__console.print(f"  |    {' ' * len(user_code)}    |")
            # self.__console.print(f"  |    {user_code}    |")
            # self.__console.print(f"  |    {' ' * len(user_code)}    |")
            # self.__console.print(f"  +----{'-' * len(user_code)}----+")
            # self.__console.print('\n')

            self.__console.print(f"Please go to {device_verify_uri} to continue.\n")
        else:
            if "error" in device_code_res.json():
                error_message = f'The device code request failed with message "{device_code_json["error"]}"'
            else:
                error_message = "The device code request failed"

            self._logger.error(f'Failed to initiate the device code flow ({device_code_params})')
            raise LoginException(url=login_url, msg=error_message)

        token_url = auth_info.token_endpoint

        while time() < expiry:
            auth_token_res = session.post(
                token_url,
                data={
                    "grant_type": self.__grant_type,
                    "device_code": device_code,
                    "client_id": client_id,
                },
            )

            auth_token_json = auth_token_res.json()
            if in_global_debug_mode:
                self._logger.debug(f'Response from {token_url}:\n{pformat(auth_token_json, indent=2)}')

            if auth_token_res.ok:
                self._logger.debug('Response: Authorized')
                session.close()
                return auth_token_json
            elif "error" in auth_token_json:
                if auth_token_json.get("error") == "authorization_pending":
                    self._logger.debug('Response: Pending on authorization...')
                    sleep(poll_interval)
                    continue

                error_msg = "Failed to retrieve a token"
                if "error_description" in auth_token_json:
                    error_msg += f": {auth_token_json['error_description']}"

                self._logger.error('Exceeded the waiting time limit for the device code')
                raise LoginException(url=token_url, msg=error_msg)
            else:
                self._logger.debug('Response: Unknown state')
                sleep(poll_interval)

        raise LoginException(url=token_url, msg="The authorize step timed out.")