"""This module sends request to the ITS Private Cloud API.

`API Reference <https://vss-wiki.eis.utoronto.ca/display/API/>`__.
"""
import datetime
import os
import platform
import re
from typing import Dict, List, Optional, Tuple, Union
import warnings

import requests

from pyvss.const import (
    API_ENDPOINT_BASE, DATETIME_FMT, DEFAULT_DEBUG, DEFAULT_DRY_RUN,
    DEFAULT_TIMEOUT, PACKAGE_NAME, VALID_VM_BUILD_PROCESS, VALID_VM_DISK_MODE,
    VALID_VM_DISK_SHARING, VALID_VM_EXTRA_CFG, VALID_VM_FIRMWARE_TYPE,
    VALID_VM_NIC_TYPE, VALID_VM_SCSI_CONTROLLER, VALID_VM_USAGE, VALID_VM_VMX,
    VSS_S3_STS_URL, VSS_S3_SVC_URL, VSS_S3_URL, __version__ as product_version)
from pyvss.enums import RequestStatus
from pyvss.exceptions import VssError
from pyvss.helper import HTTPBasicAuth, is_list_of, normalize_str

warnings.simplefilter('always')


try:
    import minio

    HAS_MINIO = True
except ImportError:
    HAS_MINIO = False


class VssManager:
    """Class containing methods to interact with the VSS REST API.

    Example::

        vss = VssManager(tk='access-token')
        vss.whoami()
        vss.ping()


    If tk is none it will get the token from the
    ``VSS_API_TOKEN`` environment variable.

    Example::

        vss = VssManager()
        vss.whoami()
    """

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'
    _content_type = 'application/json'

    def __init__(
        self,
        tk=None,
        api_endpoint=None,
        debug=False,
        timeout=None,
        dry_run=False,
    ):
        """Create VSS Manager to interact with the REST API.

        :param tk: REST API access token. also set by
          env var ``VSS_API_TOKEN``.
        :type tk: str
        :param api_endpoint: REST API endpoint defaults to
         https://vss-api.eis.utoronto.ca
        :type api_endpoint: str
        :param debug: turn debug mode on
        :param timeout: request timeout. also set by
          env var ``VSS_API_TIMEOUT``.
        :type timeout: int
        """
        self.user_agent = self._default_user_agent()
        self.api_endpoint_base = api_endpoint or API_ENDPOINT_BASE
        self.api_endpoint = f'{self.api_endpoint_base}/v2'
        self.token_endpoint = '{}/auth/request-token'.format(
            self.api_endpoint_base
        )
        self.tf_enabled = False
        self.tf_endpoint = f'{self.api_endpoint_base}/tf'
        self.api_token = tk or os.environ.get('VSS_API_TOKEN')
        self.debug = debug or os.environ.get('VSS_API_DEBUG', DEFAULT_DEBUG)
        self.timeout = timeout or os.environ.get(
            'VSS_API_TIMEOUT', DEFAULT_TIMEOUT
        )
        # test mode:
        self._dry_run = None
        if dry_run is not None:
            self.dry_run = dry_run
        else:
            self.dry_run = os.environ.get('VSS_API_DRY_RUN', DEFAULT_DRY_RUN)
        # supported objects
        self.s_vm_build = None
        self.s_nic_types = None
        self.s_scsi_controllers = None
        self.s_disk_back_modes = None
        self.s_vmx_versions = None
        self.s_vss_options = None
        self.s_disk_back_sharing = None
        self.s_scsi_controllers_sharing = None
        self.s_extra_config_options = None
        self.s_firmware_types = None
        # other services
        self.vskey_stor = None
        self.vskey_stor_s3api = None
        self.vskey_stor_s3_gui = None
        self.vskey_stor_s3_ak = None
        self.vskey_stor_s3_sk = None

    @property
    def dry_run(self):
        """Get dry_run value."""
        return self._dry_run

    @dry_run.setter
    def dry_run(self, value):
        """Set dry_run value."""
        if value is not None:
            self._dry_run = bool(value)

    def __repr__(self) -> str:
        """Return the representation of the Configuration."""
        view = {
            "api_endpoint": self.api_endpoint,
            "access_token": 'yes' if self.api_token is not None else 'no',
            "tf_enabled": 'yes' if self.tf_enabled is not None else 'no',
            "timeout": self.timeout,
            "debug": self.debug,
            "dry_run": self.dry_run,
        }
        return f"<{self.__class__.__name__}({view})"

    def pre_load(self):
        """Load in class many data from the API."""
        self.s_vm_build = self.get_supported_build_types(only_type=True)
        self.s_nic_types = self.get_supported_nic_types(only_type=True)
        self.s_scsi_controllers = self.get_supported_scsi_controllers(
            only_type=True
        )
        self.s_disk_back_modes = self.get_supported_disk_backing_modes(
            only_type=True
        )
        self.s_vmx_versions = self.get_supported_vmx_types(only_type=True)
        self.s_vss_options = self.get_supported_vss_options(only_option=True)
        self.s_disk_back_sharing = self.get_supported_disk_sharing(
            only_type=True
        )
        self.s_scsi_controllers_sharing = self.get_supported_scsi_sharing(
            only_type=True
        )
        self.s_extra_config_options = self.get_supported_extra_cfg_options(
            only_option=True
        )
        self.s_firmware_types = self.get_supported_firmware_types(
            only_type=True
        )

    @staticmethod
    def _default_user_agent(
        name=PACKAGE_NAME, version=product_version, extensions=''
    ):
        """Generate default user agent."""
        environment = {
            'product': name,
            'product_version': version,
            'python_version': platform.python_version(),
            'system': platform.system(),
            'system_version': platform.release(),
            'platform_details': platform.platform(),
            'extensions': extensions,
        }
        # User-Agent:
        # <product>/<version> (<system-information>)
        # <platform> (<platform-details>) <extensions>
        user_agent = (
            '{product}/{product_version}'
            ' ({system}/{system_version}) '
            'Python/{python_version} ({platform_details}) '
            '{extensions}'.format(**environment)
        )
        return user_agent

    @staticmethod
    def _process_extra_cfg(options: Optional[List[Dict]]) -> List[Dict]:
        """Process extra configuration to exclude vmware drivers and tools."""
        r = []
        if options is None:
            return r
        for o in options:
            for k, v in o.items():
                if (
                    '.Cb.' not in k
                    and '.vmtools.' not in k
                    and '.driver.' not in k
                ):
                    item = {k: v}
                    r.append(item)
        return r

    @staticmethod
    def _get_credentials_from_env(
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get credentials from input or environment."""
        # get user/pwd
        username = user or os.environ.get('VSS_API_USER')
        password = password or os.environ.get('VSS_API_USER_PASS')
        # normalize
        username_u = normalize_str(username)
        password_u = normalize_str(password)
        return username_u, password_u

    def request_totp(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Request TOTP."""
        username_u, password_u = self._get_credentials_from_env(user, password)
        rv = self.request(
            f'{self.tf_endpoint}/request-token',
            method=self.POST,
            auth=HTTPBasicAuth(username_u, password_u),
        )
        return rv

    def enable_totp(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        method: Optional[str] = 'EMAIL',
        **kwargs,
    ) -> Dict:
        """Enable totp on account.

        Provided either by function argument or env var:
        - ``VSS_API_USER``: username
        - ``VSS_API_USER_PASS``: password

        :param user: Username
        :type user: str
        :param password: Username password
        :type password: str
        :param method: Method to enable TOTP (SMS, AUTHENTICATOR, EMAIL).
        :type method: str
        :return:
        """
        payload = dict(method=method)
        method = method.upper()
        # get user/pwd
        username_u, password_u = self._get_credentials_from_env(user, password)
        if method == 'SMS':
            phone = kwargs.get('phone')
            if phone is None:
                raise VssError('phone is required for SMS')
            payload['phone'] = phone
        rv = self.request(
            f'{self.tf_endpoint}/enable',
            method=self.POST,
            auth=HTTPBasicAuth(username_u, password_u),
            payload=payload,
        )
        return rv

    def disable_totp(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Disable TOTP on account.

        :param user: Username
        :type user: str
        :param password: Username password
        :type password: str
        :return:
        """
        # get user/pwd
        username_u, password_u = self._get_credentials_from_env(user, password)
        rv = self.request(
            f'{self.tf_endpoint}/disable',
            method=self.POST,
            auth=HTTPBasicAuth(username_u, password_u),
        )
        return rv

    def disable_totp_confirm(
        self,
        token: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Disable TOTP on account with confirmation token.

        :param token: Confirmation token
        :type token: str
        :param user: Username
        :type user: str
        :param password: Username password
        :type password: str
        :return:
        """
        # get user/pwd
        username_u, password_u = self._get_credentials_from_env(user, password)
        rv = self.request(
            f'{self.tf_endpoint}/disable/{token}',
            method=self.POST,
            auth=HTTPBasicAuth(username_u, password_u),
        )
        return rv

    def verify_totp(self, user=None, password=None, otp=None):
        """Verify TOTP.

        Provided either by function argument or env var:
        - ``VSS_API_USER``: username
        - ``VSS_API_USER_PASS``: password
        - ``VSS_API_USER_OTP``: one time password

        :param user: Username
        :type user: str
        :param password: Username password
        :type password: str
        :param otp: one time password
        :type otp: str
        """
        otp = otp or os.environ.get('VSS_API_USER_OTP')
        # get user/pwd
        username_u, password_u = self._get_credentials_from_env(user, password)

        rv = self.request(
            f'{self.tf_endpoint}/verify',
            method=self.POST,
            auth=HTTPBasicAuth(username_u, password_u),
            payload={'otp': otp},
        )
        return rv

    def get_token(self, user=None, password=None, otp=None):
        """Generate token based username and password.

        Provided either by function argument or env var:
        - ``VSS_API_USER``: username
        - ``VSS_API_USER_PASS``: password
        - ``VSS_API_USER_OTP``: one time password

        :param user: Username
        :type user: str
        :param password: Username password
        :type password: str
        :param otp: one time password
        :type otp: str
        :return: generated token or VssError

        """
        import jwt

        otp = otp or os.environ.get('VSS_API_USER_OTP')
        # get user/pwd
        username_u, password_u = self._get_credentials_from_env(user, password)

        tk_request = self.request(
            self.token_endpoint,
            method=self.POST,
            auth=HTTPBasicAuth(username_u, password_u),
            payload={'otp': otp},
        )

        if tk_request.get('token'):
            self.api_token = tk_request.get('token')
            payload = jwt.decode(
                self.api_token, options=dict(verify_signature=False)
            )
            self.tf_enabled = payload.get('otp', False)
            return self.api_token
        else:
            raise VssError('Could not generate token')

    def get_vskey_stor(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        s3_endpoint: Optional[str] = None,
    ):
        """Instantiate a Minio Client to interact with VSKEY-STOR.

        :param user: Username to access remote configuration.
        :param password: Username password to access remote configuration.
        :param access_key: Access key for minio service.
        :param secret_key: Secret key for minio service.
        :param s3_endpoint: S3 endpoint to interact with minio.

        .. warning::
         `Min.IO <https://pypi.org/project/minio/>`__
         module is required

        Example::

            # Creating an instance with username and password if
            # no env var was set
            vss.get_vskey_stor(user='user',
            password='P455w00rD')

            # Download inventory file
            url = vss.vskey_stor.presigned_get_object(
             'ut-vss',
             'inventory/88c4a526-4096-4920-9c07-3d25b6347f70.json'
            )
            rv = requests.get(url)
            Path('88c4a526-4096-4920-9c07-3d25b6347f70.json').write_bytes(rv.content)

            # Upload image
            vss.vskey_stor.fput_object(
             bucket_name='ut-vss',
             object_name='jammy-server-cloudimg-amd64.ova',
             file_path=os.path.expanduser('~/Downloads/jammy-server-cloudimg-amd64.ova')
             )
        """
        if not HAS_MINIO:
            raise VssError('minio library is required')

        from minio import Minio
        from urllib.parse import urlparse

        self.vskey_stor_s3api = os.environ.get('VSS_S3_API', s3_endpoint)
        self.vskey_stor_s3_ak = os.environ.get('VSS_S3_ACCESS_KEY', access_key)
        self.vskey_stor_s3_sk = os.environ.get('VSS_S3_SECRET_KEY', secret_key)

        if not all(
            [
                self.vskey_stor_s3api,
                self.vskey_stor_s3_ak,
                self.vskey_stor_s3_sk,
            ]
        ):
            self.init_vskey_stor(user, password)
        # create client
        self.vskey_stor = Minio(
            urlparse(self.vskey_stor_s3api).netloc,
            self.vskey_stor_s3_ak,
            self.vskey_stor_s3_sk,
        )

        return self.vskey_stor.list_buckets()

    def _get_auth_from_creds(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> HTTPBasicAuth:
        """Get HTTPBasicAuth from credentials."""
        username_u, password_u = self._get_credentials_from_env(user, password)
        return HTTPBasicAuth(username_u, password_u)

    @staticmethod
    def get_vskey_stor_cfg() -> Dict:
        """Get vskey-stor configuration."""
        s3_endpoint = os.environ.get('VSS_S3_URL', VSS_S3_URL)
        adm_endpoint = VSS_S3_SVC_URL.format(s3_server=s3_endpoint)
        status_endpoint = VSS_S3_STS_URL.format(s3_svc_url=adm_endpoint)
        return {
            'endpoint': s3_endpoint,
            'minio_svc': adm_endpoint,
            'status': status_endpoint,
        }

    def get_vskey_stor_status(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Dict:
        """Get vskey-stor status."""
        auth = self._get_auth_from_creds(user, password)
        rv = requests.get(self.get_vskey_stor_cfg()['status'], auth=auth)
        return rv.json()

    def init_vskey_stor(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize VSS s3 configuration."""
        auth = self._get_auth_from_creds(user, password)
        cfg = self.get_vskey_stor_cfg()
        adm_endpoint = cfg['minio_svc']
        status = self.get_vskey_stor_status(user, password)
        status_minio = status['minIO']
        if status_minio == 'running':
            pass
        elif status_minio == 'dormant':
            # Wake up service (POST /minio-svc/index.php action=wake).
            rv_wake = requests.post(
                adm_endpoint, auth=auth, data=dict(action='wake')
            )
            rv_wake.raise_for_status()
        elif status_minio == 'configured':
            # Start Service (POST /minio-svc/index.php action=start)
            rv_start = requests.post(
                adm_endpoint, auth=auth, data=dict(action='start')
            )
            rv_start.raise_for_status()
        elif status_minio == 'not-configured':
            # Service initialization (POST /minio-svc/index.php action=init)
            rv_init = requests.post(
                adm_endpoint, auth=auth, data=dict(action='init')
            )
            rv_init.raise_for_status()
            # Generate S3 Keys (POST /minio-svc/index.php action=generate)
            rv_generate = requests.post(
                adm_endpoint, auth=auth, data=dict(action='generate')
            )
            rv_generate.raise_for_status()
            # Start Service (POST /minio-svc/index.php action=start)
            rv_start = requests.post(
                adm_endpoint, auth=auth, data=dict(action='start')
            )
            rv_start.raise_for_status()
        else:
            raise VssError(f'Invalid minIO svc status. {status_minio}')
        # check for status again
        status = self.get_vskey_stor_status(user, password)
        # set attrs
        self.vskey_stor_s3api = status['S3api']
        self.vskey_stor_s3_gui = status['S3gui']
        self.vskey_stor_s3_ak = status['accessKey']
        self.vskey_stor_s3_sk = status['secretKey']
        return status

    # User Management methods
    def get_user_isos(self, show_all=False, per_page=250, **kwargs):
        """Obtain list of user ISO images in personal store.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        If you have uploaded an iso to VSKEY-STOR_ already
        and is not listed, run :py:func:`sync_user_isos`.

        :param show_all: Whether to show all ISO images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/user/image/iso', show_all=show_all, **kwargs
        )
        return data

    def sync_user_isos(self):
        """Submit an ISO Image Synchronization request.

        Sync between VSKEY-STOR_ and API.
        Verify status with :py:func:`get_image_sync_request`.

        :return: request object
        """
        json = self.request('/user/image/iso', method=self.PATCH)
        return json.get('data')

    def get_user_vmdks(self, show_all=False, per_page=250, **kwargs):
        """Obtain list of user VMDK files in personal store.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        If you have uploaded an iso to VSKEY-STOR_ already
        and is not listed, run :py:func:`sync_user_vmdks`.

        :param show_all: Whether to show all VMDK files or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/user/file/vmdk', show_all=show_all, **kwargs
        )
        return data

    def sync_user_vmdks(self):
        """Submit a VMDK File Synchronization request.

        Sync between VSKEY-STOR_ and API.
        Verify status with :py:func:`get_vmdk_sync_request`.

        :return: request object
        """
        json = self.request('/user/file/vmdk', method=self.PATCH)
        return json.get('data')

    def get_user_floppies(self, show_all=False, per_page=250, **kwargs):
        """Obtain list of user Floppy images in personal store.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        If you have uploaded a .flp image to VSKEY-STOR_ already
        and is not listed, run :py:func:`sync_user_floppies`.

        :param show_all: Whether to show all floppy images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects
        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/user/image/floppy', show_all=show_all, **kwargs
        )
        return data

    def sync_user_floppies(self):
        """Submit an Floppy Image Synchronization request.

        Sync between VSKEY-STOR_ and API. Verify status with
        :py:func:`get_image_sync_request`.
        :return: request object
        """
        json = self.request('/user/image/floppy', method=self.PATCH)
        return json.get('data')

    def get_user_vm_images(self, show_all=False, per_page=250, **kwargs):
        """Obtain list of user OVA/OVF VM images in personal store.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        If you have uploaded an OVF/OVA image to VSKEY-STOR_ already and
        is not listed, run :py:func:`sync_user_vm_images`.

        :param show_all: Whether to show all vm images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects
        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/user/image/vm', show_all=show_all, **kwargs
        )
        return data

    def sync_user_vm_images(self):
        """Submit an OVA/OVF VM Image Synchronization request.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        Sync between VSKEY-STOR_ and API. Verify status with
        :py:func:`get_image_sync_request`.

        :return: request object
        """
        json = self.request('/user/image/vm', method=self.PATCH)
        return json.get('data')

    def get_user_roles(self):
        """Get both request and access roles of current user.

        :return: object
        """
        json = self.request('/user/role', method=self.GET)
        return json.get('data')

    def get_user_status(self):
        """Get your account current status.

        Attributes included:
        - active: whether user is active or not
        - created_on: time stamp when user was created
        - last_access: most recent access time stamp
        - updated_on: last time user was updated

        :return: object
        """
        json = self.whoami()
        return json.get('status')

    def get_user_totp(self):
        """Get account MFA TOTP status.

        Attributes included:
        - enabled: whether mfa totp is enabled
        - enabled_onn: time stamp when user enabled mfa
        - disabled_on: time stamp when user disabled mfa
        - method: mfa totp token generation method

        :return: object
        """
        json = self.whoami()
        return json.get('totp')

    def get_user_personal(self):
        """Get your account info.

        Such as email, phone, username and full name.

        :return: object
        """
        json = self.request('/user/personal', method=self.GET)
        return json.get('data')

    def get_user_ldap(self):
        """Get account ldap info.

        Attributes included:
        - pwd_account_locked_time: shows whether your LDAP account is locked
        - pwd_change_time: time stamp when you changed your pwd
        - mail: associated emails
        - auth_timestamp: last authenticated time stamp

        :return: object
        """
        json = self.request('/user/ldap', method=self.GET)
        return json.get('data')

    def get_user_groups(self, show_all=False, **kwargs):
        """Get current user groups.

        :return: list of str
        """
        data = self._get_objects(
            pag_resource='/user/group', show_all=show_all, **kwargs
        )
        return data

    def get_groups(self, show_all=False, **kwargs):
        """Get groups.

        :return: list of str
        """
        data = self._get_objects(
            pag_resource='/group', show_all=show_all, **kwargs
        )
        return data

    def get_group(self, g_id):
        """Get group info.

        :param g_id: group identifier
        :type g_id: int
        :return: object
        """
        json = self.request(f'/group/{g_id}', method=self.GET)
        return json.get('data')

    def get_group_members(self, g_id):
        """Get group members.

        :param g_id: group identifier
        :return: list
        """
        json = self.request(f'/group/{g_id}/member', method=self.GET)
        return json.get('data')

    def get_user_token(self, token_id):
        """Get token id data.

        Attributes included:
        - value
        - status

        :param token_id: Access token id to manage
        :type token_id: int
        :return: object

        """
        json = self.request(f'/user/token/{token_id}', method=self.GET)
        return json.get('data')

    def disable_user_token(self, token_id):
        """Disable access token id.

        :param token_id: token id to disable
        :type token_id: int
        :return: status dict
        """
        json = self.request(f'/user/token/{token_id}', method=self.PUT)
        return json

    def get_user_tokens(self, show_all=False, **kwargs):
        """Get user tokens.

        :param show_all: Whether to show all tokens or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `User <https://vss-wiki.eis.utoronto.ca/x/tgGC>`__

        Example::

            vss.get_user_tokens(filter='active,eq,true',
                                per_page=10)
        """
        data = self._get_objects(
            pag_resource='/user/token', show_all=show_all, **kwargs
        )
        return data

    def delete_user_token(self, token_id):
        """Delete token id.

        :param token_id: Token id to delete
        :type token_id: int
        :return: dict with request status
        """
        json = self.request(f'/user/token/{token_id}', method=self.DELETE)
        return json

    def get_user_ssh_keys(self, show_all=False, **kwargs):
        """Get user ssh-keys.

        :param show_all: Whether to show all SSH Keys or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details.

        Example::

            vss.get_user_ssh_keys(filter='type,eq,ssh-rsa',
                                  per_page=10)
        """
        data = self._get_objects(
            pag_resource='/user/ssh-key', show_all=show_all, **kwargs
        )
        return data

    def get_user_ssh_key(self, key_id):
        """Get SSH Key id data.

        Attributes included:
        - fingerprint
        - type
        - value
        - comment

        :param key_id: SSHKey id
        :type key_id: int
        :return: object
        """
        json = self.request(f'/user/ssh-key/{key_id}', method=self.GET)
        return json.get('data')

    def create_user_ssh_key(self, public_key):
        """Create a new SSH Public Key entry.

        :param public_key: SSH Public Key string
        :type public_key: str
        :return:
        """
        payload = dict(value=public_key)
        json = self.request('/user/ssh-key', method=self.POST, payload=payload)
        return json.get('data')

    def create_user_ssh_key_path(self, public_key_path):
        """Create a new SSH Public Key entry from file path.

        :param public_key_path: Full path to SSH Public Key string
        :type public_key_path: str
        :return:
        """
        if not os.path.exists(public_key_path):
            raise VssError('File does not exist')

        with open(public_key_path, 'rb') as f:
            public_key = f.read()

        payload = dict(value=public_key.decode('utf-8'))
        json = self.request('/user/ssh-key', method=self.POST, payload=payload)
        return json.get('data')

    def delete_user_ssh_key(self, key_id):
        """Delete given SSH Key id.

        :param key_id: SSH Key id to delete
        :type key_id: int
        :return: dict with request status
        """
        json = self.request(f'/user/ssh-key/{key_id}', method=self.DELETE)
        return json

    def get_user_notification_settings(self):
        """Get all notification settings.

        :return: object
        """
        json = self.request('/user/setting/notification', method=self.GET)
        return json.get('data')

    def get_user_request_notification_settings(self):
        """Get all notification request settings.

        :return: object
        """
        json = self.request(
            '/user/setting/notification/request', method=self.GET
        )
        return json.get('data')

    def get_user_notification_method(self):
        """Get notification method.

        :return: object
        """
        json = self.request(
            '/user/setting/notification/method', method=self.GET
        )
        return json.get('data')

    def update_user_notification_method(self, method):
        """Update notification method.

        :param method: notification format mail|message
        :type method: str
        :return: object
        """
        values = ['mail', 'message']
        if method not in values:
            raise VssError('Format should be in {}'.format(', '.join(values)))

        payload = dict(value=method)
        _json = self.request(
            '/user/setting/notification/method',
            method=self.PUT,
            payload=payload,
        )
        if self.debug:
            print(_json)
        return self.get_user_notification_method()

    def get_user_notification_format(self):
        """Get notification format.

        :return: dict
        """
        json = self.request(
            '/user/setting/notification/format', method=self.GET
        )
        return json.get('data')

    def update_user_notification_format(self, fmt):
        """Update notifications format.

        :param fmt: notification format (text, html)
        :type fmt: str
        :return: object
        """
        values = ['text', 'html']
        if fmt not in values:
            raise VssError('Format should be in {}'.format(', '.join(values)))

        payload = dict(value=fmt)
        _json = self.request(
            '/user/setting/notification/format',
            method=self.PUT,
            payload=payload,
        )
        if self.debug:
            print(_json)
        return self.get_user_notification_format()

    def disable_user_request_all_notification(self):
        """Disable all email notification from requests.

        :return: updated  object
        """
        json = self.update_user_request_notification_settings(
            attribute='none', value=True
        )
        return json

    def enable_user_request_all_notification(self):
        """Enable all email notification from requests.

        :return: updated object
        """
        json = self.update_user_request_notification_settings(
            attribute='all', value=True
        )
        return json

    def enable_user_request_error_notification(self):
        """Enable notification by errors from requests.

        Receive notification if a request (change, new, etc.) has
        resulted in error.

        :return: updated email settings object
        """
        json = self.update_user_request_notification_settings(
            attribute='error', value=True
        )
        return json

    def disable_user_request_error_notification(self):
        """Disable notification by errors from requests.

        Stop receiving notification if a request (change, new, etc.)
        has resulted in error.

        :return: updated email settings object
        """
        json = self.update_user_request_notification_settings(
            attribute='error', value=True
        )
        return json

    def enable_user_request_completion_notification(self):
        """Enable notification by completion from requests.

        Receive notification if a request (change, new, etc.) has
        completed successfully.

        :return: updated email settings object
        """
        json = self.update_user_request_notification_settings(
            attribute='completion', value=True
        )
        return json

    def disable_user_request_completion_notification(self):
        """Disable notification by completion from requests.

        Stop receiving notification if a request (change, new, etc.)
        has completed successfully.

        :return: updated email settings object
        """
        json = self.update_user_request_notification_settings(
            attribute='completion', value=False
        )
        return json

    def enable_user_request_submission_notification(self):
        """Enable notification by submission from requests.

        Receive notification if a request (change, new, etc.) has
        submitted successfully.

        :return: updated email settings object
        """
        json = self.update_user_request_notification_settings(
            attribute='submission', value=True
        )
        return json

    def disable_user_request_submission_notification(self):
        """Disable notification by submission from requests.

        Stop receiving notification if a request (change, new, etc.) has
        submitted successfully.

        :return: updated email settings object
        """
        json = self.update_user_request_notification_settings(
            attribute='submission', value=False
        )
        return json

    def get_user_digest_settings(self):
        """Get current user digest settings.

        Weekly digests are notifications sent summarizing a group of objects.
        :return: object
        """
        json = self.request('/user/setting/digest', method=self.GET)
        return json.get('data')

    def get_user_message_digest(self):
        """Get current user weekly message digest settings.

        :return: object
        """
        json = self.get_user_digest_settings()
        cfg = {'message': json.get('message')}
        return cfg

    def enable_user_message_digest(self):
        """Enable Message weekly digest.

        :return: updated email settings object
        """
        json = self.request(
            '/user/setting/digest/message',
            method=self.PUT,
            payload=dict(value=True),
        )
        return json.get('data')

    def disable_user_message_digest(self):
        """Disable Message weekly digest.

        :return: updated email settings object
        """
        json = self.request(
            '/user/setting/digest/message',
            method=self.PUT,
            payload=dict(value=False),
        )
        return json.get('data')

    def update_user_request_notification_settings(self, attribute, value):
        """Update user request notification attribute and value.

        :param attribute: attribute to update. could be
         ``<error|none|completion|submission>``
        :type attribute: str
        :param value: True or false
        :type value: bool
        :return: updated email settings object
        """
        json_payload = dict(attribute=attribute, value=value)
        json = self.request(
            '/user/setting/notification/request',
            method=self.PUT,
            payload=json_payload,
        )
        json.update(self.get_user_request_notification_settings())
        return json

    def whoami(self):
        """Retrieve current user summary.

        :return: object
        """
        json = self.request('/user')
        return json.get('data')

    def ping(self):
        """Perform Http "Ping" to server.

        Replies with request info in form of dictionary.

        :return: object
        """
        json = self.request('/ping')
        return json.get('data')

    def get_vss_services(self, show_all=False, **kwargs):
        """Get VSS Services.

        Filter and sort available Service definition.

        :param show_all: Whether to show all services or just
         the default count
        :type show_all: bool
        :param kwargs:
        :return:
        """
        data = self._get_objects(
            pag_resource='/vss/service', show_all=show_all, **kwargs
        )
        return data

    def get_user_messages(self, show_all=False, **kwargs):
        """Get user messages.

        :param show_all: Whether to show all messages or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `User <https://vss-wiki.eis.utoronto.ca/x/tgGC>`__

        Example::

            vss.get_user_messages(filter='kind,eq,NOTICE',
                                  per_page=10)
        """
        data = self._get_objects(
            pag_resource='/user/message', show_all=show_all, **kwargs
        )
        return data

    def get_user_message(self, m_id):
        """Get given user message.

        :param m_id: message id
        :type m_id: int
        :return: message object
        """
        json = self.request(f'/user/message/{m_id}')
        return json.get('data')

    def ack_user_message(self, m_id):
        """Acknowledge given user message.

        :param m_id: message id
        :type m_id: int
        :return: message object
        """
        return self.request(f'/user/message/{m_id}', method=self.PATCH)

    # Operating systems
    def get_os(self, name=None, show_all=True, **kwargs):
        """Get Virtual Machine supported Guest Operating systems.

        Attribute definition:
        - name: Guest operating system full name. i.e. CentOS 4/5
        - id: Guest operating system id. i.e. centosGuest

        :param show_all: Whether to show all requests or just
         the default count
        :param name: Filter by Guest OS full name
        :type show_all: bool
        :param kwargs: arguments to pass such as:
            - guest_id: Guest OS identifier
            - full_name: Guest OS full name.

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Operating Systems <https://vss-wiki.eis.utoronto.ca/x/EQGC>`__

        Example::

            vss.get_os(sort='created_on,desc', per_page=100)


        """
        if name:
            kwargs.update({'filter': f'full_name,like,{name}%'})
        data = self._get_objects(
            pag_resource='/os', show_all=show_all, **kwargs
        )
        return data

    # inventory management
    def get_inventory_properties(self):
        """List available properties to create an inventory report.

        :return: list
        """
        json = self.request('/inventory/options')
        dat = json.get('data')
        return [i['key'] for i in dat]

    def create_inventory_file(
        self, props=None, filters=None, transfer=False, fmt='json'
    ):
        """Submit a request to generate a full inventory report of your VMs.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        The report will be transferred if set to your space at
        VSKEY-STOR_ and also be available via
        :py:func:`download_inventory_result`.

        :param props: properties to include in report. exec
           :py:func:`get_inventory_properties` to get a full list.
        :type props: list
        :param transfer: whether to transfer to personal store at vskey-stor
        :type transfer: bool
        :param fmt: report format <json|csv>. default json
        :type fmt: str
        :param filters: Filters to add in the inventory report.
           attr:value format.
        :type filters: list
        :return: inventory request object

        .. note:: See
          `Inventory Docs <https://vss-wiki.eis.utoronto.ca/x/_gCC>`__
          for more information

        """
        json_payload = dict(properties=props, format=fmt, transfer=transfer)
        if filters:
            json_payload.update(filters)
        json = self.request(
            '/inventory', payload=json_payload, method=self.POST
        )
        return json.get('data')

    def download_inventory_result(self, request_id, directory=None):
        """Download given inventory report.

        :param request_id: Inventory request id
        :param directory: Directory to download file
        :return: full path to written file

        Example::

            vss.download_inventory_result(request_id=123,
                                          directory='~/Downloads')

            vss.download_inventory_result(request_id=123)


        .. note:: See
          `Inventory Docs <https://vss-wiki.eis.utoronto.ca/x/_gCC>`__
          for more information

        """
        response = self.request(f'/inventory/{request_id}', method=self.GET)
        # only requests.models.Response is allowed here
        if isinstance(response, requests.models.Response):
            # check if content disposition header is present
            content_disposition = response.headers.get('Content-Disposition')

            if content_disposition:
                _file_name_find = re.findall(
                    r'filename=(.*)', content_disposition
                )
                # check if search found filename
                _file_name = _file_name_find[0] if _file_name_find else ''
                if _file_name:
                    # check if directory exist
                    _directory = (
                        os.path.expanduser(directory)
                        if directory
                        else os.path.curdir
                    )
                    if not os.path.isdir(_directory):
                        os.mkdir(_directory)
                    # full_path
                    _full_path = os.path.join(_directory, _file_name)
                    with open(_full_path, 'wb') as f:
                        f.write(response.content)
                    return _full_path
                else:
                    raise VssError('File name was not found')
            else:
                raise VssError('File has not been created')
        else:
            msg = response.get('message', 'Invalid response')
            raise VssError(msg)

    # Request management
    def get_requests(self, **kwargs):
        """Get Summary of current requests submitted.

        :return: list of objects

        """
        json = self.request('/request', params=kwargs)
        return json.get('data')

    def _get_objects(self, pag_resource, show_all=False, **kwargs):
        """Get paginated objects.

        :param pag_resource: API resource to retrieve
        :type pag_resource: str
        :param show_all: true to show all objects
        :type show_all: bool
        :return: list of objects
        """
        params = dict(expand=1)
        params.update(kwargs)
        json = self.request(pag_resource, params=params)
        result = list()
        result_extend = result.extend
        while True:
            json_data = json.get('data')
            if not isinstance(json_data, list):
                break
            result_extend(json.get('data'))
            r_meta = json.get('meta')
            if r_meta:
                p_meta = r_meta.get('pages')
                next_url = p_meta.get('next_url')
                if not show_all or not p_meta or not next_url:
                    break
                json = self.request(next_url)
        return result

    def get_new_requests(self, show_all=False, **kwargs):
        """Get new vm deployment requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_new_requests(sort='created_on,desc', per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/new', show_all=show_all, **kwargs
        )
        return data

    def get_new_request(self, request_id):
        """Get given new request data.

        :param request_id: new request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/new/{request_id}')
        return json.get('data')

    def get_new_request_meta_data(self, request_id):
        """Get given new request meta data.

        :param request_id: new request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/new/{request_id}/meta_data')
        return json.get('data')

    def get_new_request_user_data(self, request_id, decode=False):
        """Get given new request submitted user data.

        Cloud-init user_data to preconfigure the guest os upon first boot.

        .. note:: Experimental feature and currently tested with Ubuntu
          Cloud Images and VMware Photon OS. Only supported on OVA/OVF
          deployments.

        :param request_id: new request id to get
        :type request_id: int
        :param decode: whether to decode user_data
        :type decode: bool
        :return: object

        """
        params = dict(decode=1) if decode else None
        json = self.request(
            f'/request/new/{request_id}/user_data', params=params
        )
        return json.get('data')

    def get_new_request_custom_spec(self, request_id):
        """Get given new request submitted custom specification.

        :param request_id: new request id to get
        :type request_id: int
        :return: object
        """
        json = self.request(f'/request/new/{request_id}/custom_spec')
        return json.get('data')

    def retry_new_request(self, request_id):
        """Retry given new request.

        Only if it has an "ERROR PROCESSED" status.

        :param request_id: new request id to get
        :type request_id: int
        :return: object
        """
        json = self.request(f'/request/new/{request_id}', method=self.PATCH)
        return json.get('data')

    def get_vm_change_requests(
        self, vm_id: str, show_all: bool = False, **kwargs
    ):
        """Get change requests associated to a virtual machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_vm_change_requests(vm_id='vm-123',
                                       filter='attribute,eq,name',
                                       per_page=100)

        """
        return self._get_objects(
            pag_resource=f'/vm/{vm_id}/change-request',
            show_all=show_all,
            **kwargs,
        )

    def retire_vm(
        self,
        vm_id: str,
        rtype: str,
        value: Dict,
        warning: Optional[int] = None,
        **kwargs,
    ) -> Optional[Dict]:
        """Create retirement request for a given VM.

        The retirement request allows to set a retirement
        date for a virtual machine. There are currently
        two types:

        - ``timedelta``: days, months and hours from now
          until retirement.
        - ``datetime``: specific timestamp to retire vm.

        The retirement request sends notifications to
        ``confirm`` or ``cancel`` if  a ``warning`` is set
        and will continue to notify until an action has been
        performed.

        Once the retirement request is confirmed, the request
        is marked for execution in the ``retire_on`` date set
        by either the ``timedelta`` or ``datetime`` provided
        initially. Once executed, a new Vm Change Request will
        be submitted to ``decommission`` the virtual machine

        If the retirement request is cancelled, no action
        is performed.

        :param vm_id: virtual machine moref or uuid.
        :type vm_id: str
        :param rtype: retirement request type: timedelta or datetime
        :type rtype: str
        :param value: payload of the given retirement request type.
        :type value: dict
        :param warning: set a notification to cancel or confirm in
          x given days
        :type warning: int
        :return:

        Example::

            warning = 15
            time_delta_val = {'days': 4, 'months': 6, 'hours': 0}
            r = vss.retire_vm(vm_id='vm-123', rtype='timedelta',
                              value=time_delta_val, warning=warning)

            warning = 30
            datetime_val = {'datetime': '2021-10-02 08:00'}
            r = vss.retire_vm(vm_id='vm-123', rtype='timedelta',
                              value=datetime_val, warning=warning)

        """
        type_lookup = {
            'timedelta': ['days', 'months', 'hours'],
            'datetime': ['datetime'],
        }
        try:
            attrs = type_lookup[rtype]
        except KeyError:
            raise VssError(
                f'Invalid type {type}. '
                f'Choose between: {",".join(type_lookup.keys())}'
            )
        for attr in attrs:
            try:
                _ = value[attr]
            except KeyError:
                raise VssError(
                    f'Missing {attr}. '
                    f'Type {type} must include: {",".join(type_lookup.keys())}'
                )
        value.update(dict(type=rtype))
        payload = dict(value=value)
        if warning is not None:
            payload['warning'] = dict(days=warning)
        payload.update(kwargs)
        if self.debug:
            print(payload)
        rv = self.request(
            f'/vm/{vm_id}/retirement', method=self.POST, payload=payload
        )
        if rv:
            return rv.get('data')
        return rv

    def get_vm_retirement_requests(
        self, vm_id: str, show_all: bool = False, **kwargs
    ) -> Optional[List[Dict]]:
        """Get retirement requests associated to a virtual machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_vm_retirement_requests(vm_id='vm-123',
                                           per_page=100)

        """
        return self._get_objects(
            pag_resource=f'/vm/{vm_id}/retirement',
            show_all=show_all,
            **kwargs,
        )

    def get_retirement_requests(
        self, show_all=False, **kwargs
    ) -> Optional[List[Dict]]:
        """Get retirement requests submitted for every change to a VM.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool
        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_retirement_requests(
                filter='status,eq,ERROR',
                per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/retirement', show_all=show_all, **kwargs
        )
        return data

    def get_retirement_request(self, request_id) -> Optional[Dict]:
        """Get given retirement request data.

        :param request_id: retirement request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/retirement/{request_id}')
        return json.get('data')

    def set_retirement_request_timedelta(
        self,
        request_id: int,
        hours: Optional[int] = 0,
        days: Optional[int] = 0,
        months: Optional[int] = 0,
    ) -> Optional[Dict]:
        """Change retirement request to timedelta.

        :param request_id: retirement request id
        :type request_id: int
        :param hours: number of hours from now until retirement.
        :type hours: int
        :param days: number of days from now until retirement.
        :type days: int
        :param months: number of months from now until retirement.
        :type months: int
        :return: object
        """
        payload = self.get_retirement_timedelta_spec(
            hours=hours, days=days, months=months
        )
        rv = self.request(
            f'/request/retirement/{request_id}/type',
            method=self.PUT,
            payload=payload,
        )
        return rv

    def set_retirement_request_datetime(
        self, request_id: int, date_time: str
    ) -> Optional[Dict]:
        """Change retirement request to datetime.

        :param request_id: retirement request id
        :type request_id: int
        :param date_time: Timestamp with the following format
         ``%Y-%m-%d %H:%M``.
        :type date_time: str
        :return: object
        """
        payload = self.get_retirement_datetime_spec(date_time)
        rv = self.request(
            f'/request/retirement/{request_id}/type',
            method=self.PUT,
            payload=payload,
        )
        return rv

    def update_warning_retirement_request(
        self, request_id: int, days: Optional[int] = None
    ):
        """Update warning for retirement request.

        :param request_id: retirement request id
        :type request_id: int
        :param days: number of days to receive a warning
        :type days: int
        :return: object

        """
        payload = None
        if days is not None:
            payload = dict(days=days)
        rv = self.request(
            f'/request/retirement/{request_id}/warning',
            method=self.PUT,
            payload=payload,
        )
        return rv

    def cancel_retirement_request(self, request_id: int):
        """Cancel retirement request."""
        rv = self.request(
            f'/request/retirement/{request_id}/cancel',
            method=self.PUT,
        )
        if rv:
            return rv.get('data')
        return rv

    def confirm_retirement_request(self, request_id: int):
        """Confirm retirement request.

        :param request_id: retirement request id
        :type request_id: int
        :return: object
        """
        rv = self.request(
            f'/request/retirement/{request_id}/confirm',
            method=self.PUT,
        )
        if rv:
            return rv.get('data')
        return rv

    def send_confirmation_retirement_request(self, request_id: int):
        """Send confirmation retirement request.

        :param request_id: retirement request id
        :type request_id: int
        :return: object
        """
        rv = self.request(
            f'/request/retirement/{request_id}/send-confirmation',
            method=self.PUT,
        )
        if rv:
            return rv.get('data')
        return rv

    def get_change_requests(self, show_all=False, **kwargs):
        """Get change requests submitted for every change to a VM.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_change_requests(filter='status,eq,ERROR',
                                    per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/change', show_all=show_all, **kwargs
        )
        return data

    def get_change_request(self, request_id):
        """Get given change request data.

        :param request_id: change request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/change/{request_id}')
        return json.get('data')

    def cancel_scheduled_change_request(self, request_id):
        """Cancel scheduled execution of a given change request.

        :param request_id: Change request id
        :type request_id: int
        :return: request status
        """
        payload = dict(scheduled=False)
        json = self.request(
            f'/request/change/{request_id}',
            payload=payload,
            method=self.PUT,
        )
        return json

    def reschedule_change_request(self, request_id, date_time):
        """Reschedule change request.

        :param request_id: Change request id
        :type request_id: int
        :param date_time: Timestamp with the following format
         ``%Y-%m-%d %H:%M``. If date is in the past, the change
         request will be processed right away, otherwise it will wait.
        :type date_time: str
        :return: request status

        """
        date_time_v = datetime.datetime.strptime(date_time, DATETIME_FMT)
        if self.debug:
            print(date_time_v)
        payload = dict(scheduled_datetime=date_time)
        json = self.request(
            f'/request/change/{request_id}',
            payload=payload,
            method=self.PUT,
        )
        return json

    def retry_change_request(self, request_id):
        """Retry given change request.

        Only if it has an "ERROR PROCESSED" status.

        :param request_id: new request id to get
        :type request_id: int
        :return: object
        """
        json = self.request(f'/request/change/{request_id}', method=self.PATCH)
        return json.get('data')

    def get_snapshot_requests(self, show_all=False, **kwargs):
        """Get snapshot requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_snapshot_request(filter='status,eq,PROCESSED',
                                    per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/snapshot', show_all=show_all, **kwargs
        )
        return data

    def get_snapshot_request(self, request_id, **kwargs):
        """Get given snapshot request data.

        :param request_id: snapshot request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/snapshot/{request_id}', params=kwargs)
        return json.get('data')

    def extend_snapshot_request(self, request_id, duration):
        """Extend valid snapshot request to a given number of hours.

        :param request_id: Snapshot request id
        :type request_id: int
        :param duration: new duration
        :type duration: int
        :return: tuple with status and new snapshot data

        """
        payload = dict(attribute='duration', value=duration)
        request = self.request(f'/request/snapshot/{request_id}')
        # check if lifetime is done
        if request.get('data').get('status') not in [
            RequestStatus.SCHEDULED.name
        ]:
            raise VssError('Only scheduled snapshot requests can be extended.')
        # update
        json = self.request(
            f'/request/snapshot/{request_id}',
            method=self.PUT,
            payload=payload,
        )
        # return
        return json.get('data')

    def get_inventory_requests(self, show_all=False, **kwargs):
        """Get inventory requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_inventory_requests(filter='transferred,eq,true',
                                       per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/inventory', show_all=show_all, **kwargs
        )
        return data

    def get_inventory_request(self, request_id, **kwargs):
        """Get given inventory request data.

        :param request_id: inventory request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/inventory/{request_id}', params=kwargs)
        return json.get('data')

    def get_export_requests(self, show_all=False, **kwargs):
        """Get virtual machine export requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_export_requests(filter='status,eq,PROCESSED',
                                    per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/export', show_all=show_all, **kwargs
        )
        return data

    def get_export_request(self, request_id, **kwargs):
        """Get given export request data.

        :param request_id: export request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/export/{request_id}', params=kwargs)
        return json.get('data')

    def get_folder_requests(self, show_all=False, **kwargs):
        """Get folder requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_folder_requests(filter='status,eq,PROCESSED',
                                    per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/folder', show_all=show_all, **kwargs
        )
        return data

    def get_folder_request(self, request_id, **kwargs):
        """Get given folder request data.

        :param request_id: folder request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/folder/{request_id}', params=kwargs)
        return json.get('data')

    def get_vmdk_sync_requests(self, show_all=False, **kwargs):
        """Get vmdk synchronization requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_vmdk_sync_requests(filter='status,eq,PROCESSED',
                                        per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/vmdk-sync', show_all=show_all, **kwargs
        )
        return data

    def get_vmdk_sync_request(self, request_id, **kwargs):
        """Get VMDK file synchronization request data.

        :param request_id: image synchronization request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/vmdk-sync/{request_id}', params=kwargs)
        return json.get('data')

    def get_image_sync_requests(self, show_all=False, **kwargs):
        """Get image synchronization requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://vss-wiki.eis.utoronto.ca/x/fACW>`__

        Example::

            vss.get_image_sync_requests(filter='status,eq,PROCESSED',
                                        per_page=100)

        """
        data = self._get_objects(
            pag_resource='/request/image_sync', show_all=show_all, **kwargs
        )
        return data

    def get_image_sync_request(self, request_id, **kwargs):
        """Get image synchronization request data.

        :param request_id: image synchronization request id to get
        :type request_id: int
        :return: object

        """
        json = self.request(f'/request/image_sync/{request_id}', params=kwargs)
        return json.get('data')

    # Domain management
    def get_domains(self, show_all=False, per_page=250, **kwargs):
        """Get available Fault Domains.

        :param show_all: Whether to show all items
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects
        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/domain', show_all=show_all, **kwargs
        )
        return data

    def get_domain(self, moref, **kwargs):
        """Get fault domain data.

        :param moref: managed object id
        :type moref: str
        :return: object

        """
        json = self.request('/domain/%s' % moref, params=kwargs)
        return json.get('data')

    def get_vms_by_domain(self, moref, **kwargs):
        """Get Virtual Machines on given Fault Domain.

        :param moref: Domain managed object id
        :type moref: str
        :return: list of  objects

        """
        json = self.request('/domain/%s/vm' % moref, params=kwargs)
        return json.get('data')

    # Content Library items
    def get_content_libraries(
        self, show_all: bool = False, per_page: int = 5, **kwargs
    ) -> Optional[List[Dict]]:
        """Get content libraries.

        :param show_all: Whether to show all items or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details.
        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/contentlib/library', show_all=show_all, **kwargs
        )
        return data

    def get_content_library_items(
        self, show_all: bool = False, per_page: int = 5, **kwargs
    ) -> Optional[List[Dict]]:
        """Get content library items.

        :param show_all: Whether to show all items or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details.
        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/contentlib/item', show_all=show_all, **kwargs
        )
        return data

    def get_content_library_vm_items(
        self, show_all: bool = False, per_page: int = 5, **kwargs
    ):
        """Get content library virtual machine template items.

        :param show_all: Whether to show all items or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects
        """
        _filter = ['type,eq,VM_TEMPLATE']
        if 'filter' in kwargs:
            _filter.append(kwargs['filter'])
            del kwargs['filter']
        return self.get_content_library_items(
            show_all=show_all,
            per_page=per_page,
            filter=';'.join(_filter),
            **kwargs,
        )

    def get_content_library_ovf_items(
        self, show_all: bool = False, per_page: int = 5, **kwargs
    ):
        """Get content library virtual machine OVF items.

        :param show_all: Whether to show all items or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects
        """
        _filter = ['type,eq,OVF']
        if 'filter' in kwargs:
            _filter.append(kwargs['filter'])
            del kwargs['filter']
        return self.get_content_library_items(
            show_all=show_all,
            per_page=per_page,
            filter=';'.join(_filter),
            **kwargs,
        )

    def get_content_library_iso_items(
        self, show_all: bool = False, per_page: int = 5, **kwargs
    ):
        """Get content library ISO items.

        :param show_all: Whether to show all items or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects
        """
        _filter = ['type,eq,ISO']
        if 'filter' in kwargs:
            _filter.append(kwargs['filter'])
            del kwargs['filter']
        return self.get_content_library_items(
            show_all=show_all,
            per_page=per_page,
            filter=';'.join(_filter),
            **kwargs,
        )

    def get_content_library_item(self, item_id: str) -> Optional[Dict]:
        """Get content library item.

        :param item_id: item identifier
        :type item_id: str
        :returns object
        """
        data = self.request(f'/contentlib/item/{item_id}')
        return data.get('data')

    # Image Management
    def get_images(self, show_all=False, per_page=250, **kwargs):
        """Get list of global OVA/OVF images.

        :param show_all: Whether to show all OVA/OVF VM images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `OVA/OVF Images <https://vss-wiki.eis.utoronto.ca/x/aAGC>`__

        Example::

            vss.get_images(filter='name,like,ub%', sort='name,asc')

            vss.get_images(filter='name,like,Win%', sort='path,desc')


        """
        kwargs.update({'per_page': per_page})
        resources = ['/image', '/user/image/vm']
        data = []
        for resource in resources:
            _data = self._get_objects(
                pag_resource=resource, show_all=show_all, **kwargs
            )
            if _data:
                data.extend(_data)
        return data

    # ISO Management
    def get_isos(self, show_all=False, per_page=250, **kwargs):
        """Get list of global and user iso images.

        :param show_all: Whether to show all ISO images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `ISO Images <https://vss-wiki.eis.utoronto.ca/x/IAGC>`__

        Example::

            vss.get_isos(filter='name,like,ub%', sort='name,asc')

            vss.get_isos(filter='name,like,Win%', sort='path,desc')


        """
        kwargs.update({'per_page': per_page})
        resources = ['/iso', '/user/image/iso']
        data = []
        for resource in resources:
            _data = self._get_objects(
                pag_resource=resource, show_all=show_all, **kwargs
            )
            if _data:
                data.extend(_data)
        return data

    # Floppy Management
    def get_floppies(self, show_all=False, per_page=250, **kwargs):
        """Get list of global and user floppy images.

        :param show_all: Whether to show all floppy images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per pege
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Floppy Images <https://vss-wiki.eis.utoronto.ca/x/OIC2>`__

        Example::

            vss.get_floppies(filter='name,like,pvscsi%')

        """
        kwargs.update({'per_page': per_page})
        resources = ['/floppy', '/user/image/floppy']
        data = []
        for resource in resources:
            _data = self._get_objects(
                pag_resource=resource, show_all=show_all, **kwargs
            )
            if _data:
                data.extend(_data)
        return data

    # Network Management
    def get_networks(self, show_all=False, per_page=250, **kwargs):
        """Get list of networks available for your account.

        :param show_all: Whether to show all items
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Networks <https://vss-wiki.eis.utoronto.ca/x/BQGC>`__

        Example::

            vss.get_networks(filter='name,like,%PUBLIC%', sort='name,asc')

            vss.get_networks(filter='vlan_id,eq,1234', sort='label,desc')


        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/network', show_all=show_all, **kwargs
        )
        return data

    def get_network(self, moref, **kwargs):
        """Get details of given network.

        :param moref: network managed object id
        :param kwargs: additional parameters

        :return: list of virtual machine objects

        """
        json = self.request(f'/network/{moref}', params=kwargs)
        return json.get('data')

    def get_vms_by_network(self, moref, **kwargs):
        """Get Virtual Machines on given network.

        :param moref: network managed object id
        :return: list of objects
        """
        json = self.request(f'/network/{moref}/vm', params=kwargs)
        return json.get('data')

    # Folder Management
    def get_folders(self, show_all=False, per_page=250, **kwargs):
        """Get list of folders available for your account.

        :param show_all: Whether to show all items
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Networks <https://vss-wiki.eis.utoronto.ca/x/rgGC>`__

        Example::

            vss.get_folders(filter='path,like,%Parent > MyFolder%',
                            sort='name,asc')

            vss.get_folders(filter='parent_moref,eq,group-v303',
                            sort='label,desc')

        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/folder', show_all=show_all, **kwargs
        )
        return data

    def get_folder(self, moref, **kwargs):
        """Get logical folder data.

        :param moref: managed object id
        :type moref: str

        :return: object
        """
        json = self.request('/folder/%s' % moref, params=kwargs)
        return json.get('data')

    def get_folder_children(self, moref, **kwargs):
        """Get children folders on given folder.

        :param moref: managed object id
        :return: list of objects
        """
        json = self.request('/folder/%s/children' % moref, params=kwargs)
        return json.get('data')

    def get_vms_by_folder(self, moref, **kwargs):
        """Get Virtual Machines on given folder.

        :param moref: managed object id
        :return: list of objects
        """
        json = self.request('/folder/%s/vm' % moref, params=kwargs)
        return json.get('data')

    def create_folder(self, moref, name):
        """Create logical folder under given managed object reference.

        :param moref: Parent folder managed object id
        :type moref: str
        :param name: New folder name
        :type name: str
        :return: folder request object
        """
        json_payload = dict(name=name)
        json = self.request(
            '/folder/%s' % moref, payload=json_payload, method=self.POST
        )
        return json.get('data')

    def delete_folder(self, moref):
        """Delete virtual machine folder.

        :param moref: Parent folder managed object id
        :type moref: str
        :return: folder request object
        """
        json = self.request('/folder/%s' % moref, method=self.DELETE)
        return json.get('data')

    def move_folder(self, moref, new_moref):
        """Move given folder to new parent.

        :param moref: folder to move managed object
         reference
        :param new_moref: target parent managed object
         reference to move folder to
        :return: folder request object
        """
        json_payload = dict(attribute='parent', value=new_moref)
        json = self.request(
            '/folder/%s' % moref, payload=json_payload, method=self.PUT
        )
        return json.get('data')

    def rename_folder(self, moref, name, **kwargs):
        """Rename given logical folder.

        :param moref: folder managed object id
        :param name: folder new name
        :return: folder request object
        """
        json_payload = dict(attribute='name', value=name)
        json_payload.update(kwargs)
        json = self.request(
            '/folder/%s' % moref, payload=json_payload, method=self.PUT
        )
        return json.get('data')

    # Virtual Machine Management
    def get_templates(self, show_all=False, per_page=250, **kwargs):
        """Get list of virtual machines templates available.

         :param show_all: Whether to show all items
         :type show_all: bool
         :param per_page: how many results per page
         :type per_page: int
         :return: list of objects

         .. note:: keyword arguments implement
           paging, filtering and sorting. Refer to the official
           documentation for further details. See
           `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        - **name**: filter by name
        - **folder.path**: filter by VM path (folder.path)

        :return: list of virtual machine template objects

        Example::

             vss.get_templates(filter='name,like,1%vm%',
                               sort='name,desc')
        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/template', show_all=show_all, **kwargs
        )
        return data

    def get_template(self, vm_id, **kwargs):
        """Get basic information of given virtual machine template.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str

        :return: object

        Virtual Machine attributes include:

        - storage
        - state
        - snapshot
        - note
        - devices
        - memory
        - cpu
        - guest
        - folder

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        json = self.request(f'/vm/{vm_id}', params=kwargs)
        return json.get('data')

    def get_vms(self, show_all=False, per_page=250, **kwargs):
        """Get list of virtual machines available.

         :param show_all: Whether to show all items
         :type show_all: bool
         :param per_page: how many results per page
         :type per_page: int
         :return: list of objects

         .. note:: keyword arguments implement
           paging, filtering and sorting. Refer to the official
           documentation for further details. See
           `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        - **hostname**: filter by main dns name
        - **ip_address**: filter by main ip address
        - **name**: filter by name
        - **path**: filter by VM path

        :return: list of virtual machine objects

        Example::

             vss.get_vms(filter='hostname,like,host%',
                         sort='name,asc')

             vss.get_vms(filter='name,like,1%vm%',
                         sort='name,desc')


        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(
            pag_resource='/vm', show_all=show_all, **kwargs
        )
        return data

    def get_vms_by_name(self, name, **kwargs):
        """Get Virtual machines by name.

        Wildcard symbol is ``%`` and can be added at any point in
        the string to search.

        :param name: string to search
        :param kwargs:
        :return: list of objects

        Example::

             vss.get_vms_by_name(name='%VMname%')

             vss.get_vms_by_name(name='%VMname%', sort='name,desc')

        """
        f = 'name,like,%s' % name
        data = self.get_vms(filter=f, **kwargs)
        return data

    def get_vms_by_hostname(self, hostname, **kwargs):
        """Get Virtual machine by Hostname.

        Wildcard symbol is ``%`` and can be added at any point in
        the string to search.

        :param hostname: string to search
        :param kwargs:
        :return: list of objects

        Example::

             vss.get_vms_by_hostname(hostname='%hostname%')

             vss.get_vms_by_hostname(hostname='%hostname.domain%',
                                     sort='name,desc')

        .. note:: VMware Tools must be running to query by hostname

        """
        f = 'hostname,like,%s' % hostname
        data = self.get_vms(filter=f, **kwargs)
        return data

    def get_vms_by_ip(self, ip_address, **kwargs):
        """Get Virtual machine by IP address.

        Wildcard symbol is ``%`` and can be added at any point in
        the string to search.

        :param ip_address: string to search
        :param kwargs:
        :return: list of objects

        Example::

             vss.get_vms_by_ip(ip_address='128.100%')

             vss.get_vms_by_ip(ip_address='128.100.31%',
                               sort='name,desc')

        .. note:: VMware Tools must be running to query by
          Ip address

        """
        f = 'ip_address,like,%s' % ip_address
        data = self.get_vms(filter=f, **kwargs)
        return data

    def get_vm(self, vm_id, **kwargs):
        """Get basic information of given virtual machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str

        :return: object

        Virtual Machine attributes include:

        - storage
        - state
        - snapshot
        - note
        - devices
        - memory
        - cpu
        - guest
        - folder

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        json = self.request(f'/vm/{vm_id}', params=kwargs)
        return json.get('data')

    def get_vm_spec(self, vm_id):
        """Get given virtual Machine specification.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        .. note:: useful to create a ``shell clone``

        """
        json = self.request(f'/vm/{vm_id}/spec')
        return json.get('data')

    def get_vm_name(self, vm_id):
        """Get given Virtual Machine full name.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object
        """
        json = self.request(f'/vm/{vm_id}/name')
        return json.get('data')

    def get_vm_state(self, vm_id):
        """Get given Virtual Machine state info.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        Virtual Machine attributes include:

        - boot_time
        - domain
        - connection_state
        - power_state

        """
        json = self.request(f'/vm/{vm_id}/state')
        return json.get('data')

    def update_vm_state(self, vm_id, state, **kwargs):
        """Update given Virtual Machine power state.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param state: Desired state
        :type state: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if state not in [
            'poweredOff',
            'poweredOn',
            'reset',
            'reboot',
            'shutdown',
            'suspend',
        ]:
            raise VssError(f'Unsupported {state} state')
        json_payload = dict(value=state)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/state',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_domain(self, vm_id):
        """Get domain where Virtual Machine is running.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object
        """
        json = self.request(f'/vm/{vm_id}/domain')
        return json.get('data')

    def update_vm_domain(
        self, vm_id, moref, power_on=False, force=False, **kwargs
    ):
        """Update fault domain of given VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param moref: Target domain managed object id
        :type moref: str
        :param power_on: Whether VM will be powered of after migration
        :type power_on: bool
        :param force: If set to True, VM will be powered off prior migration
        :type force: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. seealso:: :py:func:`get_domains` for domain parameter

        """
        valid_domain = self.get_domain(moref=moref)
        if self.debug:
            print(valid_domain)
        json_payload = dict(value=moref, poweron=power_on, force=force)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/domain',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    # Virtual Machine Configuration
    def get_vm_boot(self, vm_id):
        """Get given Virtual Machine boot configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: int
        :return: object

        Configuration includes:

        - enter_bios_setup
        - boot_retry_delayMs
        - boot_delay_ms

        .. note:: more information about required attributes available in
          `Virtual Machine Attributes
          <https://vss-wiki.eis.utoronto.ca/x/5ACC>`__

        """
        json = self.request(f'/vm/{vm_id}/boot')
        return json.get('data')

    def update_vm_boot_bios(self, vm_id, boot_bios, **kwargs):
        """Update boot to bios configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param boot_bios: Enable or disable
        :type boot_bios: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_boot(
            vm_id, attribute='bootbios', value=boot_bios, **kwargs
        )
        return json

    def update_vm_boot_delay(self, vm_id, boot_delay_ms, **kwargs):
        """Update boot bios delay configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param boot_delay_ms: boot delay in milliseconds
        :type boot_delay_ms: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_boot(
            vm_id, attribute='bootdelay', value=boot_delay_ms, **kwargs
        )
        return json

    def update_vm_boot(self, vm_id, attribute, value, **kwargs):
        """Update boot configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param attribute: Either boot bios or boot delay
        :param value: int or bool
        :return: change request object

        .. note:: keywords arguments include schedule to process request
          on a given date and time
        """
        if attribute not in ['bootbios', 'bootdelay']:
            raise VssError(f'Boot attribute {attribute} not supported')
        json_payload = dict(attribute=attribute, value=value)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/boot',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_os(self, vm_id):
        """Get Virtual Machine configured Operating System.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object
        """
        json = self.request(f'/vm/{vm_id}/os')
        return json.get('data')

    def update_vm_os(self, vm_id, os, **kwargs):
        """Update Virtual Machine Operating System configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param os: Operating system id.
        :type os: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        .. seealso:: :py:func:`get_os` for os parameter

        """
        json_payload = dict(value=os)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/os',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_folder(self, vm_id):
        """Get given Virtual Machine parent folder information.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        attributes include:

        - full_path
        - name
        - parent
        - reference to folder resource

        .. seealso:: :py:func:`get_folder` for further information
          about a given folder

        """
        json = self.request(f'/vm/{vm_id}/folder')
        return json.get('data')

    def update_vm_folder(self, vm_id, folder_moId, **kwargs):
        """Move VM into a given folder.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param folder_moId: folder managed object id
        :type folder_moId: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        folder = self.get_folder(moref=folder_moId)
        if self.debug:
            print(folder)
        json_payload = dict(value=folder_moId)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/folder',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_firmware(self, vm_id):
        """Get Virtual Machine firmware.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/firmware')
        return json.get('data')

    def validate_vm_firmware(self, n_type):
        """Validate supported firmware.

        :param n_type: firmware type
        :param n_type: str
        :return: str
        """
        if self.s_firmware_types is None:
            self.s_firmware_types = self.get_supported_firmware_types(
                only_type=True
            )
        return self.validate_options(n_type, self.s_firmware_types)

    def get_supported_firmware_types(self, only_type=True):
        """Get Virtual Machine Firmware types supported.

        :param only_type:
        :return:
        """
        if self.dry_run:
            data = VALID_VM_FIRMWARE_TYPE
        else:
            json = self.request('/vss/vm-firmware')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def update_vm_firmware(self, vm_id, firmware):
        """Update virtual machine firmware.

        :param vm_id: virtual machine moref or uuid.
        :param firmware: valid firmware setting.
        :return:
        """
        payload = dict(value=self.validate_vm_firmware(firmware))
        json = self.request(
            f'/vm/{vm_id}/firmware',
            method=self.PUT,
            payload=payload,
        )
        return json.get('data')

    def get_vm_version(self, vm_id):
        """Get Virtual Machine VMX version and upgrade policy status.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/version')
        return json.get('data')

    def get_supported_vmx_types(self, only_type=True):
        """Get Virtual Machine virtual hardware versions supported.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_VMX
        else:
            json = self.request('/vss/vmx')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def validate_vm_vmx_version(self, n_type):
        """Validate supported vmx version.

        :param n_type: Backing mode
        :param n_type: str
        :return: str
        """
        if self.s_vmx_versions is None:
            self.s_vmx_versions = self.get_supported_vmx_types(only_type=True)
        return self.validate_options(n_type, self.s_vmx_versions)

    def update_vm_version(self, vm_id, vmx, **kwargs):
        """Update virtual machine version (vmx-XX).

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param vmx: Virtual machine hardware version (vmx-XX)
        :type vmx: str
        :return: change request object
        """
        json_payload = dict(
            attribute='version', value=self.validate_vm_vmx_version(vmx)
        )
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/version',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_version_policy(self, vm_id, policy, **kwargs):
        """Update virtual machine hardware version upgrade policy.

        Policies are:
        - always: Always run scheduled upgrades.
        - never: No scheduled upgrades.
        - onSoftPowerOff: Run scheduled upgrades only on normal
         guest OS shutdown.


        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param policy: Virtual machine hardware upgrade version policy
        :type policy: str
        :return: change request object
        """
        json_payload = dict(attribute='upgrade_policy', value=policy)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/version',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    # Virtual Machine Guest
    def get_vm_guest(self, vm_id):
        """Get Virtual Machine guest operating system info.

        Including hostname, ip addresses, guest state, tools, etc.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/guest')
        return json.get('data')

    def get_vm_guest_os(self, vm_id):
        """Get Virtual Machine Guest Operating System.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/guest/os')
        return json.get('data')

    def run_cmd_guest_vm(self, vm_id, user, pwd, cmd, arg, **kwargs):
        """Execute command in Guest Operating System.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param user: Guest Operating Username
        :type user: str
        :param pwd: Guest Operating Username password
        :type pwd: str
        :param cmd: Command to execute
        :type cmd: str
        :param arg: Command arguments
        :type arg: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. note:: more information about required attributes
          available in `Virtual Machine Attributes
          <https://vss-wiki.eis.utoronto.ca/x/5ACC>`__

        """
        json_payload = {'user': user, 'pass': pwd, 'args': arg, 'cmd': cmd}
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/guest/cmd',
            method=self.POST,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_guest_process_id(self, vm_id, user, pwd, pid):
        """Get process id info.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param user: Guest Operating Username
        :type user: str
        :param pwd: Guest Operating Username password
        :type pwd: str
        :param pid: Process Id to query
        :type pid: int
        :return: list of objects

        .. note:: Processes running in the guest operating system can be listed
          using the API via VMware Tools. If VMware Tools has not been
          installed or is not running, this resource will not work properly.

        .. note:: more information about required attributes
          available in
          `Virtual Machine Attributes
          <https://vss-wiki.eis.utoronto.ca/x/5ACC>`__

        """
        json_payload = {'user': user, 'pass': pwd}
        json = self.request(
            f'/vm/{vm_id}/guest/cmd/{pid}',
            method=self.GET,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_guest_processes(self, vm_id, user, pwd):
        """Get virtual machine processes.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param user: Guest Operating Username
        :type user: str
        :param pwd: Guest Operating Username password
        :type pwd: str
        :return: list of objects

        .. note:: Processes running in the guest operating system can be listed
          using the API via VMware Tools. If VMware Tools has not been
          installed or is not running, this resource will not work properly.

        .. note:: more information about required attributes
          available in
          `Virtual Machine Attributes
          <https://vss-wiki.eis.utoronto.ca/x/5ACC>`__

        """
        json_payload = {'user': user, 'pass': pwd}
        json = self.request(
            f'/vm/{vm_id}/guest/cmd',
            method=self.GET,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_guest_ip(self, vm_id):
        """Get Virtual Machine IP and Mac addresses via VMware tools.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/guest/net/ip')
        return json.get('data')

    # VMWare Tools
    def get_vm_tools(self, vm_id):
        """Get VMware Tools status on given Virtual Machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        attributes include:

        - running_status
        - version
        - version_status
        """
        json = self.request(f'/vm/{vm_id}/guest/tools', method=self.GET)
        return json.get('data')

    def upgrade_vm_tools(self, vm_id, **kwargs):
        """Upgrade official VMware Tools version.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: This method fails if Guest OS is running
          an unmanaged distribution of VMware Tools.

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_tools(vm_id, 'upgrade', **kwargs)
        return json

    def mount_vm_tools(self, vm_id, **kwargs):
        """Mount official distribution of VMware Tools in Guest OS.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: This method fails if Guest OS is running
          an unmanaged distribution of VMware Tools.

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_tools(vm_id, 'mount', **kwargs)
        return json

    def unmount_vm_tools(self, vm_id, **kwargs):
        """Unmount official distribution of VMware Tools in Guest OS.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: This method fails if VMware Tools ISO is not
          mounted in guest OS

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_tools(vm_id, 'unmount', **kwargs)
        return json

    def update_vm_tools(self, vm_id, action, **kwargs):
        """Manage VMware tools on Virtual Machiene.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param action: Either mount, unmount or upgrade actions
        :type action: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if action not in ['mount', 'unmount', 'upgrade']:
            raise VssError(f'Unsupported {action} action')
        json_payload = dict(value=action)
        json_payload.update(kwargs)
        rv = self.request(
            f'/vm/{vm_id}/guest/tools',
            method=self.PUT,
            payload=json_payload,
        )
        return rv.get('data')

    # Virtual Machine Snapshot Management
    def has_vm_snapshot(self, vm_id):
        """Validate if Virtual Machine has snapshots.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: bool
        """
        rv = self.get_vm(vm_id)
        snapshot = rv.get('snapshot')
        return snapshot.get('exist')

    def create_vm_snapshot(
        self,
        vm_id: str,
        desc: str,
        date_time: Optional[str] = None,
        valid: Optional[int] = 24,
        consolidate: Optional[bool] = True,
        with_memory: Optional[bool] = True,
    ):
        """Create a Virtual Machine snapshot on a given date and time.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param desc: A brief description of the snapshot.
        :type desc: str
        :param date_time: Timestamp with the following format
         ``%Y-%m-%d %H:%M``. If date is in the past, the change
         request will be processed right away, otherwise it will wait.
         If date_time is None, the value is set to now.
        :type desc: str
        :param valid: Number of hours (max 72) the snapshot will live
        :type valid: int
        :param consolidate: Whether to consolidate when snapshot
         has been removed
        :type consolidate: bool
        :param with_memory: whether to include memory in snapshot
        :type with_memory: bool
        :return: snapshot request object

        """
        if date_time is None:
            date_time = datetime.datetime.now().strftime(DATETIME_FMT)
        date_time_v = datetime.datetime.strptime(date_time, DATETIME_FMT)
        if self.debug:
            print(date_time_v)
        # payload
        payload = dict(
            description=desc,
            from_date=date_time,
            valid_for=valid,
            consolidate=consolidate,
            with_memory=with_memory,
        )
        rv = self.request(
            f'/vm/{vm_id}/snapshot',
            method=self.POST,
            payload=payload,
        )
        return rv.get('data')

    def get_vm_snapshots(self, vm_id):
        """List existent Virtual Machine snapshots.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects

        """
        rv = self.request(f'/vm/{vm_id}/snapshot')
        return rv.get('data')

    def get_vm_snapshot(self, vm_id, snapshot):
        """Get given Virtual Machine Snapshot information.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param snapshot: Snapshot Id
        :type snapshot: int
        :return: object

        """
        rv = self.request(f'/vm/{vm_id}/snapshot/{snapshot}')
        return rv.get('data')

    def delete_vm_snapshot(self, vm_id, snapshot):
        """Delete given Virtual Machine snapshot.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param snapshot: Snapshot Id
        :type snapshot: int
        :return: snapshot request object

        """
        rv = self.request(
            f'/vm/{vm_id}/snapshot/{snapshot}',
            method=self.DELETE,
        )
        return rv.get('data')

    def revert_vm_snapshot(self, vm_id, snapshot):
        """Revert to given Virtual Machine snapshot.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param snapshot: Snapshot Id
        :type snapshot: int
        :return: snapshot request object

        """
        rv = self.request(
            f'/vm/{vm_id}/snapshot/{snapshot}',
            method=self.PATCH,
        )
        return rv.get('data')

    def get_vm_consolidation(self, vm_id):
        """Get current Virtual Machine disks consolidation state.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        rv = self.request(f'/vm/{vm_id}/snapshot/consolidate')
        return rv.get('data')

    def needs_consolidation(self, vm_id):
        """Check if Vm requires disk consolidation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: boolean
        """
        rv = self.get_vm_consolidation(vm_id)
        return rv['require_disk_consolidation']

    def consolidate_vm_disks(self, vm_id, **kwargs):
        """Submit a Virtual Machine disk consolidation request.

        :param vm_id: virtual machine moref or uuid
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict()
        payload.update(kwargs)
        rv = self.request(
            f'/vm/{vm_id}/snapshot/consolidate',
            method=self.PUT,
            payload=payload,
        )
        return rv.get('data')

    # Virtual Machine alarms
    def get_vm_alarms(self, vm_id):
        """Get Virtual Machine triggered Alarms.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects

        """
        json = self.request(f'/vm/{vm_id}/alarm')
        return json.get('data')

    def get_vm_alarm(self, vm_id, moref):
        """Get Virtual Machine triggered Alarm info.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param moref: Alarm managed object id
        :type moref: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/alarm/{moref}')
        return json.get('data')

    def clear_vm_alarm(self, vm_id, moref, **kwargs):
        """Clear given Virtual Machine alarm.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param moref: Virtual Machine Alarm managed object
                      reference
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        return self.update_vm_alarm(
            vm_id=vm_id, moref=moref, value='clear', **kwargs
        )

    def ack_vm_alarm(self, vm_id, moref, **kwargs):
        """Acknowledge given Virtual Machine triggered alarm.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param moref: Virtual Machine Alarm managed object
                      reference
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        return self.update_vm_alarm(
            vm_id=vm_id, moref=moref, value='ack', **kwargs
        )

    def update_vm_alarm(self, vm_id, moref, **kwargs):
        """Update given Virtual Machine triggered Alarm.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param moref: Virtual Machine Alarm managed object
         reference
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict()
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/alarm/{moref}',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    # Virtual Machine events
    def get_vm_events(self, vm_id, hours=1):
        """Query Virtual Machine events in vCenter.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param hours: Time window to get events from
        :type hours: int
        :return: list of events

        """
        event_uri = f'/event/{hours}' if hours > 1 else '/event'
        json = self.request(f'/vm/{vm_id}{event_uri}')
        return json.get('data')

    # Virtual Machine performance
    def get_vm_performance_cpu(self, vm_id):
        """Query Virtual Machine CPU performance counters.

        VM has to be powered On.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        Performance counters include:

        - readyAvgPct
        - readyMaxPct
        - usagePct

        """
        json = self.request(f'/vm/{vm_id}/performance/cpu')
        return json.get('data')

    def get_vm_performance_memory(self, vm_id):
        """Query Virtual Machine Memory performance counters.

        VM has to be powered On.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        Performance counters include:

        - activeMb
        - activePct
        - balloonMb
        - balloonPct
        - dateTime
        - name
        - sharedMb
        - sharedPct
        - swappedMb
        - swappedPct
        - usagePct

        """
        json = self.request(f'/vm/{vm_id}/performance/memory')
        return json.get('data')

    def get_vm_performance_io(self, vm_id):
        """Query Virtual Machine IO performance counters.

        VM has to be powered On.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        Performance counters include:

        - ioReadIops
        - ioWriteIops
        - latReadMs
        - latWriteMs

        """
        json = self.request(f'/vm/{vm_id}/performance/io')
        return json.get('data')

    def get_vm_performance_net(self, vm_id):
        """Query Virtual Machine Network performance counters.

        VM has to be powered On.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        Performance counters include:

        - rxErrors
        - rxMbps
        - txErrors
        - txMbps

        """
        json = self.request(f'/vm/{vm_id}/performance/net')
        return json.get('data')

    # Virtual Machine creation and deployment
    def export_vm(self, vm_id):
        """Export given Virtual Machine to OVF.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: export request object

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        .. note:: Once the export completes, will be transferred to
          VSKEY-STOR_

        """
        json = self.request(f'/vm/{vm_id}/export', method=self.POST)
        return json.get('data')

    def delete_vm(self, vm_id, force=False, prune=False):
        """Decommission given Virtual Machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param force: Force deletion if vm is on
        :type force: bool
        :param prune: Completely delete vm. Skip Trash folder.
        :type prune: bool
        :return: change request object

        """
        params = {}
        if self.is_powered_on_vm(vm_id=vm_id) and not force:
            raise VssError('VM is powered on. Please use force=True')
        # check if prune is set to true
        if prune:
            params['prune'] = 1
        json = self.request(f'/vm/{vm_id}', method=self.DELETE, params=params)
        return json.get('data')

    def delete_template(self, vm_id):
        """Decommission given Virtual Machine Template.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        """
        json = self.request(f'/template/{vm_id}', method=self.DELETE)
        return json.get('data')

    def create_vm(
        self,
        os: str,
        built: str,
        client: str,
        description: str,
        folder: str,
        networks: List[Dict],
        disks: Union[List[int], List[Dict]],
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        name: Optional[str] = None,
        iso: Optional[str] = None,
        notes: Optional[Dict] = None,
        usage: Optional[str] = 'Test',
        cpu: Optional[Union[int, Dict]] = 1,
        memoryGB: int = 1,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Create single Virtual Machine.

        :param os: Operating system id.
        :type os: str
        :param built: built process
        :param client: Client department
        :type client: str
        :param description: VM description
        :type description: str
        :param folder: Target VM folder moref
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param name: name of the new virtual machine
        :type name: str
        :param iso: ISO image path to be mounted after creation
        :type iso: str
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage
        :type usage: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}


        :type cpu: int, dict
        :param memoryGB: Memory size in GB
        :type memoryGB: int
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs: key value arguments
        :return: new request object

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks,
          :py:func:`get_vss_services` for vss_service,
          :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec` for retirement.

        .. note:: more information about required attributes
          available in `Virtual Machine
          <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        # validate input
        usage = self.validate_usage(usage)
        built_from = self.validate_build_process(built)
        assert self.get_folder(folder), 'Invalid folder moref'
        # check disks input and create payload
        disks = disks if disks else [40]
        _disks = self.validate_disks(disks)
        # check network input and allow backwards compat
        _networks = self.validate_networks(networks)
        # generating payload
        payload = dict(
            os=os,
            built_from=built_from,
            client=client,
            cpu=cpu,
            memory=memoryGB,
            usage=usage,
            description=description,
            folder=folder,
            networks=_networks,
            disks=_disks,
            power_on=power_on,
            template=template,
        )
        if scsi:
            payload['scsi'] = self.validate_scsi(scsi)
        if name:
            payload['name'] = name
        if notes:
            payload['notes'] = notes
        if iso:
            self.get_isos(filter='path,eq,iso')
            payload['iso'] = iso
        if vss_service:
            payload['vss_service'] = vss_service
        if extra_config:
            payload['extra_config'] = extra_config
        if firmware:
            payload['firmware'] = self.validate_vm_firmware(firmware)
        if retirement:
            payload['retirement'] = retirement
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    def create_vms(
        self,
        count: int,
        name: str,
        os: str,
        built: str,
        client: str,
        description: str,
        folder: str,
        networks: List[Dict],
        disks: Union[List[int], List[Dict]],
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        iso: Optional[str] = None,
        notes: Optional[Dict] = None,
        usage: str = 'Test',
        cpu: Optional[Union[int, Dict]] = 1,
        memoryGB: int = 1,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Create multiple Virtual Machines.

        Names are generated by appending ``name_number``.

        :param count: number of virtual machines to deploy
        :type count: int
        :param name: name of the new virtual machines
        :type name: str
        :param os: Operating system id.
        :type os: str
        :param built: built process
        :param client: Client department
        :type client: str
        :param description: Brief description of what the virtual
          machine will host.
        :type description: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param iso: ISO image path to be mounted after creation
        :type iso: str
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage
        :type usage: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memoryGB: Memory size in GB. Defaults to 1GB
        :type memoryGB: int
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks,
          :py:func:`get_vss_services` for vss_service..

        .. note:: more information about required attributes
          available in `Virtual Machine
          <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        # validate basic items
        usage = self.validate_usage(usage)
        built_from = self.validate_build_process(built)
        disks = disks if disks else [40]
        assert self.get_folder(folder), 'Invalid folder moref'
        _networks = self.validate_networks(networks)
        names = [f'{name}_{i}' for i in range(0, count)]
        # generating payload
        payload = dict(
            os=os,
            built_from=built_from,
            client=client,
            cpu=cpu,
            memory=memoryGB,
            usage=usage,
            description=description,
            folder=folder,
            names=names,
            disks=disks,
            networks=_networks,
            power_on=power_on,
            template=template,
        )
        if scsi:
            payload['scsi'] = self.validate_scsi(scsi)
        if notes:
            payload['notes'] = notes
        if iso:
            self.get_isos(filter='path,eq,iso')
            payload['iso'] = iso
        if vss_service:
            payload['vss_service'] = vss_service
        if extra_config:
            payload['extra_config'] = extra_config
        if firmware:
            payload['firmware'] = self.validate_vm_firmware(firmware)
        if retirement:
            payload['retirement'] = retirement
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    def create_vm_from_image(
        self,
        os: str,
        image: str,
        client: str,
        description: str,
        folder: str,
        networks: List[Dict],
        disks: Union[List[int], List[Dict]],
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        notes: Optional[Dict] = None,
        usage: str = 'Test',
        name: Optional[str] = None,
        cpu: Optional[Union[int, Dict]] = 1,
        memoryGB: Optional[int] = 1,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Create a new Virtual Machine from OVA or OVF.

        :param os: Operating system id.
        :type os: str
        :param image: OVA/OVF filename
        :type image: str
        :param client: Client department
        :type client: str
        :param description: Brief description of what the virtual
          machine will host.
        :type description: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. Defaults to Test
        :type usage: str
        :param name: Virtual Machine name. If not set, will be generated
         dynamically by the API
        :type name: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memoryGB: Memory size in GB. Defaults to 1GB
        :type memoryGB: int
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks,
          :py:func:`get_vss_services` for vss_service.

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        # validate basic items
        usage = self.validate_usage(usage)
        assert self.get_folder(folder), 'Invalid folder moref'
        disks = disks if disks else [40]
        _disks = self.validate_disks(disks)
        _networks = self.validate_networks(networks)
        # generate payload
        payload = dict(
            os=os,
            cpu=cpu,
            memory=memoryGB,
            built_from='image',
            client=client,
            description=description,
            folder=folder,
            networks=_networks,
            disks=_disks,
            source_image=image,
            usage=usage,
            power_on=power_on,
            template=template,
        )
        if scsi:
            payload['scsi'] = self.validate_scsi(scsi)
        if name:
            payload['name'] = name
        if notes:
            payload['notes'] = notes
        if vss_service:
            payload['vss_service'] = vss_service
        if extra_config:
            payload['extra_config'] = extra_config
        if firmware:
            payload['firmware'] = self.validate_vm_firmware(firmware)
        if retirement:
            payload['retirement'] = retirement
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    def create_vm_from_clone(
        self,
        source: str,
        description: str,
        name: Optional[str] = None,
        os: Optional[str] = None,
        client: Optional[str] = None,
        folder: Optional[str] = None,
        networks: Optional[List[Dict]] = None,
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        disks: Optional[Union[List[int], List[Dict]]] = None,
        notes: Optional[Dict] = None,
        usage: Optional[str] = None,
        cpu: Optional[Union[int, Dict]] = None,
        memoryGB: Optional[int] = None,
        custom_spec: Optional[Dict] = None,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        firmware: Optional[str] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        source_snap_id: Optional[int] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Deploy virtual machine by cloning from any given source.

        :param source: Source virtual machine moref or uuid
        :type source: str
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param name: Virtual machine name. If not specified, will
         create a new name based on source
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param client: client department. If not specified, will be
         same as source.
        :type client: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools must be installed on
         the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param source_snap_id: source virtual machine snapshot identifier.
         :py:func:`get_vm_snapshots`. If set, clone will be a result from the
         given snapshot id state.
        :type source_snap_id: int
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_templates` for virtual machine templates
          :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification, :py:func:`get_vss_services`
          for vss_service.

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        # get source virtual machine specification
        source_vm_spec = self.get_vm_spec(source)
        # new vm specification
        new_vm_spec = dict(
            description=description,
            built_from='clone',
            source_vm=source,
            power_on=power_on,
            template=template,
        )
        new_vm_spec['name'] = (
            name if name else '{}-clone'.format(source_vm_spec['name'])
        )
        # set valid and not none params in new spec
        new_vm_spec['os'] = os if os else source_vm_spec['os']
        new_vm_spec['disks'] = (
            self.validate_disks(disks) if disks else source_vm_spec['disks']
        )
        new_vm_spec['scsi'] = (
            self.validate_scsi(scsi) if scsi else source_vm_spec['scsi']
        )
        new_vm_spec['cpu'] = cpu if cpu else source_vm_spec['cpu']
        new_vm_spec['memory'] = (
            memoryGB if memoryGB else source_vm_spec['memory']
        )
        new_vm_spec['usage'] = (
            self.validate_usage(usage) if usage else source_vm_spec['usage']
        )
        # client
        if client:
            new_vm_spec['client'] = client
        # folder
        if folder:
            self.get_folder(folder)
            new_vm_spec['folder'] = folder
        # network adapters
        if networks:
            new_vm_spec['networks'] = self.validate_networks(networks)
        # client notes
        if notes:
            new_vm_spec['notes'] = notes
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        # vss_service
        if vss_service:
            new_vm_spec['vss_service'] = vss_service
        # validate service from source even if not included
        if 'vss_service' in source_vm_spec:
            if not source_vm_spec['vss_service']:
                del source_vm_spec['vss_service']
        # extra_config
        if source_vm_spec.get('extra_config') or extra_config:
            _extra_cfg = (
                extra_config
                if extra_config
                else self._process_extra_cfg(
                    source_vm_spec.get('extra_config')
                )
            )
            if _extra_cfg:
                new_vm_spec['extra_config'] = _extra_cfg
        else:
            if 'extra_config' in source_vm_spec:
                del source_vm_spec['extra_config']
        if firmware:
            new_vm_spec['firmware'] = self.validate_vm_firmware(firmware)
        if source_snap_id:
            new_vm_spec['source_vm_snap_id'] = source_snap_id
        if retirement:
            new_vm_spec['retirement'] = retirement
        # creating payload
        payload = source_vm_spec
        # overriding source spec with new vm spec
        payload.update(new_vm_spec)
        # update any additional k-v args
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    def create_vms_from_clone(
        self,
        source: str,
        description: str,
        count: int = 1,
        name: Optional[str] = None,
        os: Optional[str] = None,
        client: Optional[str] = None,
        folder: Optional[str] = None,
        networks: Optional[List[Dict]] = None,
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        disks: Optional[Union[List[int], List[Dict]]] = None,
        notes: Optional[Dict] = None,
        usage: Optional[str] = None,
        cpu: Optional[Union[int, Dict]] = None,
        memoryGB: Optional[int] = None,
        custom_spec: Optional[Dict] = None,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        source_snap_id: Optional[int] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Deploy multiple or a single VM from a source VM.

        Useful when you need to deploy multiple virtual machine instances
        from a single source. Not recommended when using `custom_spec` for
        guest OS customization specification.

        Use :py:func:`create_vm_from_clone` in a loop for deploying multiple
        virtual machines with different `custom_spec`.

        :param source: Source virtual machine moref or uuid (powered off)
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param count: Number or virtual machines to deploy. Defaults
         to 1.
        :param name: Virtual machine name. If not specified, will
         create all new virtual machines based on source VM name
         appending the number of item.
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param client: client department. If not specified, will be
         same as source.
        :type client: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools and Perl must be
         installed on the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param source_snap_id: source virtual machine snapshot identifier.
         :py:func:`get_vm_snapshots`. If set, clone will be a result from the
         given snapshot id state.
        :type source_snap_id: int
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_vms` for virtual machine
          :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification, :py:func:`get_vss_services`
          for vss_service.

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        assert self.is_powered_off_vm(source), (
            'Source is powered ON. '
            'Multiple Vm deployment from a vm can only be '
            'performed while powered OFF'
        )
        # get source virtual machine specification
        source_spec = self.get_vm_spec(source)
        if name:
            names = (
                [f'{name}_{i}' for i in range(1, count + 1)]
                if count > 1
                else [name]
            )
        else:
            names = [f"{source_spec['name']}_{i}" for i in range(1, count + 1)]
        new_vms_spec = dict(
            description=description,
            built_from='clone',
            names=names,
            source_vm=source,
            power_on=power_on,
            template=template,
        )
        # set valid and not none params in new spec
        new_vms_spec['os'] = os if os else source_spec['os']
        new_vms_spec['scsi'] = (
            self.validate_scsi(scsi) if scsi else source_spec['scsi']
        )
        new_vms_spec['disks'] = (
            self.validate_disks(disks) if disks else source_spec['disks']
        )
        new_vms_spec['cpu'] = cpu if cpu else source_spec['cpu']
        new_vms_spec['memory'] = (
            memoryGB if memoryGB else source_spec['memory']
        )
        new_vms_spec['usage'] = (
            self.validate_usage(usage) if usage else source_spec['usage']
        )
        # client
        if client:
            new_vms_spec['client'] = client
        # folder
        if folder:
            self.get_folder(folder)
            new_vms_spec['folder'] = folder
        # network adapters
        if networks:
            new_vms_spec['networks'] = self.validate_networks(networks)
        # client notes
        if notes:
            new_vms_spec['notes'] = notes
        # customization specification
        if custom_spec:
            new_vms_spec['custom_spec'] = custom_spec
        # vss_service
        if vss_service:
            new_vms_spec['vss_service'] = vss_service
        # validate service from source even if not included
        if 'vss_service' in source_spec:
            if not source_spec['vss_service']:
                del source_spec['vss_service']
        # extra_config
        if source_spec.get('extra_config') or extra_config:
            _extra_cfg = (
                extra_config
                if extra_config
                else self._process_extra_cfg(source_spec.get('extra_config'))
            )
            if _extra_cfg:
                new_vms_spec['extra_config'] = _extra_cfg
        else:
            if 'extra_config' in source_spec:
                del source_spec['extra_config']
        if firmware:
            new_vms_spec['firmware'] = self.validate_vm_firmware(firmware)
        if source_snap_id:
            new_vms_spec['source_vm_snap_id'] = source_snap_id
        if retirement:
            new_vms_spec['retirement'] = retirement
        # creating payload
        payload = source_spec
        # overriding source spec with new vm spec
        payload.update(new_vms_spec)
        # update any additional k-v args
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    @staticmethod
    def payload_deprecation_warn(payload: Dict) -> Dict:
        """Process deprecation warnings."""
        if 'memoryGB' in payload:
            warnings.warn(
                "memoryGB will be deprecated in version"
                " 0.19.0, use memory_gb instead",
                PendingDeprecationWarning,
            )
            payload['memory_gb'] = payload['memoryGB']
            del payload['memoryGB']
        return payload

    def deploy_vm_from_clib_item(
        self,
        item_id: str,
        os: str,
        client: str,
        description: str,
        folder: str,
        networks: List[Dict],
        disks: Union[List[int], List[Dict]],
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        notes: Optional[Dict] = None,
        usage: Optional[str] = 'Test',
        name: Optional[str] = None,
        cpu: Optional[Union[int, Dict]] = 1,
        memory_gb: Optional[int] = 1,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        additional_parameters: Optional[Dict] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Deploy virtual machine from content library item.

        :param item_id: Content library deployable item id.
          :py:func:`get_content_library_vm_items` or
          :py:func:`get_content_library_ovf_items` or
        :type item_id: str
        :param os: Operating system id.
        :type os: str
        :param client: Client department
        :type client: str
        :param description: Brief description of what the virtual
          machine will host.
        :type description: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. Defaults to Test
        :type usage: str
        :param name: Virtual Machine name. If not set, will be generated
         dynamically by the API
        :type name: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memory_gb: Memory size in GB. Defaults to 1GB
        :type memory_gb: int
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param additional_parameters: Set OVF parameters or deployment options.
         These options are included in the OVF descriptor `<ProductSection/>`
         and are mapped based on the `ovf:key` attribute.
         Each property can be injected via a dictionary of `PropertyParams`
         and `DeploymentOptionParams` keys. The following example applies
         for an Ubuntu Cloud image:

         Example::

            {
             "PropertyParams": {
               "hostname": "ubuntu-web",
               "public-keys": "ssh-rsa ...",
               "user-data": "IyEvYmluL3NoCmVjaG8gImhpIHdvcmxkIgo=",
               "password": "RANDOM"
              }
             }

        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks,
          :py:func:`get_vss_services` for vss_service.

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        assert self.is_deployable_item(
            item_id
        ), 'Source is not a deployable item.'
        usage = self.validate_usage(usage)
        assert self.get_folder(folder), 'Invalid folder moref'
        disks = disks if disks else [40]
        _disks = self.validate_disks(disks)
        _networks = self.validate_networks(networks)
        # generate payload
        payload = dict(
            os=os,
            cpu=cpu,
            memory=memory_gb,
            built_from='contentlib',
            client=client,
            description=description,
            folder=folder,
            networks=_networks,
            disks=_disks,
            source_clib=item_id,
            usage=usage,
            power_on=power_on,
            template=template,
        )
        # add deprecation warnings (if any)
        payload = VssManager.payload_deprecation_warn(payload)
        if scsi:
            payload['scsi'] = self.validate_scsi(scsi)
        if name:
            payload['name'] = name
        if notes:
            payload['notes'] = notes
        if vss_service:
            payload['vss_service'] = vss_service
        if extra_config:
            payload['extra_config'] = extra_config
        if additional_parameters:
            payload['additional_parameters'] = additional_parameters
        if firmware:
            payload['firmware'] = self.validate_vm_firmware(firmware)
        if retirement:
            payload['retirement'] = retirement
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    def deploy_vm_from_template(
        self,
        source_template: str,
        description: str,
        name: Optional[str] = None,
        os: Optional[str] = None,
        client: Optional[str] = None,
        folder: Optional[str] = None,
        networks: Optional[List[Dict]] = None,
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        disks: Optional[Union[List[int], List[Dict]]] = None,
        notes: Optional[Dict] = None,
        usage: Optional[str] = None,
        cpu: Optional[Union[int, Dict]] = 1,
        memoryGB: Optional[int] = None,
        custom_spec: Optional[Dict] = None,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        retirement: Optional[str] = None,
        **kwargs,
    ):
        """Deploy single virtual machine from template.

        Recommended approach for multiple virtual machine deployment
        from template with independent specification, including
        `custom_spec` configuration.

        :param source_template: Source virtual machine template
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param name: Virtual machine name. If not specified, will
         create new virtual machine based on source template name
         appending the -clone suffix.
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param client: client department. If not specified, will be
         same as source.
        :type client: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :type disks: list
        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools and Perl must be
         installed on the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_templates` for virtual machine templates
          :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification, :py:func:`get_vss_services`
          for vss_service.

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        assert self.is_vm_template(source_template).get(
            'is_template'
        ), 'Source is not a template'
        # get source virtual machine specification
        source_template_spec = self.get_vm_spec(source_template)
        new_vm_spec = dict(
            description=description,
            built_from='template',
            source_template=source_template,
            power_on=power_on,
            template=template,
        )
        # set valid and not none params in new spec
        new_vm_spec['name'] = (
            name if name else '{}-clone'.format(source_template_spec['name'])
        )
        new_vm_spec['os'] = os if os else source_template_spec['os']
        new_vm_spec['scsi'] = (
            self.validate_scsi(scsi) if scsi else source_template_spec['scsi']
        )
        new_vm_spec['disks'] = (
            self.validate_disks(disks)
            if disks
            else source_template_spec['disks']
        )
        new_vm_spec['cpu'] = cpu if cpu else source_template_spec['cpu']
        new_vm_spec['memory'] = (
            memoryGB if memoryGB else source_template_spec['memory']
        )
        new_vm_spec['usage'] = (
            self.validate_usage(usage)
            if usage
            else source_template_spec['usage']
        )
        # client
        if client:
            new_vm_spec['client'] = client
        # folder
        if folder:
            self.get_folder(folder)
            new_vm_spec['folder'] = folder
        # network adapters
        if networks:
            new_vm_spec['networks'] = self.validate_networks(networks)
        # client notes
        if notes:
            new_vm_spec['notes'] = notes
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        # vss_service
        if vss_service:
            new_vm_spec['vss_service'] = vss_service
        # validate service from source even if not included
        if 'vss_service' in source_template_spec:
            if not source_template_spec['vss_service']:
                del source_template_spec['vss_service']
        # extra_config
        if source_template_spec.get('extra_config') or extra_config:
            _extra_cfg = (
                extra_config
                if extra_config
                else self._process_extra_cfg(
                    source_template_spec.get('extra_config')
                )
            )
            if _extra_cfg:
                new_vm_spec['extra_config'] = _extra_cfg
        else:
            if 'extra_config' in source_template_spec:
                del source_template_spec['extra_config']
        if firmware:
            new_vm_spec['firmware'] = self.validate_vm_firmware(firmware)
        if retirement:
            new_vm_spec['retirement'] = retirement
        # creating payload
        payload = source_template_spec
        # overriding source spec with new vm spec
        payload.update(new_vm_spec)
        # update any additional k-v args
        payload.update(kwargs)
        json = self.request('/vm', payload=payload, method=self.POST)
        return json.get('data')

    def deploy_vms_from_template(
        self,
        source_template: str,
        description: str,
        count: int = 1,
        name: Optional[str] = None,
        os: Optional[str] = None,
        client: Optional[str] = None,
        folder: Optional[str] = None,
        networks: Optional[List[Dict]] = None,
        disks: Optional[Union[List[int], List[Dict]]] = None,
        scsi: Optional[Union[List[str], List[Dict]]] = None,
        notes: Optional[Dict] = None,
        usage: Optional[str] = None,
        cpu: Optional[Union[int, Dict]] = 1,
        memoryGB: Optional[int] = None,
        custom_spec: Optional[Dict] = None,
        vss_service: Optional[str] = None,
        extra_config: Optional[List[Dict]] = None,
        power_on: Optional[bool] = False,
        template: Optional[bool] = False,
        firmware: Optional[str] = None,
        retirement: Optional[Dict] = None,
        **kwargs,
    ):
        """Deploy multiple or a single virtual machine from template.

        Useful when you need to deploy multiple virtual machine instances
        from a single source. Not recommended when using `custom_spec` for
        guest OS customization specification.

        Use :py:func:`deploy_vm_from_template` in a loop for deploying multiple
        virtual machines with different `custom_spec`.

        :param source_template: Source virtual machine template
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param count: Number or virtual machines to deploy. Defaults
         to 1.
        :param name: Virtual machine name. If not specified, will
         create all new virtual machines based on source template name
         appending the number of item.
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param client: client department. If not specified, will be
         same as source.
        :type client: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of network adapter objects
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.

        Example::

            {'network': 'moref', 'type': 'valid_type'}

        :type networks: list
        :param disks: list of disk sizes in gb or list of disk
         specification including `capacity_gb`, `backing_mode` and
         `backing_sharing`.

         Example::

            {"capacity_gb": 100, "backing_mode": "persistent"}
            {"capacity_gb": 500, "backing_mode": "independent_persistent"}

        :param scsi: list of scsi controllers types or list of scsi
         specification including `type`, `bus` and `sharing`.

         Example::

            {"type": "lsilogic", "bus": 0}
            {"type": "paravirtual", "bus": 1}

        :type scsi: list
        :type disks: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count or count and core per socket configuration

         Example::

            {"count": 4, "cores_per_socket": 2}

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cpu: int, dict
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools and Perl must be
         installed on the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param vss_service: VSS Service definition.
        :type vss_service: str or int
        :param extra_config: Set VMware **guestinfo** interface
         which are available to the VM guest operating system via VMware Tools
         These properties are stored within the VMX prefixed with "guestinfo."
         string. This parameter also can include supported properties available
         from :py:func:`get_supported_extra_cfg_options`.
        :type extra_config: list
        :param power_on: Power on virtual machine after successful deployment
        :type power_on: bool
        :param template: Mark resulting vm as template.
        :type template: bool
        :param firmware: type of firmware to use. Supported types are available
         :py:func:`get_supported_firmware_types`.
        :type firmware: str
        :param retirement: vm retirement payload. Expected
         either :py:func:`get_retirement_datetime_spec` or
         :py:func:`get_retirement_timedelta_spec`.
        :type retirement: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_templates` for virtual machine templates
          :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification, :py:func:`get_vss_services`
          for vss_service.

        .. note:: more information about required attributes
          available in
          `Virtual Machine <https://vss-wiki.eis.utoronto.ca/x/pgCC>`__

        """
        assert self.is_vm_template(source_template).get(
            'is_template'
        ), 'Source is not a template'
        # get source virtual machine specification
        source_template_spec = self.get_vm_spec(source_template)
        if name:
            names = (
                [f'{name}_{i}' for i in range(1, count + 1)]
                if count > 1
                else [name]
            )
        else:
            names = [
                f"{source_template_spec['name']}_{i}"
                for i in range(1, count + 1)
            ]

        new_vms_spec = dict(
            description=description,
            built_from='template',
            names=names,
            source_template=source_template,
            power_on=power_on,
            template=template,
        )
        # set valid and not none params in new spec
        new_vms_spec['os'] = os if os else source_template_spec['os']
        new_vms_spec['scsi'] = (
            self.validate_scsi(scsi) if scsi else source_template_spec['scsi']
        )
        new_vms_spec['disks'] = (
            self.validate_disks(disks)
            if disks
            else source_template_spec['disks']
        )
        new_vms_spec['cpu'] = cpu if cpu else source_template_spec['cpu']
        new_vms_spec['memory'] = (
            memoryGB if memoryGB else source_template_spec['memory']
        )
        new_vms_spec['usage'] = (
            self.validate_usage(usage)
            if usage
            else source_template_spec['usage']
        )
        # client
        if client:
            new_vms_spec['client'] = client
        # folder
        if folder:
            self.get_folder(folder)
            new_vms_spec['folder'] = folder
        # network adapters
        if networks:
            new_vms_spec['networks'] = self.validate_networks(networks)
        # client notes
        if notes:
            new_vms_spec['notes'] = notes
        # customization specification
        if custom_spec:
            new_vms_spec['custom_spec'] = custom_spec
        # vss_service
        if vss_service:
            new_vms_spec['vss_service'] = vss_service
        # validate service from source even if not included
        if 'vss_service' in source_template_spec:
            if not source_template_spec['vss_service']:
                del source_template_spec['vss_service']
        # extra_config
        if source_template_spec.get('extra_config') or extra_config:
            _extra_cfg = (
                extra_config
                if extra_config
                else self._process_extra_cfg(
                    source_template_spec.get('extra_config')
                )
            )
            if _extra_cfg:
                new_vms_spec['extra_config'] = _extra_cfg
        else:
            if 'extra_config' in source_template_spec:
                del source_template_spec['extra_config']
        if firmware:
            new_vms_spec['firmware'] = self.validate_vm_firmware(firmware)
        if retirement:
            new_vms_spec['retirement'] = retirement
        # creating payload
        json_payload = source_template_spec
        # overriding source spec with new vm spec
        json_payload.update(new_vms_spec)
        # update any additional k-v args
        json_payload.update(kwargs)
        json = self.request('/vm', payload=json_payload, method=self.POST)
        return json.get('data')

    def create_vm_custom_spec(self, vm_id, custom_spec, **kwargs):
        """
        Create a custom specification for a given virtual machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools must be installed on
         the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param kwargs:
        :return:

        .. note:: Virtual machine must be powered on and VMware Tools must
          be installed.

        .. seealso:: :py:func:`get_custom_spec` for
          customization specification.

        """
        json = self.request(
            f'/vm/{vm_id}/custom_spec',
            method=self.POST,
            payload=custom_spec,
            **kwargs,
        )
        return json.get('data')

    def get_vm_console(self, vm_id, auth=None, client='flash'):
        """Produce a one-time URL to Virtual Machine console.

        Virtual machine has to be powered on and user must have a valid vCenter
        session (limitation in the vSphere SOAP API).

        Example::

            vss.get_vm_console(vm_id, auth=(username, password))


        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param auth: username and password
        :type auth: tuple
        :param client: What client: choose between **flash (default)**
         **html5** or **vmrc**.
        :type client: str
        :return: object
        """
        kwargs = dict()
        params = dict(client=client)
        if auth:
            username_u, password_u = auth
            _auth = HTTPBasicAuth(username_u, password_u)
            kwargs['auth'] = _auth
        json = self.request(f'/vm/{vm_id}/console', params=params, **kwargs)
        return json.get('data')

    def get_vm_vsphere_link(self, vm_id, **kwargs):
        """Produce an URL to the vSphere client on the given VM view.

        Example::

            vss.get_vm_vsphere_link('vm-123')

        :param vm_id: virtual machine identifier
        :type vm_id: str
        :param kwargs:
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/vcenter', **kwargs)
        return json.get('data')

    def is_deployable_item(self, item_id: str) -> bool:
        """Verify if item is deployable.

        :param item_id: content library content id
        :type item_id: str
        :return: bool
        """
        item = self.get_content_library_item(item_id)
        if item is not None:
            if item.get('type') in ['OVF', 'VM_TEMPLATE']:
                return True
        return False

    def is_vm_template(self, vm_id):
        """Check if Virtual Machine is marked as template.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: bool
        """
        json = self.request(f'/vm/{vm_id}/template')
        return json.get('data')

    def mark_vm_as_template(self, vm_id, **kwargs):
        """Mark Virtual Machine as template to freeze changes.

        Templates cannot be modified nor powered on unless marked
        as Virtual Machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=True)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/template',
            payload=json_payload,
            method=self.PUT,
        )
        return json.get('data')

    def mark_template_as_vm(self, vm_id, **kwargs):
        """Mark Template as Virtual Machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=False)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/template',
            payload=json_payload,
            method=self.PUT,
        )
        return json.get('data')

    def get_vm_memory(self, vm_id):
        """Get Virtual Machine memory information.

        Attributes like:
        - memory_gb
        - hot_add
        - quick_stats:
        - ballooned
        - compressed
        - consumed_overhead,
        - private
        - shared
        - swapped

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/memory')
        return json.get('data')

    def get_vm_memory_config(self, vm_id):
        """Get VM memory configuration.

        Attributes included:
        - hot_add
        - limit_gb

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object
        """
        json = self.request(f'/vm/{vm_id}/memory/config')
        return json.get('data')

    def update_vm_memory_hot_add(self, vm_id, hot_add, **kwargs):
        """Update Virtual Machine Memory hot add configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param hot_add: Enable or disable hot add
        :type hot_add: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(attribute='hotAdd', value=hot_add)
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/memory/config',
            payload=payload,
            method=self.PUT,
        )
        return json.get('data')

    def enable_vm_memory_hot_add(self, vm_id, **kwargs):
        """Enable virtual machine Memory hot add.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_memory_hot_add(vm_id, True, **kwargs)
        return json.get('data')

    def disable_vm_memory_hot_add(self, vm_id, **kwargs):
        """Disable virtual machine Memory hot add.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_memory_hot_add(vm_id, False, **kwargs)
        return json.get('data')

    def set_vm_memory(self, vm_id, sizeGB, **kwargs):
        """Update Virtual Machine Memory size.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param sizeGB: New memory size in GB
        :type sizeGB: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
         on a given date and time

        """
        payload = dict(value=int(sizeGB))
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/memory',
            payload=payload,
            method=self.PUT,
        )
        return json.get('data')

    def get_vm_cpu(self, vm_id):
        """Get VM cpu information.

        - cores_per_socket
        - cpu
        - hot_add
        - hot_remove
        - quick_stats

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object
        """
        json = self.request(f'/vm/{vm_id}/cpu')
        return json.get('data')

    def get_vm_cpu_config(self, vm_id):
        """Get VM cpu configuration.

        - hot_add
        - hot_remove

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object
        """
        json = self.request(f'/vm/{vm_id}/cpu/config')
        return json.get('data')

    def update_vm_cpu_hot_add(self, vm_id, hot_add, **kwargs):
        """Update Virtual Machine CPU hot add configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param hot_add: Enable or disable hot add
        :type hot_add: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(attribute='hotAdd', value=hot_add)
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/cpu/config',
            payload=payload,
            method=self.PUT,
        )
        return json.get('data')

    def update_vm_cpu_hot_remove(self, vm_id, hot_remove, **kwargs):
        """Update Virtual Machine CPU hot remove configuration.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param hot_remove: Enable or disable hot remove
        :type hot_remove: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(attribute='hotRemove', value=hot_remove)
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/cpu/config',
            payload=payload,
            method=self.PUT,
        )
        return json.get('data')

    def enable_vm_cpu_hot_add(self, vm_id, **kwargs):
        """Enable virtual machine CPU hot add.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_cpu_hot_add(vm_id, True, **kwargs)
        return json.get('data')

    def disable_vm_cpu_hot_add(self, vm_id, **kwargs):
        """Disable virtual machine CPU hot add.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_cpu_hot_add(vm_id, False, **kwargs)
        return json.get('data')

    def enable_vm_cpu_hot_remove(self, vm_id, **kwargs):
        """Enable virtual machine CPU hot remove.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_cpu_hot_remove(vm_id, True, **kwargs)
        return json.get('data')

    def disable_vm_cpu_hot_remove(self, vm_id, **kwargs):
        """Disable virtual machine CPU hot remove.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_cpu_hot_remove(vm_id, False, **kwargs)
        return json.get('data')

    def set_vm_cpu(
        self, vm_id, number, cores_per_socket: Optional[int] = 1, **kwargs
    ):
        """Update Virtual Machine CPU count.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param number: New vCPU count
        :type number: int
        :param cores_per_socket: number of cores per socket.

         ..note: When setting this parameter
           refer to https://kb.vmware.com/s/article/1010184
           for further details.

        :type cores_per_socket: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(
            value={'count': number, 'cores_per_socket': cores_per_socket}
        )
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/cpu',
            payload=payload,
            method=self.PUT,
        )
        return json.get('data')

    # Virtual Machine devices
    def get_vm_nics(self, vm_id):
        """Get Virtual Machine NICs information.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/nic')
        nic_numbers = [nic.get('unit') for nic in json.get('data')]
        nics = list()
        for nic in nic_numbers:
            json = self.request(f'/vm/{vm_id}/nic/{nic}')
            nics.append({'unit': nic, 'data': json['data'][0]})
        return nics

    def get_vm_nic(self, vm_id, nic):
        """Get Virtual Machine NIC information.

        - connected
        - label
        - mac_address
        - network
        - start_connected
        - type

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param nic: nic number
        :type nic: int
        :return:
        """
        json = self.request(f'/vm/{vm_id}/nic/{nic}')
        return json.get('data')

    def get_supported_build_types(
        self, only_type: bool = True
    ) -> Union[Dict, List[str]]:
        """Get supported VM build types.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_BUILD_PROCESS
        else:
            json = self.request('/vss/vm-build')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def get_supported_nic_types(
        self, only_type: bool = True
    ) -> Union[Dict, List[str]]:
        """Get supported Virtual Machine network adapter types.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_NIC_TYPE
        else:
            json = self.request('/vss/vm-nic-type')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def create_vm_nic(self, vm_id, networks, **kwargs):
        """Create Virtual Machine NICs.

        For every network in the list a network adapter
        number will be assigned.

            Example::

                networks = [
                    {'network': 'dvmoref-01'},
                    {'network': 'dvmoref-02', 'type': 'vmxnet3'}
                ]

                vss.create_vm_nic(vm_id, networks=networks)

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param networks: list of network adapter objects. For example:
            `{'network': 'moref', 'type': 'valid_type'}`
        :type networks: list
        :return: change request object

        .. note:: For more information about network interface types,
          refer to :py:func:`get_supported_nic_types`.
        .. note:: If `type` is not found in network interface object,
          the default value will be used.
        .. note:: If duplicated networks are included, the API will ignore
          them since no VM  is to have two adapters on the same network.

        """
        json_payload = dict(value=self.validate_networks(networks))
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/nic',
            method=self.POST,
            payload=json_payload,
        )
        return json.get('data')

    def delete_vm_nic(self, vm_id, unit, **kwargs):
        """Delete Virtual Machine NIC unit.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: Network interface card number
        :type unit: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict()
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/nic/{unit}',
            method=self.DELETE,
            payload=json_payload,
        )
        return json.get('data')

    def delete_vm_nics(self, vm_id, units, **kwargs):
        """Delete Virtual Machine NIC units.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param units: Network interface card numbers
        :type units: list
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=units)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/nic',
            method=self.DELETE,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_nic_network(self, vm_id, nic, network, **kwargs):
        """Update Virtual Machine network on a given nic.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param nic: Network interface card number
        :type nic: int
        :param network: new network moref
        :type network: str
        :return: change request object

        .. note:: keywords arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(attribute='network', value=network)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/nic/{nic}',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_nic_type(self, vm_id, nic, type, **kwargs):
        """Update Virtual Machine NIC type.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param nic: Network interface card number
        :type nic: int
        :param type: new nic type :py:func:`get_supported_nic_types`.
        :type type: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        supported_nic_types = self.get_supported_nic_types(only_type=True)
        if type not in supported_nic_types and not self.dry_run:
            raise VssError(
                '%s: unsupported NIC type. Choose between: %s'
                % (type, ', '.join(supported_nic_types))
            )

        json_payload = dict(attribute='type', value=type)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/nic/{nic}',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_nic_state(self, vm_id, nic, state, **kwargs):
        """Update Virtual Machine NIC state.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param nic: Network interface card number
        :type nic: int
        :param state: new nic state (connect, disconnect)
        :type state: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if state not in ['connect', 'disconnect']:
            raise VssError('Unsupported NIC state')

        json_payload = dict(attribute='state', value=state)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/nic/{nic}',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_floppies(self, vm_id):
        """Get Virtual Machine Floppy devices available.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/floppy')
        floppy_units = [fl.get('unit') for fl in json.get('data')]
        floppies = list()
        for fl in floppy_units:
            data = self.get_vm_floppy(vm_id, fl)
            floppies.append({'unit': data, 'data': data[0]})
        return floppies

    def get_vm_floppy(self, vm_id, floppy):
        """Get Virtual Machine floppy unit.

        - backing
        - connected
        - controller
        - description
        - label

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param floppy: floppy unit number
        :type floppy: int
        :return: object
        """
        json = self.request(f'/vm/{vm_id}/floppy/{floppy}')
        return json.get('data')

    def update_vm_floppy(self, vm_id, unit, image=None, **kwargs):
        """Update Floppy unit backing to client or image.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: floppy unit
        :type unit: int
        :param image: full path to Image
        :type image: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(attribute='img', value=image)
        if not image:
            payload['attribute'] = 'client'
            payload['value'] = 'ph'
        payload.update(kwargs)
        data = self.request(
            f'/vm/{vm_id}/floppy/{unit}',
            method=self.PUT,
            payload=payload,
        )
        return data.get('data')

    def get_vm_cds(self, vm_id):
        """Get Virtual Machine CD/DVD devices available.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/cd')
        cd_units = [cd.get('unit') for cd in json.get('data')]
        cds = list()
        for cd in cd_units:
            data = self.get_vm_cd(vm_id, cd)
            cds.append({'unit': cd, 'data': data[0]})
        return cds

    def get_vm_cd(self, vm_id, cd):
        """Get Virtual Machine CD/DVD unit information.

        - backing
        - connected
        - controller
        - description
        - label

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param cd: CD/DVD unit number
        :type cd: int
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/cd/{cd}')
        return json.get('data')

    def update_vm_cd(self, vm_id, unit, iso=None, **kwargs):
        """Update given CD unit backing to client or ISO.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: CD/DVD unit
        :type unit: int
        :param iso: full path to ISO
        :type iso: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(iso=iso) if iso else dict()
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/cd/{unit}',
            method=self.PATCH,
            payload=json_payload,
        )
        return json.get('data')

    def create_vm_cd(self, vm_id, backings=None, **kwargs):
        """Create CD/DVD drives.

        By default it creates a single CD/DVD unit
        backed by client pass-through.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param backings: either client or iso path or iso image id.
          I.e ["client", "iso_id_or_path"]
        :param backings: list
        :param kwargs:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(value=backings or ['client'])
        payload.update(kwargs)
        json = self.request(
            '/vm/%s/cd' % vm_id, method=self.POST, payload=payload
        )
        return json.get('data')

    def get_vm_controllers(self, vm_id):
        """List Virtual machine available controllers.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/controller')
        data = json.get('data')
        if not data:
            return None
        del data['scsi']['_links']
        return data

    def get_vm_scsi_devices(self, vm_id):
        """Get Virtual machine available SCSI controllers.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects
        """
        json = self.request(f'/vm/{vm_id}/controller/scsi')
        data = json.get('data')
        if not data:
            return None
        scsi = []
        for c in data:
            del c['_links']
            scsi.append(c)
        return scsi

    def get_vm_scsi_device(self, vm_id, bus, devices=None):
        """Get Virtual Machine available SCSI bus.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param bus: SCSI bus number
        :type bus: int
        :param devices: include attached devices
        :type devices: bool
        :return: object
        """
        json = self.request(f'/vm/{vm_id}/controller/scsi/{bus}')
        data = json.get('data')
        if not data:
            return None
        data = data[0]
        if devices:
            devs = self.get_vm_disk_by_scsi_device(vm_id, bus)
        else:
            devs = data['devices']['count']
        data['devices'] = devs
        return data

    def get_supported_scsi_sharing(
        self, only_type: bool = True
    ) -> List[Union[str, Dict]]:
        """Get supported Virtual Machine scsi controller sharing.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_SCSI_CONTROLLER
        else:
            json = self.request('/vss/vm-disk-scsi-controller-sharing')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def get_supported_scsi_controllers(self, only_type: bool = True):
        """Get supported Virtual Machine scsi controller types.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_SCSI_CONTROLLER
        else:
            json = self.request('/vss/vm-disk-scsi-controller')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def create_vm_scsi_device(self, vm_id, devices, **kwargs):
        """Create Virtual Machine SCSI controllers given specs.

        For every item in the `devices` list, a new SCSI
        controller will be created matching the provided type.

            Example::

                devices = ['paravirtual', 'lsilogic']

                or

                devices = [
                    {"type": "lsilogic"},
                    {
                     "type": "paravirtual", "sharing":
                     "virtualSharing"
                    }
                ]

                vss.create_vm_scsi_device(vm_id, devices=devices)

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param devices: SCSI bus number
        :type devices: list
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. note:: For more information about SCSI controller types,
          refer to :py:func:`get_supported_scsi_controllers`.
        .. note:: For more information about SCSI controller sharing,
          refer to :py:func:`get_supported_scsi_sharing`.
        """
        json_payload = dict(value=self.validate_scsi_controllers(devices))
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/controller/scsi',
            method=self.POST,
            payload=json_payload,
        )
        return json.get('data')

    def validate_scsi_controllers(self, devices: Union[List[str], List[Dict]]):
        """Validate scsi payloads.

        Supports either a scsi spec payload or a simple list of ints.

            Example::

                devices = ['paravirtual', 'paravirtual']

                or

                disks = [
                  {"type": "paravirtual"},
                  {
                   "type": "paravirtual",
                   "sharing": "virtualSharing"
                  },
                ]
        """
        payload = list()
        for device in devices:
            if isinstance(device, dict):
                try:
                    self.validate_vm_scsi_controller_type(device['type'])
                except KeyError:
                    raise VssError('Missing type')
                if 'sharing' in device:
                    self.validate_vm_scsi_controller_sharing(device['sharing'])
                payload.append(device)
            else:
                try:
                    item = {'type': str(device)}
                except ValueError:
                    raise VssError(
                        'Either a list of strings or a '
                        'scsi spec (list of dict)'
                    )
                payload.append(item)
        return payload

    def delete_vm_scsi_device(self, vm_id, bus, **kwargs):
        """Delete given Virtual Machine SCSI controller.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param bus: bus number
        :type bus: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.request(
            f'/vm/{vm_id}/controller/scsi/{bus}',
            method=self.DELETE,
            payload=kwargs,
        )
        return json.get('data')

    def delete_vm_scsi_devices(self, vm_id, buses, **kwargs):
        """Delete given Virtual Machine SCSI controller units.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param buses: disk units to delete
        :type buses: list
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=buses)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/controller/scsi',
            method=self.DELETE,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_scsi_device_type(self, vm_id, bus, bus_type, **kwargs):
        """Update given Virtual Machine SCSI controller type.

         - buslogic
         - paravirtual
         - lsilogicsas
         - lsilogic

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param bus: bus number to update
        :type bus: int
        :param bus_type: new bus type
        :type bus_type: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=bus_type)
        json_payload.update(kwargs)
        json = self.request(
            '/vm/{vm_id}/controller/scsi/{bus}/type'.format(
                vm_id=vm_id, bus=bus
            ),
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_scsi_device_sharing(
        self, vm_id: str, bus: Union[str, int], sharing: str, **kwargs
    ):
        """Update given Virtual Machine SCSI controller type.

         - nosharing
         - physicalsharing
         - virtualsharing

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param bus: bus number to update
        :type bus: int
        :param sharing: new bus type
        :type sharing: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=sharing)
        json_payload.update(kwargs)
        json = self.request(
            '/vm/{vm_id}/controller/scsi/{bus}/sharing'.format(
                vm_id=vm_id, bus=int(bus)
            ),
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_disk_by_scsi_device(self, vm_id, bus):
        """Get Virtual Machine attached devices to given SCSI controller.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param bus: SCSI bus number
        :type bus: int
        :return: list of objects
        """
        json = self.request(
            '/vm/{vm_id}/controller/scsi/{bus}/disk'.format(
                vm_id=vm_id, bus=bus
            )
        )
        disks = list()
        disk_units = [disk.get('unit') for disk in json.get('data')]
        for disk in disk_units:
            d = self.get_vm_disk(vm_id, disk)
            disks.append(d[0])
        return disks

    def get_vm_disks(self, vm_id):
        """Get Virtual Machine available disks.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of objects

        """
        json = self.request(f'/vm/{vm_id}/disk')
        disk_units = [disk.get('unit') for disk in json.get('data')]
        disks = list()
        for disk in disk_units:
            data = self.get_vm_disk(vm_id, disk)
            disks.append({'unit': disk, 'data': data[0]})
        return disks

    def get_vm_disk(self, vm_id, disk):
        """Get Virtual Machine disk data.

        - capacity_gb
        - controller
        - description
        - label
        - shares

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param disk: Virtual Machine disk number
        :type disk: int
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/disk/{disk}')
        return json.get('data')

    def get_vm_disk_notes(self, vm_id, unit):
        """Get vm disk note metadata.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: Virtual Machine disk number
        :type unit: int
        :return: int
        """
        notes = self.request(f'/vm/{vm_id}/disk/{unit}/note')
        return notes.get('data')

    def get_vm_disk_capacity(self, vm_id, unit):
        """Get virtual machine disk capacity in GB.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: Virtual Machine disk number
        :type unit: int
        :return: int
        """
        disk = self.get_vm_disk(vm_id, unit)
        if not disk:
            raise VssError(f'Could not find disk {unit}')
        return disk[0].get('capacity_gib')

    def get_supported_disk_backing_modes(self, only_type=True):
        """Get supported Virtual Machine Disk Backing modes.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_DISK_MODE
        else:
            json = self.request('/vss/vm-disk-mode')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def get_vm_disk_backing(self, vm_id, disk):
        """Get Virtual Machine disk backing data mode.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param disk: Virtual Machine disk number
        :type disk: int
        :return: object

        .. note:: For more information about disk backing modes,
          refer to :py:func:`get_supported_disk_backing_modes`.
        """
        json = self.request(f'/vm/{vm_id}/disk/{disk}/backing')
        return json.get('data')

    def update_vm_disk_backing_mode(self, vm_id, unit, mode, **kwargs):
        """Update given Virtual Machine Disk backing mode.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: disk unit to update
        :type unit: int
        :param mode: new bus type
        :type mode: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. note:: For more information about disk backing modes,
          refer to :py:func:`get_supported_disk_backing_modes`.

        """
        payload = dict(value=self.validate_vm_disk_backing_mode(mode))
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/disk/{unit}/backing/mode',
            method=self.PUT,
            payload=payload,
        )
        return json.get('data')

    def get_supported_disk_sharing(self, only_type=True):
        """Get supported Virtual Machine Disk Sharing modes.

        :param only_type: return only types (no description)
        :return: list
        """
        if self.dry_run:
            data = VALID_VM_DISK_SHARING
        else:
            json = self.request('/vss/vm-disk-sharing')
            data = json.get('data')
        return [i['type'] for i in data] if only_type else data

    def update_vm_disk_backing_sharing(self, vm_id, unit, sharing, **kwargs):
        """Update given Virtual Machine Disk backing mode.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: disk unit to update
        :type unit: int
        :param sharing: new sharing type
        :type sharing: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. note:: For more information about disk backing modes,
          refer to :py:func:`get_supported_disk_backing_modes`.

        """
        payload = dict(value=self.validate_vm_disk_backing_sharing(sharing))
        payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/disk/{unit}/backing/sharing',
            method=self.PUT,
            payload=payload,
        )
        return json.get('data')

    def get_vm_disk_scsi(self, vm_id, disk):
        """Get Virtual Machine disk SCSI controller data.

        - bus_number
        - label
        - type

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param disk: Virtual Machine disk number
        :type disk: int
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/disk/{disk}/scsi')
        return json.get('data')

    def update_vm_disk_scsi(self, vm_id, unit, bus_number, **kwargs):
        """Update Virtual Machine disk SCSI controller.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param bus_number: New SCSI controller bus number
        :type bus_number: int
        :param unit: Virtual Machine disk number
        :type unit: int
        :return: object

        """
        payload = dict(value=bus_number)
        payload.update(kwargs)
        rv = self.request(
            f'/vm/{vm_id}/disk/{unit}/scsi',
            method=self.PUT,
            payload=payload,
        )
        return rv.get('data')

    @staticmethod
    def validate_scsi_bus(bus: Union[str, int]) -> int:
        """Validate SCSI bus."""
        try:
            bus = int(bus)
            if not -1 < bus < 4:
                raise VssError('SCSI controller bus must be between 0 and 3')
        except ValueError:
            raise VssError('SCSI Controller bus must be a number.')
        return bus

    def validate_scsi(self, scsi: Union[List[str], List[Dict]]) -> List[Dict]:
        """Validate scsi payloads.

        Supports either a scsi spec payload or a simple list of str.

            Example::

                scsi = ["lsilogic", "paravirtual]

                or

                scsi = [
                  {"type": "paravirtual", "bus":  1},
                  {"type": "lsilogic", "bus": 0}
                ]

        """
        payload = list()
        for ctlr in scsi:
            if isinstance(ctlr, dict):
                try:
                    ctlr_type = ctlr['type']
                    ctlr_bus = ctlr['bus']
                except KeyError as ex:
                    raise VssError(f'Missing {ex.args}')
                ctlr['bus'] = self.validate_scsi_bus(ctlr_bus)
                self.validate_vm_scsi_controller_type(ctlr_type)
                if 'sharing' in ctlr:
                    self.validate_vm_scsi_controller_sharing(ctlr['sharing'])
                payload.append(ctlr)
            else:
                item = self.validate_vm_scsi_controller_type(ctlr)
                payload.append(item)
        return payload

    def validate_disks(
        self, disks: Union[List[int], List[Dict]]
    ) -> List[Dict]:
        """Validate disk payloads.

        Supports either a disk spec payload or a simple list of ints.

            Example::

                disks = [40, 100, 50]

                or

                disks = [
                  {"capacity_gb": 40},
                  {
                   "capacity_gb": 100,
                   "backing_mode": "independent_persistent",
                   "backing_vmdk":
                   "[vssUser-xfers] vskey/<user>/FOLDER/disk-0.vmdk"
                   },
                ]
        """
        payload = list()
        for disk in disks:
            if isinstance(disk, dict):
                try:
                    _ = disk['capacity_gb']
                except KeyError:
                    raise VssError('Missing capacity_gb')
                if 'backing_mode' in disk:
                    self.validate_vm_disk_backing_mode(disk['backing_mode'])
                if 'backing_sharing' in disk:
                    self.validate_vm_disk_backing_sharing(
                        disk['backing_sharing']
                    )
                if 'scsi' in disk:
                    disk['scsi'] = self.validate_scsi_bus(disk['scsi'])
                payload.append(disk)
            else:
                try:
                    item = {'capacity_gb': int(disk)}
                except ValueError:
                    raise VssError(
                        'Either a list of ints or a '
                        'disk spec (list of dict)'
                    )
                payload.append(item)
        return payload

    def create_vm_disk(self, vm_id, disks, **kwargs):
        """Create virtual machine disks with a given specs.

        For every value in GB in the list a virtual disk will be assigned.

            Example::

                disks = [40, 100, 50]

                or

                disks = [
                  {"capacity_gb": 40},
                  {
                   "capacity_gb": 100,
                   "backing_mode": "independent_persistent",
                   "backing_vmdk":
                   "[vssUser-xfers] vskey/<user>/FOLDER/disk-0.vmdk"
                   },
                ]

                vss.create_vm_disk(vm_id, disks=disks)

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param disks: a list of disk capacities in GB or disk specs.
        :type disks: list
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=self.validate_disks(disks))
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/disk',
            method=self.POST,
            payload=json_payload,
        )
        return json.get('data')

    def update_vm_disk_notes(self, vm_id, unit, notes, append=True):
        """Update vm disk notes.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: unit to update
        :type unit: int
        :param notes: text to add
        :type notes: str
        :param append: whether to append or replace.
        :type append: bool
        :return:
        """
        payload = dict(value=str(notes), append=append)
        disk = self.get_vm_disk(vm_id, unit)
        if not disk:
            raise VssError(f'Cannot find disk {unit}')
        return self.request(
            f'/vm/{vm_id}/disk/{unit}/note', method='PUT', payload=payload
        )

    def delete_vm_disk_notes(self, vm_id, unit):
        """Delete vm disk notes.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: unit to update
        :type unit: int
        :return:
        """
        disk = self.get_vm_disk(vm_id, unit)
        if not disk:
            raise VssError(f'Cannot find disk {unit}')
        return self.request(f'/vm/{vm_id}/disk/{unit}/note', method='DELETE')

    def update_vm_disk_capacity(self, vm_id, unit, value_gb, **kwargs):
        """Update given Virtual Machine disk capacity.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: unit to update
        :type unit: int
        :param value_gb: New capacity in GB
        :type value_gb: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(attribute='capacity', value=value_gb)
        if self.needs_consolidation(vm_id):
            raise VssError(
                'Disk consolidation is required. '
                'Please, consolidate disks prior increasing capacity.'
            )
        c_dc = self.get_vm_disk_capacity(vm_id, unit)
        if value_gb <= c_dc:
            raise VssError(
                f'Reducing disk size is not supported: '
                f'current {c_dc}GB to {value_gb}GB.'
            )
        payload.update(kwargs)
        rv = self.request(
            f'/vm/{vm_id}/disk/{unit}',
            method=self.PUT,
            payload=payload,
        )
        return rv.get('data')

    def delete_vm_disk(self, vm_id, unit, **kwargs):
        """Delete given Virtual Machine disk unit.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param unit: unit to delete
        :type unit: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = self.request(
            f'/vm/{vm_id}/disk/{unit}',
            method=self.DELETE,
            payload=kwargs,
        )
        return payload.get('data')

    def delete_vm_disks(self, vm_id, units, **kwargs):
        """Delete given Virtual Machine disk units.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param units: disk units to delete
        :type units: list
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(value=units)
        payload.update(kwargs)
        rv = self.request(
            f'/vm/{vm_id}/disk',
            method=self.DELETE,
            payload=payload,
        )
        return rv.get('data')

    def is_powered_on_vm(self, vm_id):
        """Check if given Virtual Machine is On.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: bool
        """
        data = self.get_vms(filter='moref,eq,%s' % vm_id) or self.get_vms(
            filter='uuid,eq,%s' % vm_id
        )
        if not data:
            return False
        else:
            power_state = data[0].get('power_state', 'unknown')
            return power_state == 'poweredOn'

    def is_powered_off_vm(self, vm_id):
        """Check if given Virtual Machine is Off.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: bool
        """
        data = self.get_vms(filter='moref,eq,%s' % vm_id) or self.get_vms(
            filter='uuid,eq,%s' % vm_id
        )
        if not data:
            return None
        else:
            power_state = data[0].get('power_state', 'unknown')
            return power_state == 'poweredOff'

    def reboot_vm(self, vm_id, **kwargs):
        """Graceful reboot VM.

        This method sends a reboot signal via VMware Tools to
        the Guest Operating system, thus VMware Tools is required
        up-to-date and running on VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        rv = self.update_vm_state(vm_id=vm_id, state='reboot', **kwargs)
        return rv

    def suspend_vm(self, vm_id, **kwargs):
        """Suspend Virtual Machine.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
           on a given date and time

        """
        json = self.update_vm_state(vm_id=vm_id, state='suspend', **kwargs)
        return json

    def reset_vm(self, vm_id, **kwargs):
        """Power cycle VM.

        Hard reset VM. This method resets a given Virtual Machine.
        This method is equivalent to power_off_vm and power_on_vm

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
           on a given date and time

        """
        json = self.update_vm_state(vm_id=vm_id, state='reset', **kwargs)
        return json

    def power_off_vm(self, vm_id, **kwargs):
        """Power Off VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(vm_id=vm_id, state='poweredOff', **kwargs)
        return json

    def power_on_vm(self, vm_id, **kwargs):
        """Power On VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(vm_id=vm_id, state='poweredOn', **kwargs)
        return json

    def shutdown_vm(self, vm_id, **kwargs):
        """Graceful shutdown VM.

        This method sends a shutdown signal via VMware Tools
        to the Guest Operating system, thus VMware Tools is required
        up-to-date and running on VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(vm_id=vm_id, state='shutdown', **kwargs)
        return json

    def rename_vm(self, vm_id, name, **kwargs):
        """Update Virtual Machine name.

        This does not change the VSS prefix ``YYMM{P|Q|D|T}-VMName``.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param name: New virtual machine name. Do not
         include VSS prefix.
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=name)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/name',
            method=self.PUT,
            payload=json_payload,
        )

        return json.get('data')

    # Virtual Machine Remote Console (VMRC) Settings
    def is_enabled_vm_vmrc_copy_paste(self, vm_id):
        """Check if VM Remote Console Copy Paste Settings are enabled.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: bool
        """
        json = self.get_vm_vmrc_copy_paste(vm_id)
        return json.get('enabled', False)

    def get_vm_vmrc_copy_paste(self, vm_id, options=False, **kwargs):
        """Get Virtual Machine Remote Console Copy Paste Settings.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param options: show enabled options
        :type options: bool
        :return: obj
        """
        params = dict(options=options) if options else None
        json = self.request(
            f'/vm/{vm_id}/console/copy-paste', params=params, **kwargs
        )
        return json.get('data')

    def enable_vm_vmrc_copy_paste(self, vm_id, **kwargs):
        """Enable the Copy/Paste between the VMRC client and Windows VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: obj
        """
        if self.is_enabled_vm_vmrc_copy_paste(vm_id):
            raise VssError('vmrc copy-paste already enabled')
        json = self.request(
            f'/vm/{vm_id}/console/copy-paste', method=self.POST, **kwargs
        )
        return json.get('data')

    def disable_vm_vmrc_copy_paste(self, vm_id, **kwargs):
        """Disable the Copy/Paste between the VMRC client and Windows VM.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: obj
        """
        if not self.is_enabled_vm_vmrc_copy_paste(vm_id):
            raise VssError('vmrc copy-paste already disabled')
        json = self.request(
            f'/vm/{vm_id}/console/copy-paste', method=self.DELETE, **kwargs
        )
        return json.get('data')

    # Virtual Machine Notes
    def get_vm_notes(self, vm_id):
        """Get Virtual Machine client notes.

        Metadata available for users to manage.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of key value notes
        """
        json = self.request(f'/vm/{vm_id}/note/client')
        return json.get('data')

    def update_vm_notes(self, vm_id, notes, **kwargs):
        """Update Virtual Machine client notes.

        Notes are stored as key-value metadata items.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param notes: New client custom notes
        :type notes: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=notes)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/note/client',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    # Virtual Machine VSS attributes
    def get_vm_vss_service(self, vm_id):
        """Obtain virtual machine VSS Service.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: obj
        """
        json = self.request(f'/vm/{vm_id}/vss/service')
        return json.get('data')

    def update_vm_vss_service(self, vm_id, service_name_or_id, **kwargs):
        """Update virtual machine VSS Service.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param service_name_or_id: VSS Service name.
        :type service_name_or_id: str or int
        :return: obj
        """
        json_payload = dict(value=service_name_or_id)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/service',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_supported_vss_options(self, only_option=True):
        """Get Virtual Machine VSS Options supported.

        :param only_option: return only option (no description)
        :return: list
        """
        json = self.request('/vss/option')
        data = json.get('data')
        return [i['option'] for i in data] if only_option else data

    def get_vm_vss_options(self, vm_id):
        """Get virtual machine vss options.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of options
        """
        json = self.request(f'/vm/{vm_id}/vss/option')
        return json.get('data')

    def get_vm_vss_option(self, vm_id, option_name):
        """Get virtual machine vss option by name.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param option_name: Vss option name
        :type option_name: str
        :return: dict
        """
        json = self.request(
            '/vm/{vm_id}/vss/option/{option_name}'.format(
                vm_id=vm_id, option_name=option_name
            )
        )
        return json.get('data')

    def enable_vm_vss_option(self, vm_id, option_name, **kwargs):
        """Enable virtual machine vss option by name.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param option_name: Vss option name
        :type option_name: str
        :return: dict
        """
        json = self.request(
            '/vm/{vm_id}/vss/option/{option_name}'.format(
                vm_id=vm_id, option_name=option_name
            ),
            method=self.POST,
            **kwargs,
        )
        return json.get('data')

    def disable_vm_vss_option(self, vm_id, option_name, **kwargs):
        """Disable virtual machine vss option by name.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param option_name: Vss option name
        :type option_name: str
        :return: dict
        """
        json = self.request(
            '/vm/{vm_id}/vss/option/{option_name}'.format(
                vm_id=vm_id, option_name=option_name
            ),
            method=self.DELETE,
            **kwargs,
        )
        return json.get('data')

    def get_vm_vss_description(self, vm_id):
        """Get Virtual Machine description.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: dict with description
        """
        json = self.request(f'/vm/{vm_id}/vss/description')
        return json.get('data')

    def update_vm_vss_description(self, vm_id, description, **kwargs):
        """Update Virtual Machine description.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param description: New virtual machine description.
        :type description: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=description)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/description',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_vss_admin(self, vm_id):
        """Get Virtual Machine administrator.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: dict with phone, name and email of
         vm admin

        """
        json = self.request(f'/vm/{vm_id}/vss/admin')
        return json.get('data')

    def update_vm_vss_admin(self, vm_id, name, phone, email, **kwargs):
        """Update Virtual Machine administrator contact info.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param name: Full name of VM admin
        :type name: str
        :param phone: Valid phone number of VM admin
        :type phone: str
        :param email: Valid email address of VM admin
        :type email: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=':'.join([name, phone, email]))
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/admin',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_vss_ha_group(self, vm_id):
        """Get Virtual Machine High Availability Group.

        This is part of the VSS metadata added to the VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: object

        """
        json = self.request(f'/vm/{vm_id}/vss/ha_group')
        return json.get('data')

    def delete_vm_vss_ha_group(self, vm_id):
        """Remove VM from availability group.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: obj
        """
        json = self.request(f'/vm/{vm_id}/vss/ha_group', method=self.DELETE)
        return json.get('data')

    def migrate_vm_vss_ha_group(self, vm_id):
        """Migrate VM from availability group from uuid to moref.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: obj
        """
        json = self.request(f'/vm/{vm_id}/vss/ha_group', method=self.PATCH)
        return json.get('data')

    def update_vm_vss_ha_group(self, vm_id, vms, append=True, **kwargs):
        """Update High Availability Group.

        This is part of the VSS metadata added to the
        VM annotation

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param vms: list of virtual machine Uuids
        :type vms: list
        :param append: whether to replace or append
        :type append: bool
        :return: object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=','.join(vms), append=append)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/ha_group',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_vss_usage(self, vm_id):
        """Get Virtual Machine Usage.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: dict

        """
        json = self.request(f'/vm/{vm_id}/vss/usage')
        return json.get('data')

    def get_vm_vss_client(self, vm_id):
        """Get Virtual Machine Client.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: dict

        """
        json = self.request(f'/vm/{vm_id}/vss/client')
        return json.get('data')

    def update_vm_vss_client(self, vm_id, client, **kwargs):
        """Update virtual machine client metadata.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param client: New VSS client
        :type client: str
        :return: change request

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=client)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/client',
            payload=json_payload,
            method=self.PUT,
        )
        return json.get('data')

    def get_vm_vss_changelog(self, vm_id):
        """Get Virtual Machine change log.

        Maximum change log entries are 9.

        This is part of the VSS metadata added to the
        VM annotation.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of changelog entries as dict

        """
        json = self.request(f'/vm/{vm_id}/vss/changelog')
        return json.get('data')

    def update_vm_vss_usage(self, vm_id, usage, **kwargs):
        """Update virtual machine VSS usage or environment.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param usage: New usage (Prod, Dev, Test or QA)
        :type usage: str
        :return: change request

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=usage)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/usage',
            payload=json_payload,
            method=self.PUT,
        )
        return json.get('data')

    def get_vm_vss_inform(self, vm_id):
        """Get Virtual Machine informational contacts.

        This is part of the VSS metadata added to the
        VM annotation

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of email addresses if any

        """
        json = self.request(f'/vm/{vm_id}/vss/inform')
        return json.get('data')

    def update_vm_vss_inform(self, vm_id, emails, append=True, **kwargs):
        """Update informational contacts.

        This is part of the VSS metadata added to the
        VM annotation

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param emails: list of email(s)
        :type emails: list
        :param append: whether to replace or append
        :type append: bool
        :return: object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=','.join(emails), append=append)
        json_payload.update(kwargs)
        json = self.request(
            f'/vm/{vm_id}/vss/inform',
            method=self.PUT,
            payload=json_payload,
        )
        return json.get('data')

    def get_vm_vss_requested(self, vm_id):
        """Get Virtual Machine requested timestamp.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: timestamp in str or none if unknown

        """
        json = self.request(f'/vm/{vm_id}/vss')
        return json.get('data').get('requested')

    # Virtual Machine summary
    def get_vm_storage(self, vm_id):
        """Get Virtual Machine storage summary.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: dict with:

        - uncommitted_gb
        - provisioned_gb
        - committed_gb
        - unshared_gb

        """
        json = self.get_vm(vm_id)
        return json.get('storage')

    def get_supported_extra_cfg_options(self, only_option=True):
        """Get Virtual Machine Extra Config Options supported.

        :param only_option: return only option (no description)
        :return: list
        """
        json = self.request('vss/vm-extra-config')
        data = json.get('data')
        return [i['option'] for i in data] if only_option else data

    def get_vm_extra_cfg_options(self, vm_id):
        """Get VM extra configuration (guestinfo.* and allowed options).

        Extra config options can be queried from the Guest Operating
        system using VMware Tools:

        Example::

            vmtoolsd --cmd "info-get guestinfo.<option>"

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of key value objects
        """
        json = self.request(f'/vm/{vm_id}/extra')
        return json.get('data')

    def get_vm_extra_cfg_option(self, vm_id, option):
        """Get VM extra configuration (guestinfo.* and allowed options).

        Extra config options can be queried from the Guest Operating
        system using VMware Tools:

        Example::

            vmtoolsd --cmd "info-get guestinfo.<option>"

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param option: Extra config option
        :type option: str
        :return: list of key value objects
        """
        json = self.request(f'/vm/{vm_id}/extra/{option}')
        return json.get('data')

    def update_vm_extra_cfg_options(self, vm_id, options):
        """Update VM extra configuration.

        Extra configuration options are either guestinfo.* or allowed
        options.

        Extra config guestinfo.* options can be queried from the
        Guest Operating system using VMware Tools:

        Example::

            vmtoolsd --cmd "info-get guestinfo.<option>"

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param options: list of dictionaries with key-value options to update.
        :type: list
        :return: object
        """
        json = self.request(
            f'/vm/{vm_id}/extra',
            method=self.PUT,
            payload=dict(value=options),
        )
        return json.get('data')

    def create_vm_extra_cfg_options(self, vm_id, options):
        """Create VM extra configuration settings.

        Extra configuration options are either guestinfo.* or allowed
        options.

        Extra config guestinfo.* options can be queried from the
        Guest Operating system using VMware Tools:

        Example::

            vmtoolsd --cmd "info-get guestinfo.<option>"

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param options: list of dictionaries with key-value options to create.
        :type: list
        :return: object
        """
        json = self.request(
            f'/vm/{vm_id}/extra',
            method=self.POST,
            payload=dict(value=options),
        )
        return json.get('data')

    def delete_vm_extra_cfg_option(self, vm_id, option):
        """Delete VM extra configuration key.

        Extra configuration options are either guestinfo.* or allowed
        options.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :param option: single option key to delete
        :type: str
        :return: object
        """
        json = self.request(
            f'/vm/{vm_id}/extra/{option}',
            method=self.DELETE,
        )
        return json.get('data')

    def delete_vm_extra_cfg_options(self, vm_id, options):
        """Delete VM extra configuration keys using the guestinfo.* prefix.

        :param vm_id: Virtual Machine moref or uuid
        :type vm_id: str
        :param options: list of keys to delete
        :type: list
        :return: object
        """
        json = self.request(
            f'/vm/{vm_id}/extra',
            method=self.DELETE,
            payload=dict(value=options),
        )
        return json.get('data')

    def get_vm_permission(self, vm_id):
        """Get VM permission list.

        :param vm_id: virtual machine moref or uuid
        :type vm_id: str
        :return: list of key value objects
        """
        json = self.request(f'/vm/{vm_id}/perm')
        return json.get('data')

    def get_network_permission(self, moref):
        """Get Network permission list.

        :param moref: Network managed object id
        :type moref: str
        :return: list of key value objects
        """
        json = self.request(f'/network/{moref}/perm')
        return json.get('data')

    def get_folder_permission(self, moref):
        """Get Folder permission list.

        :param moref: Folder managed object id
        :type moref: str
        :return: list of key value objects
        """
        json = self.request(f'/folder/{moref}/perm')
        return json.get('data')

    def request(
        self,
        url,
        headers=None,
        params=None,
        payload=None,
        method=None,
        auth=None,
        dry_run=None,
    ):
        """Request url."""
        # update _headers
        _headers = {
            'Content-Type': self._content_type,
            'User-Agent': self.user_agent,
        }
        if dry_run is not None:
            self.dry_run = dry_run
        if headers:
            _headers.update(headers)
        # basic auth or authorization header
        if not auth and self.api_token:
            _headers['Authorization'] = f'Bearer {self.api_token}'
        # endpoint validation
        if not url.startswith('http'):
            url = self.api_endpoint + url
        # create kwargs
        request_kwargs = {
            'headers': _headers,
            'params': params,
            'auth': auth,
            'url': url,
            'json': payload,
            'timeout': self.timeout,
        }
        # method or default GET
        method = method or self.GET
        # lookup dictionary
        lookup = {
            self.POST: requests.post,
            self.GET: requests.get,
            self.DELETE: requests.delete,
            self.PUT: requests.put,
            self.OPTIONS: requests.options,
            self.PATCH: requests.patch,
        }
        try:
            try:
                if self.dry_run:
                    rv_dict = {
                        'data': {'method': method, 'request': request_kwargs}
                    }
                    return rv_dict
                else:
                    resp = lookup[method](**request_kwargs)
                    rv_dict = self.process_rv(resp)
            except KeyError:
                raise VssError(f"Unsupported method: {method}")
        except ValueError as e:  # requests.models.json.JSONDecodeError
            raise ValueError(
                "The API server did not respond with a valid JSON: {}".format(
                    e
                )
            )
        except requests.RequestException as e:  # errors from requests
            raise RuntimeError(e)

        if resp.status_code not in [
            requests.codes.ok,
            requests.codes.accepted,
            requests.codes.created,
            requests.codes.no_content,
        ]:
            if rv_dict:
                vss_exc = VssError(
                    http_code=resp.status_code, message='VSS Exception'
                )
                if 'error' in rv_dict or 'message' in rv_dict:
                    msg = [f'{k}: {v}' for k, v in rv_dict.items()]
                    vss_exc.http_headers = dict(resp.headers)
                    msg = '; '.join(msg)
                    vss_exc.message = msg
                    raise vss_exc
            resp.raise_for_status()
        return rv_dict

    def wait_for_request(
        self, request_url, request_attr, required_status, max_tries=6
    ):
        """Wait for request to be in any given status.

        :param request_url: Request URL to check periodically
        :type request_url: str
        :param request_attr: Attribute to return upon completion
        :type request_attr: str
        :param required_status: Required request status.
        :type required_status: str
        :param max_tries: Maximum tries to check. Defaults to 6 and
         every try waits for 10 secs
        :type max_tries: int
        :return: False if failed or the type of attribute requested

        """
        from time import sleep

        tries = 0
        while True:
            request = self.request(request_url)
            if 'data' in request:
                if 'status' in request['data']:
                    status = request['data']['status']
                    if required_status == status:
                        return request['data'][request_attr]
                    elif status in [
                        RequestStatus.PENDING.name,
                        RequestStatus.IN_PROGRESS.name,
                    ]:
                        pass
                    elif status in [
                        RequestStatus.ERROR.name,
                        RequestStatus.ERROR_RETRY.name,
                    ]:
                        return False
            else:
                return False
            if tries >= max_tries:
                return False
            tries += 1
            sleep(10)

    def process_rv(self, response):
        """Process response codes.

        :param response: request.response object
        :return: dict
        """
        _headers = dict(headers=response.headers)
        rv = dict(status=response.status_code)
        # no content status
        if response.status_code == requests.codes.no_content:
            return rv.update(_headers) if self.debug else rv
        # 400s error
        elif 500 > response.status_code > 399:
            _rv = dict(
                error='user error', message='check request and try again'
            )
            if 'json' in response.headers.get('Content-Type'):
                # json content type
                _r = response.json()
                if 'message' in _r:
                    _rv['message'] = _r['message']
                if 'error' in _r:
                    _rv['error'] = _r['error']
            rv.update(_rv)
        # 500+ server error
        elif response.status_code > 499:
            _rv = dict(error='server error', message='api unavailable')
            if 'json' in response.headers.get('Content-Type'):
                # json content type
                _r = response.json()
                if 'message' in _r:
                    _rv['message'] = _r['message']
                if 'error' in _r:
                    _rv['error'] = _r['error']
            rv.update(_rv)
        else:
            # everything else
            if response.headers.get(
                'Content-Disposition'
            ) and response.headers.get('Content-Type'):
                # validate if response is a file, if so, return
                # response object
                return response
            elif 'json' in response.headers.get('Content-Type'):
                # json content type
                return response.json()
            else:
                _rv = dict(
                    error='server error', message='invalid api response'
                )
                rv.update(_rv)
        # add headers if debug
        if self.debug:
            rv.update(_headers)
        return rv

    def validate_networks(self, networks):
        """Validate network list of dictionaries or strings."""
        if is_list_of(networks, o_type=str):
            _networks = [
                {'network': self.validate_network(net)} for net in networks
            ]
        elif is_list_of(networks, o_type=dict):
            _networks = [
                {
                    'network': self.validate_network(net['network']),
                    'type': self.validate_vm_nic_type(net['type']),
                }
                for net in networks
            ]
        else:
            raise VssError('Invalid networks format')
        return _networks

    def validate_network(self, network):
        """Validate single network element."""
        if self.dry_run:
            return network
        networks = self.get_networks(show_all=True)
        if network not in [n['moref'] for n in networks]:
            raise VssError('%s: invalid network found')
        return network

    def validate_vm_nic_type(self, n_type):
        """Validate supported nic type.

        :param n_type: Network interface controller type
        :type n_type: str
        :return: str
        """
        if self.s_nic_types is None:
            self.s_nic_types = self.get_supported_nic_types(only_type=True)
        # dry-run verification
        if self.dry_run:
            return n_type
        else:
            return self.validate_options(n_type, self.s_nic_types)

    def validate_vm_scsi_controller_sharing(self, sharing):
        """Validate supported disk scsi controller sharing.

        :param sharing: SCSI controller sharing
        :type sharing: str
        :return: str
        """
        if self.s_scsi_controllers_sharing is None:
            self.s_scsi_controllers_sharing = self.get_supported_scsi_sharing(
                only_type=True
            )
        # dry-run verification
        if self.dry_run:
            return sharing
        else:
            return self.validate_options(
                sharing, self.s_scsi_controllers_sharing
            )

    def validate_vm_scsi_controller_type(self, n_type):
        """Validate supported disk scsi controller type.

        :param n_type: SCSI controller type
        :type n_type: str
        :return: str
        """
        if self.s_scsi_controllers is None:
            self.s_scsi_controllers = self.get_supported_scsi_controllers(
                only_type=True
            )
        # dry-run verification
        if self.dry_run:
            return n_type
        else:
            return self.validate_options(n_type, self.s_scsi_controllers)

    def validate_vm_disk_backing_mode(self, n_type):
        """Validate supported disk backing mode.

        :param n_type: Backing mode
        :param n_type: str
        :return: str
        """
        if self.s_disk_back_modes is None:
            self.s_disk_back_modes = self.get_supported_disk_backing_modes(
                only_type=True
            )
        if self.dry_run:
            return n_type
        else:
            return self.validate_options(n_type, self.s_disk_back_modes)

    def validate_vm_disk_backing_sharing(self, n_type):
        """Validate supported disk backing sharing.

        :param n_type: Sharing type
        :param n_type: str
        :return: str
        """
        if self.s_disk_back_sharing is None:
            self.s_disk_back_sharing = self.get_supported_disk_sharing(
                only_type=True
            )
        if self.dry_run:
            return n_type
        else:
            return self.validate_options(n_type, self.s_disk_back_sharing)

    @property
    def status(self):
        """Return status of the api.

        :return: dict
        """
        return self.request('/status').get('data')

    @staticmethod
    def validate_options(item, options):
        """Validate VSS Options."""
        if item not in options:
            raise VssError(
                '%s: unsupported. Choose between: %s'
                % (item, ', '.join(options))
            )
        return item

    @staticmethod
    def validate_usage(usage):
        """Validate usage."""
        # validate basic items
        valid_usage = [
            (u, a) for u, a in VALID_VM_USAGE if usage.lower() in u.lower()
        ]
        if valid_usage:
            usage = valid_usage[0][1]
        else:
            raise VssError(f'Usage {usage} not supported')
        return usage

    def validate_build_process(self, n_type) -> str:
        """Validate build process."""
        if self.s_vm_build is None:
            self.s_vm_build = self.get_supported_build_types(only_type=True)
        if self.dry_run:
            return n_type
        else:
            return self.validate_options(n_type, self.s_vm_build)

    @staticmethod
    def get_retirement_timedelta_spec(
        hours: Optional[int] = 0,
        days: Optional[int] = 0,
        months: Optional[int] = 0,
    ) -> Dict:
        """Get retirement specification for timedelta.

        :param hours: number of hours from now until retirement.
        :type hours: int
        :param days: number of days from now until retirement.
        :type days: int
        :param months: number of months from now until retirement.
        :type months: int
        :return: object
        """
        one = list(filter(lambda x: x > 0, [days, months, hours]))
        if not one:
            raise VssError('At least one must be set: hours, days, months.')
        return dict(days=days, months=months, hours=hours, type='timedelta')

    @staticmethod
    def get_retirement_datetime_spec(date_time: str) -> Dict:
        """Get retirement specification for datetime.

        :param date_time: Timestamp with the following format
         ``%Y-%m-%d %H:%M``.
        :type date_time: str
        :return: object
        """
        _ = datetime.datetime.strptime(date_time, DATETIME_FMT)
        return dict(type='datetime', datetime=date_time)

    @staticmethod
    def get_custom_spec(hostname, domain, interfaces, dns=None):
        """Generate a customization specification.

        :param hostname: The network host name of the virtual machine.
        :type hostname: str
        :param domain: A DNS domain suffix such as eis.utoronto.ca.
        :type domain: str
        :param interfaces: A list of interface objects based on
         :py:func:`get_custom_spec_interface`
        :type interfaces: list
        :param dns: A list of server IP addresses to use for DNS lookup
         in a Windows guest operating system.
        :type dns: list
        :return:
        """
        custom_spec = dict(
            hostname=hostname, domain=domain, interfaces=interfaces
        )
        has_dhcp = False
        for interface in interfaces:
            if interface.get('dhcp') is True:
                has_dhcp = True
        # validates whether any interface has dhcp and not dns
        # but not dns and not dhcp is invalid
        if not dns and not has_dhcp:
            raise VssError('dns is required')
        # adds dns to the spec
        if dns:
            custom_spec['dns'] = dns
        return custom_spec

    @staticmethod
    def get_custom_spec_interface(dhcp, ip=None, mask=None, gateway=None):
        """Generate an interface object item for a customization specification.

        Customization specification reference :py:func:`get_custom_spec`.

        :param dhcp: Whether the virtual machine acquires IP config from
         DHCP. If set to true, parameters ip, subnet dns and gateway will
         be ignored.
        :type dhcp: bool
        :param ip: Specification to obtain a unique IP address
         for this virtual network adapter.
        :type ip: str
        :param mask: Subnet mask for this virtual network adapter.
        :type mask: str
        :param gateway: For a virtual network adapter with a static IP address,
         this data object type contains a list of gateways,
         in order of preference.
        :type gateway: list
        :return:
        """
        interface = dict(dhcp=dhcp)
        if not dhcp:
            fixed_ip = dict(ip=ip, mask=mask, gateway=gateway)
            interface.update(fixed_ip)
        return interface


def run_main():
    """Run main function wrapper.

    Checks for `VSS_API_TOKEN` environment variable

    Example::

        python pyvss/manager.py get_vms 'summary=1&name=pm'

    """
    import pprint
    import sys

    api_token = os.environ.get('VSS_API_TOKEN')
    if not api_token:
        raise VssError('Missing environment variable VSS_API_TOKEN')
    manager = VssManager(api_token)
    fname = sys.argv[1]
    pprint.pprint(getattr(manager, fname)(*sys.argv[2:]), indent=1)


if __name__ == '__main__':
    run_main()
