#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#

import logging
from urllib.parse import urlencode

import OpenSSL
import importlib_resources as pkg_resources
import requests
from colorama import Fore, Style

from aos_prov.utils.errors import DeviceRegisterError, CloudAccessError
from aos_prov.utils.user_credentials import UserCredentials
from aos_prov.utils.common import console

logger = logging.getLogger(__name__)

DEFAULT_REGISTER_HOST = 'aoscloud.io'
DEFAULT_REGISTER_PORT = 10000


class CloudAPI:
    __FILES_DIR = 'aos_prov'
    __ROOT_CA_CERT_FILENAME = 'files/1rootCA.crt'
    __REGISTER_URI_TPL = 'https://{}:{}/api/v1/units/provisioning/'
    __USER_ME_URI_TPL = 'https://{}:{}/api/v1/users/me/'
    __UNIT_STATUS_URL = 'https://{}:{}/api/v1/units/?{}'
    __FIND_UNIT_TPL = 'https://{}:{}/api/v1/units/?{}'
    __LINK_TO_THE_UNIT_ON_CLOUD_TPL = 'https://{}/oem/units/{}'

    def __init__(self, user_credentials: UserCredentials, cloud_api_port: int = DEFAULT_REGISTER_PORT):
        self._cloud_api_host = user_credentials.cloud_url
        self._cloud_api_port = cloud_api_port if cloud_api_port else DEFAULT_REGISTER_PORT
        self._user_credentials = user_credentials

    def check_cloud_access(self) -> None:
        """Check user have access to the cloud and his role is OEM.

        Raises:
            CloudAccessError: If user haven't access to the cloud or his role is not OEM.
        Returns:
            None
        """
        try:
            url = self.__USER_ME_URI_TPL.format(self._cloud_api_host, self._cloud_api_port)
            server_certificate = pkg_resources.files(self.__FILES_DIR) / self.__ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    resp = requests.get(url, verify=server_certificate_path,
                                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name))

                if resp.status_code != 200:
                    print('Auth error: {}'.format(resp.text))
                    raise CloudAccessError('You do not have access to the cloud!')

                user_info = resp.json()
                if user_info['role'] != 'oem':
                    logger.debug('invalid user role'.format(resp.text))
                    raise CloudAccessError('You should use OEM account!')

            print(f'Operation will be executed on domain '
                  f'{Fore.CYAN}{self._cloud_api_host}{Style.RESET_ALL} using OEM '
                  f'{Fore.CYAN}{user_info["oem"]["title"]}{Style.RESET_ALL} by user: '
                  f'{Fore.CYAN}{user_info["username"]}{Style.RESET_ALL}')
        except ConnectionError as e:
            raise CloudAccessError('Failed to connect to the cloud')
        except (requests.exceptions.RequestException, ValueError, OSError, OpenSSL.SSL.Error) as e:
            logger.error('Check access exception: {}'.format(e))
            raise CloudAccessError('Failed to connect to the cloud')
        except ConnectionRefusedError as e:
            raise CloudAccessError('Failed to connect to the cloud')

    def register_device(self, payload):
        """Registers device in cloud. Returns registered metadata.
        :param: str - end_point for registering
        :param: str - path to server pem that contains certs and a private one
        :param: dict
        :return: dict
        """
        logger.info('Registering the board ...')
        end_point = self.__REGISTER_URI_TPL.format(self._cloud_api_host, self._cloud_api_port)

        try:
            logger.debug('Sending to %s payload: %s', end_point, payload)
            server_certificate = pkg_resources.files(self.__FILES_DIR) / self.__ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    ret = requests.post(end_point, json=payload, verify=server_certificate_path,
                                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name))

                    if ret.status_code == 400:
                        try:
                            resp_content = ret.content.decode()
                            print(str(resp_content))
                            try:
                                answer = ret.json()['non_field_errors'][0]
                                logger.info('Registration error: ' + answer)
                            except:
                                pass

                        except UnicodeDecodeError:
                            resp_content = ret.content
                            print(resp_content)
                        logger.debug('Cloud response: {}'.format(resp_content))
                    ret.raise_for_status()
                    response = ret.json()
        except (requests.exceptions.RequestException,
                ValueError, OSError, OpenSSL.SSL.Error) as e:
            logger.debug(e)
            print(e)
            raise DeviceRegisterError('Failed to register board.')

        return response

    def check_unit_is_not_provisioned(self, system_uid):
        logger.info('Get unit\'s status on the cloud ...')
        try:
            end_point = self.__UNIT_STATUS_URL.format(
                self._cloud_api_host,
                self._cloud_api_port,
                urlencode({'system_uid': system_uid})
            )
            server_certificate = pkg_resources.files(self.__FILES_DIR) / self.__ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    response = requests.get(end_point, verify=server_certificate_path,
                                            cert=(temp_creds.cert_file_name, temp_creds.key_file_name))

        except (requests.exceptions.RequestException,
                ValueError, OSError, OpenSSL.SSL.Error) as e:
            logger.error('Failed to check unit\'s status: %s', e)
            raise DeviceRegisterError('Failed to HTTP GET: ', e)

        response_json = response.json()
        if 'results' not in response_json or 'count' not in response_json:
            raise DeviceRegisterError('Invalid answer from the cloud. Please update current library')

        if response_json['count'] == 0:
            # There is no such board on the cloud
            return

        if response_json.get('results', [{}])[0].get('board') is not None:
            raise DeviceRegisterError('Unit is already provisioned. Please do deprovisioning first.')

    def get_unit_link_by_system_uid(self, system_uid):
        end_point = self.__FIND_UNIT_TPL.format(
            self._cloud_api_host,
            self._cloud_api_port,
            urlencode({'system_uid': system_uid})
        )
        try:
            server_certificate = pkg_resources.files(self.__FILES_DIR) / self.__ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    response = requests.get(end_point, verify=server_certificate_path,
                                            cert=(temp_creds.cert_file_name, temp_creds.key_file_name))
            unit_id = response.json()['results'][0]['id']
            return self.__LINK_TO_THE_UNIT_ON_CLOUD_TPL.format(self._cloud_api_host, unit_id)
        except Exception:
            return None

    def use_model_name_param(self) -> bool:
        end_point = self.__REGISTER_URI_TPL.format(self._cloud_api_host, self._cloud_api_port)
        server_certificate = pkg_resources.files(self.__FILES_DIR) / self.__ROOT_CA_CERT_FILENAME
        with pkg_resources.as_file(server_certificate) as server_certificate_path:
            with self._user_credentials.user_credentials as temp_creds:
                resp = requests.options(end_point, verify=server_certificate_path,
                                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name))
                return 'model_name' in resp.json()['actions']['POST']
