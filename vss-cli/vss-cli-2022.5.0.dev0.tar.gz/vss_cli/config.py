"""Configuration for VSS CLI (vss-cli)."""
from base64 import b64decode, b64encode
import functools
import json
import logging
import os
from pathlib import Path
import platform
import sys
from time import sleep
from typing import (  # noqa: F401
    Any, Callable, Dict, List, Optional, Tuple, Union, cast)

import click
from click_spinner import Spinner, spinner
import jwt
from pick import pick
from pyvss.const import __version__ as pyvss_version
from pyvss.enums import RequestStatus
from pyvss.exceptions import VssError
from pyvss.manager import VssManager
from ruamel.yaml import YAML

import vss_cli.const as const
from vss_cli.data_types import ConfigEndpoint, ConfigFile, ConfigFileGeneral
from vss_cli.exceptions import VssCliError
from vss_cli.helper import (
    bytes_to_str, debug_requests_on, format_output, get_hostname_from_url)
from vss_cli.utils.emoji import EMOJI_UNICODE
from vss_cli.utils.threading import WorkerQueue
from vss_cli.validators import (
    validate_email, validate_phone_number, validate_uuid, validate_vm_moref)
import vss_cli.yaml as yaml

_LOGGING = logging.getLogger(__name__)


class Configuration(VssManager):
    """The configuration context for the VSS CLI."""

    def __init__(self, tk: str = '') -> None:
        """Initialize the configuration."""
        super().__init__(tk)
        self.user_agent = self._default_user_agent(
            extensions=f'pyvss/{pyvss_version}'
        )
        self.verbose = False  # type: bool
        self.default_endpoint_name = None  # type: Optional[str]
        # start of endpoint settings
        self._endpoint = const.DEFAULT_ENDPOINT  # type: str
        self.base_endpoint = self.endpoint  # type: str
        self.endpoint_name = const.DEFAULT_ENDPOINT_NAME
        # end of endpoint settings
        self.history = const.DEFAULT_HISTORY  # type: str
        self.s3_server = None  # type: Optional[str]
        self._s3_server = const.DEFAULT_S3_SERVER  # type: str
        self.username = None  # type: Optional[str]
        self.password = None  # type: Optional[str]
        self.totp = None  # type: Optional[str]
        self.token = None  # type: Optional[str]
        self.timeout = None  # type: Optional[int]
        self._debug = False  # type: Optional[bool]
        self.showexceptions = False  # type: bool
        self.columns = None  # type: Optional[List[Tuple[str, str]]]
        self.columns_width = None  # type: Optional[int]
        self.no_headers = False  # type: Optional[bool]
        self.table_format = None  # type: Optional[str]
        self.sort_by = None  # type: Optional[str]
        self.output = None  # type: Optional[str]
        self.config_path = None  # type: Optional[str]
        self.check_for_updates = None  # type: Optional[bool]
        self.check_for_messages = None  # type: Optional[bool]
        self.wait_for_requests = None  # type: Optional[bool]
        self.config_file = None  # type: Optional[ConfigFile]
        self.spinner = spinner
        self.wait = None  # type: Optional[bool]
        self.moref = None  # type: Optional[str]
        self.unit = None  # type: Optional[str, int]
        self.payload_options = {}  # type: Optional[Dict]
        self.tmp = None  # type: Optional[Any]

    def set_dry_run(self, val: bool) -> None:
        """Set dry_run value."""
        if val is True:
            if self.output not in ['json', 'yaml']:
                self.output = 'json'
            self.wait = not bool(val)
            self.dry_run = bool(val)

    @property
    def debug(self) -> bool:
        """Return debug status."""
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Set on debug_requests if True."""
        if value:
            debug_requests_on()
        self._debug = value

    @property
    def endpoint(self) -> str:
        """Return endpoint value."""
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        """Rebuild API endpoints."""
        self._endpoint = value
        self.base_endpoint = value
        self.api_endpoint = f'{value}/v2'
        self.token_endpoint = f'{value}/auth/request-token'
        self.tf_endpoint = f'{value}/tf'
        if value:
            self.endpoint_name = get_hostname_from_url(
                value, const.DEFAULT_HOST_REGEX
            )

    def set_defaults(self) -> None:
        """Set default configuration settings."""
        _LOGGING.debug('Setting default configuration.')
        for setting, default in const.DEFAULT_SETTINGS.items():
            if getattr(self, setting) is None:
                setattr(self, setting, default)
        _LOGGING.debug(self)

    def get_token(
        self,
        user: Optional[str] = '',
        password: Optional[str] = '',
        otp: Optional[str] = None,
    ) -> str:
        """Generate token and returns value."""
        self.api_token = super().get_token(user, password, otp)
        _LOGGING.debug(f'Token generated successfully: {self.api_token}')
        return self.api_token

    def update_endpoints(self, endpoint: str = '') -> None:
        """Rebuild API endpoints."""
        self.base_endpoint = endpoint
        self.api_endpoint = f'{endpoint}/v2'
        self.token_endpoint = f'{endpoint}/auth/request-token'
        self.tf_endpoint = f'{endpoint}/tf'

    def echo(self, msg: str, *args: Optional[Any]) -> None:
        """Put content message to stdout."""
        self.log(msg, *args)

    def log(  # pylint: disable=no-self-use
        self, msg: str, *args: Optional[str]
    ) -> None:  # pylint: disable=no-self-use
        """Log a message to stdout."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stdout)

    def secho(self, msg: str, *args: Optional[Any], **kwargs) -> None:
        """Put content message to stdout with style."""
        self.slog(msg, *args, **kwargs)

    def slog(  # pylint: disable=no-self-use
        self, msg: str, *args: Optional[str], **kwargs
    ) -> None:  # pylint: disable=no-self-use
        """Log a message to stdout with style."""
        file = sys.stdout
        if args:
            msg %= args
        if 'file' in kwargs:
            file = kwargs['file']
            del kwargs['file']
        click.secho(msg, file=file, **kwargs)

    def vlog(self, msg: str, *args: Optional[str]) -> None:
        """Log a message only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)

    def __repr__(self) -> str:
        """Return the representation of the Configuration."""
        view = {
            "endpoint": self.endpoint,
            "default_endpoint_name": self.default_endpoint_name,
            "endpoint_name": self.endpoint_name,
            "access_token": 'yes' if self.token is not None else 'no',
            "user": 'yes' if self.username is not None else 'no',
            "user_password": 'yes' if self.password is not None else 'no',
            "tf_enabled": 'yes' if self.tf_enabled is not None else 'no',
            "output": self.output,
            "timeout": self.timeout,
            "debug": self.debug,
            "verbose": self.verbose,
            "wait": self.wait,
            "dry_run": self.dry_run,
            "s3_server": self.s3_server,
        }

        return f"<Configuration({view})"

    def auto_output(self, auto_output: str) -> str:
        """Configure output format."""
        if self.output == "auto":
            if auto_output == 'data':
                auto_output = const.DEFAULT_RAW_OUTPUT
            _LOGGING.debug(f"Setting auto-output to: {auto_output}")
            self.output = auto_output
        return self.output

    @staticmethod
    def _default_user_agent(
        name: str = const.PACKAGE_NAME,
        version: str = const.__version__,
        extensions: str = '',
    ) -> str:
        """Set default user agent."""
        # User-Agent:
        # <product>/<version> (<system-information>)
        # <platform> (<platform-details>) <extensions>
        user_agent = (
            f'{name}/{version} '
            f'({platform.system()}/{platform.release()}) '
            f'Python/{platform.python_version()} '
            f'({platform.platform()}) {extensions}'
        )
        return user_agent

    def set_credentials(
        self,
        username: str,
        password: str,
        token: str,
        endpoint: str,
        name: str,
    ) -> None:
        """Set credentials.

        Username, password, Token, endpoint name.
        Useful for configuration purposes.
        """
        self.username = username
        self.password = password
        self.api_token = token
        self.token = token
        self.endpoint = endpoint
        self.endpoint_name = name
        return

    def load_profile(
        self, endpoint: str = None
    ) -> Tuple[Optional[ConfigEndpoint], Optional[str], Optional[str]]:
        """Load profile from configuration file."""
        username, password = None, None
        # load from
        config_endpoint = self.config_file.get_endpoint(endpoint)
        if config_endpoint:
            # get auth attr
            auth = config_endpoint[0].auth
            # get token attr
            token = config_endpoint[0].token
            if not auth or not token:
                _LOGGING.warning('Invalid configuration endpoint found.')
            else:
                auth_enc = auth.encode()
                credentials_decoded = b64decode(auth_enc)
                # get user/pass
                username, password = credentials_decoded.split(b':')
            return (
                config_endpoint[0],
                bytes_to_str(username),
                bytes_to_str(password),
            )
        else:
            return None, bytes_to_str(username), bytes_to_str(password)

    def load_config_file(
        self, config: Union[Path, str] = None
    ) -> Optional[ConfigFile]:
        """Load raw configuration file and return ConfigFile object."""
        raw_config = self.load_raw_config_file(config=config)
        self.config_file = ConfigFile.from_json(raw_config)
        return self.config_file

    def load_raw_config_file(
        self, config: Optional[Union[Path, str]] = None
    ) -> Optional[str]:
        """Load raw configuration file from path."""
        config_file = config or self.config_path
        try:
            if isinstance(config_file, str):
                config_file = Path(config_file)
            cfg_dict = self.yaml_load(config_file)
            return json.dumps(cfg_dict)
        except ValueError as ex:
            _LOGGING.error(f'Error loading configuration file: {ex}')
            raise VssCliError(
                'Invalid configuration file.'
                'Run "vss-cli configure mk" or '
                '"vss-cli configure upgrade" to upgrade '
                'legacy configuration.'
            )

    def load_config(
        self, validate: bool = True, spinner_cls: Optional[Spinner] = None
    ) -> Optional[Tuple[str, str, str]]:
        """Load configuration and validate.

        Load configuration either from previously set
        ``username`` and ``password`` or ``token``.
        """
        try:
            # input configuration check
            if self.token or (self.username and self.password):
                # setting defaults if required
                self.set_defaults()
                _LOGGING.debug('Loading from input')
                # don't load config_path file
                if self.token:
                    _LOGGING.debug('Checking token')
                    # set api token
                    self.api_token = self.token
                    return self.username, self.password, self.api_token
                elif self.username and self.password:
                    _LOGGING.debug('Checking user/pass to generate token')
                    # generate a new token - won't save
                    _LOGGING.warning(
                        'A new token will be generated but not persisted. '
                        'Consider running command "configure mk" to save your '
                        'credentials.'
                    )
                    self.get_token(self.username, self.password, self.totp)
                    return self.username, self.password, self.api_token
                else:
                    raise VssCliError(
                        'Environment variables error. Please, verify '
                        'VSS_TOKEN or VSS_USER and VSS_USER_PASS'
                    )
            else:
                cfg_path = Path(self.config_path)
                _LOGGING.debug(
                    f'Loading configuration file: {self.config_path}'
                )
                if cfg_path.is_file():
                    # load configuration file from json string into class
                    self.config_file = self.load_config_file(config=cfg_path)
                    # general area
                    if self.config_file.general:
                        _LOGGING.debug(
                            f'Loading general settings from {self.config_path}'
                        )
                        # set config_path defaults
                        for setting in const.GENERAL_SETTINGS:
                            try:
                                # check if setting hasn't been set
                                # by input or env
                                # which overrides configuration file
                                if getattr(self, setting) is None:
                                    setattr(
                                        self,
                                        setting,
                                        getattr(
                                            self.config_file.general, setting
                                        ),
                                    )
                                else:
                                    _LOGGING.debug(
                                        f'Prioritizing {setting} from '
                                        f'command line input.'
                                    )
                            except KeyError as ex:
                                _LOGGING.warning(
                                    f'Could not load general setting'
                                    f' {setting}: {ex}'
                                )
                        # printing out
                        _LOGGING.debug(f"General settings loaded: {self}")
                    # load preferred endpoint from file if any
                    if self.config_file.endpoints:
                        _LOGGING.debug(
                            f'Loading endpoint settings from '
                            f'{self.config_path}'
                        )
                        _LOGGING.debug(
                            f'Looking for endpoint={self.endpoint},'
                            f' default_endpoint_name='
                            f'{self.default_endpoint_name}'
                        )
                        # 1. provided by input
                        if self.endpoint:
                            msg = (
                                f'Cloud not find endpoint provided by '
                                f'input {self.endpoint}. \n'
                            )
                            # load endpoint from endpoints
                            ep, usr, pwd = self.load_profile(self.endpoint)
                        # 2. provided by configuration file
                        #    (default_endpoint_name)
                        elif self.default_endpoint_name:
                            msg = (
                                f'Could not find default endpoint '
                                f'{self.default_endpoint_name}. \n'
                            )
                            # load endpoint from endpoints
                            ep, usr, pwd = self.load_profile(
                                self.default_endpoint_name
                            )
                        # 3. fallback to default settings
                        else:
                            msg = (
                                f"Invalid endpoint {self.endpoint_name} "
                                f"configuration. \n"
                            )
                            ep, usr, pwd = self.load_profile(
                                self.endpoint_name
                            )
                        # check valid creds
                        if not (usr and pwd or getattr(ep, 'token', None)):
                            _LOGGING.warning(msg)
                            default_endpoint = const.DEFAULT_ENDPOINT_NAME
                            _LOGGING.warning(
                                f'Falling back to {default_endpoint}'
                            )
                            (ep, usr, pwd,) = self.load_profile(  # NOQA: E501
                                endpoint=const.DEFAULT_ENDPOINT_NAME
                            )
                        # set config_path data
                        self.set_credentials(
                            usr, pwd, ep.token, ep.url, ep.name,
                        )
                        if validate:
                            # last check cred
                            creds = self.username and self.password
                            if not (creds or self.api_token):
                                raise VssCliError(
                                    'Run "vss-cli configure mk" to add '
                                    'endpoint to configuration file or '
                                    '"vss-cli configure upgrade" to upgrade '
                                    'legacy configuration.'
                                )
                            _LOGGING.debug(
                                f'Loaded from file: {self.endpoint_name}: '
                                f'{self.endpoint}:'
                                f': {self.username}'
                            )
                            try:
                                self.whoami()
                                _LOGGING.debug('Token validated successfully.')
                            except Exception as ex:
                                self.vlog(str(ex))
                                _LOGGING.debug('Generating a new token')
                                self.api_token = self._get_token_with_mfa(
                                    spinner_cls=spinner_cls
                                )
                                endpoint = self._create_endpoint_config(
                                    token=self.api_token
                                )
                                self.write_config_file(new_endpoint=endpoint)
                                # check for updates
                                if self.check_for_updates:
                                    self.check_available_updates()
                                # check for unread messages
                                if self.check_for_messages:
                                    self.check_unread_messages()
                        return self.username, self.password, self.api_token
                else:
                    self.set_defaults()
            raise VssCliError(
                'Invalid configuration. Please, run '
                '"vss-cli configure mk" to initialize configuration, or '
                '"vss-cli configure upgrade" to upgrade legacy '
                'configuration.'
            )
        except Exception as ex:
            raise VssCliError(str(ex))

    def check_available_updates(self) -> None:
        """Check available update from PyPI."""
        try:
            _LOGGING.debug('Checking for available updates.')
            cmd_bin = sys.executable
            # create command with the right exec
            pip_cmd = f'{cmd_bin} -m pip list --outdated'.split(None)
            from subprocess import Popen, PIPE

            p = Popen(pip_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            out_decoded = out.decode('utf-8')
            # verify if package name is in outdated string
            pkg_name = const.PACKAGE_NAME.replace('_', '-')
            if pkg_name in out_decoded:
                lines = out_decoded.split('\n')
                pkg_line = [line for line in lines if pkg_name in line]
                if pkg_line:
                    pkg_line = pkg_line.pop()
                    pkg, current, latest, pkgn = pkg_line.split(None)
                    self.secho(
                        f'Update available {current} -> {latest} '
                        f'{EMOJI_UNICODE.get(":upwards_button:")}.',
                        file=sys.stderr,
                        fg='green',
                        nl=False,
                    )
                    self.secho(' Run ', file=sys.stderr, fg='green', nl=False)
                    self.secho(
                        'vss-cli upgrade', file=sys.stderr, fg='red', nl=False
                    )
                    self.secho(
                        ' to install latest. \n', file=sys.stderr, fg='green'
                    )
            else:
                self.secho(
                    f'Running latest version {const.__version__} '
                    f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}\n',
                    file=sys.stderr,
                    fg='green',
                )
        except Exception as ex:
            _LOGGING.error(f'Could not check for updates: {ex}')

    def check_unread_messages(self) -> None:
        """Check unread API messages."""
        try:
            _LOGGING.debug('Checking for unread messages')
            messages = self.get_user_messages(
                filter='status,eq,Created', per_page=100
            )
            n_messages = len(messages)
            if messages:
                self.secho(
                    f'You have {n_messages} unread messages '
                    f'{EMOJI_UNICODE.get(":envelope_with_arrow:")} ',
                    file=sys.stderr,
                    fg='green',
                    nl=False,
                )
                self.secho('Run ', file=sys.stderr, fg='green', nl=False)
                self.secho(
                    'vss-cli message ls -f status=Created',
                    file=sys.stderr,
                    fg='red',
                    nl=False,
                )
                self.secho(
                    ' to list unread messages.', file=sys.stderr, fg='green'
                )
            else:
                _LOGGING.debug('No messages with Created status')
        except Exception as ex:
            _LOGGING.error(f'Could not check for messages: {ex}')

    def _get_token_with_mfa(
        self,
        token: Optional[str] = None,
        spinner_cls: Optional[Spinner] = None,
    ):
        """Get token with MFA."""
        try:
            token = token or self.get_token(
                self.username, self.password, self.totp
            )
        except VssError as ex:
            if (
                500 > ex.http_code > 399
                and 'InvalidParameterValue: otp' in ex.message
            ):
                # try MFA Auth
                try:
                    _LOGGING.debug('Requesting a new timed one-time password')
                    _ = self.request_totp(self.username, self.password)
                except Exception as exc:
                    _LOGGING.warning(f'Requesting totp: {exc}')
                    pass
                if spinner_cls is not None:
                    spinner_cls.stop()
                self.totp = click.prompt(
                    'MFA enabled. Provide Timed One-Time Password'
                )
                if spinner_cls is not None:
                    spinner_cls.start()
                try:
                    token = token or self.get_token(
                        self.username, self.password, self.totp
                    )
                except Exception as exc:
                    _LOGGING.warning(f'Could not generate new token: {exc}')
                    raise exc
            else:
                raise ex
        return token

    def _create_endpoint_config(self, token: str = None) -> ConfigEndpoint:
        """Create endpoint configuration for a given token.

        Token might be ``None`` and will generate a new one
        using ``username`` and ``password``.
        """
        token = self._get_token_with_mfa(token=token)
        # encode or save
        username = (
            self.username
            if isinstance(self.username, bytes)
            else self.username.encode()
        )
        password = (
            self.password
            if isinstance(self.password, bytes)
            else self.password.encode()
        )
        credentials = b':'.join([username, password])
        auth = b64encode(credentials).strip().decode('utf-8')
        # decode jwt to verify if otp is enabled.
        payload = jwt.decode(
            self.api_token, options=dict(verify_signature=False)
        )
        endpoint_cfg = {
            'url': self.base_endpoint,
            'name': self.endpoint_name,
            'auth': auth,
            'token': self.api_token,
            'tf_enabled': payload.get('otp', False),
        }
        ep_cfg = ConfigEndpoint.from_json(json.dumps(endpoint_cfg))
        _LOGGING.debug(f'Configuration endpoint created: {ep_cfg}')
        return ep_cfg

    def load_config_template(self) -> ConfigFile:
        """Load configuration from template."""
        # load template in case it fails
        cfg_default_path = Path(const.DEFAULT_CONFIG_TMPL)
        with cfg_default_path.open() as f:
            config_tmpl = yaml.load_yaml(self.yaml(), f)
            raw_config_tmpl = json.dumps(config_tmpl)
            config_file_tmpl = ConfigFile.from_json(raw_config_tmpl)
        return config_file_tmpl

    def write_config_file(
        self,
        new_config_file: Optional[ConfigFile] = None,
        new_endpoint: Optional[ConfigEndpoint] = None,
        config_general: Optional[ConfigFileGeneral] = None,
    ) -> bool:
        """Create or update configuration endpoint section."""
        # load template in case it fails
        config_file_tmpl = self.load_config_template()
        try:
            _LOGGING.debug(f'Writing configuration file: {self.config_path}')
            cfg_path = Path(self.config_path)
            # validate if file exists
            if cfg_path.is_file():
                with cfg_path.open(mode='r+') as fp:
                    try:
                        _conf_dict = yaml.load_yaml(self.yaml(), fp)
                        raw_config = json.dumps(_conf_dict)
                        config_file = ConfigFile.from_json(raw_config)
                    except (ValueError, TypeError) as ex:
                        _LOGGING.warning(f'Invalid config_path file: {ex}')
                        if click.confirm(
                            'An error occurred loading the '
                            'configuration file. '
                            'Would you like to recreate it?',
                            err=True,
                        ):
                            config_file = config_file_tmpl
                        else:
                            return False
                    if new_config_file:
                        config_file.general = new_config_file.general
                        config_file.update_endpoints(
                            *new_config_file.endpoints
                        )
                    # update general config_path if required
                    if config_general:
                        config_file.general = config_general
                    # update endpoint if required
                    if new_endpoint:
                        # update endpoint
                        config_file.update_endpoint(new_endpoint)
                    # dumping and loading
                    _conf_dict = json.loads(config_file.to_json())
                    fp.seek(0)
                    yaml.dump_yaml(self.yaml(), _conf_dict, stream=fp)
                    fp.truncate()
                _LOGGING.debug(
                    f'Configuration file {self.config_path} has been updated'
                )
            else:
                if new_config_file:
                    f_type = 'Config file'
                    config_file_dict = json.loads(new_config_file.to_json())
                else:
                    # New configuration file. A new endpoint must be configured
                    f_type = 'Default template'
                    config_endpoint = (
                        new_endpoint or self._create_endpoint_config()
                    )
                    config_file_tmpl.update_endpoint(config_endpoint)
                    # load and dump
                    config_file_dict = json.loads(config_file_tmpl.to_json())
                # write file
                with cfg_path.open(mode='w') as fp:
                    yaml.dump_yaml(self.yaml(), config_file_dict, stream=fp)
                _LOGGING.debug(
                    f'New {f_type} has been written to {self.config_path}.'
                )
        except OSError as e:
            raise Exception(
                f'An error occurred writing ' f'configuration file: {e}'
            )
        return True

    def configure(
        self,
        username: str,
        password: str,
        endpoint: str,
        replace: Optional[bool] = False,
        endpoint_name: Optional[str] = None,
    ) -> bool:
        """Configure endpoint with provided settings."""
        self.username = username
        self.password = password
        # update instance endpoints if provided
        self.endpoint = endpoint
        if endpoint_name:
            self.endpoint_name = endpoint_name
        # directory available
        cfg_path = Path(self.config_path)
        if not cfg_path.parent.is_dir():
            cfg_path.parent.mkdir()
        # config_path file
        if cfg_path.is_file():
            try:
                self.config_file = self.load_config_file()
                # load credentials by endpoint_name
                (
                    config_endpoint,
                    e_username,
                    e_password,
                ) = self.load_profile(  # NOQA: E501c
                    endpoint=self.endpoint_name
                )
                # profile does not exist
                if not (e_username and e_password and config_endpoint.token):
                    self.echo(
                        f'Endpoint {self.endpoint_name} not found. '
                        f'Creating...'
                    )
                    endpoint_cfg = self._create_endpoint_config()
                    self.write_config_file(new_endpoint=endpoint_cfg)
                # profile exists
                elif e_username and e_password and config_endpoint.token:
                    username = bytes_to_str(e_username) if e_username else ''
                    confirm = replace or click.confirm(
                        f"Would you like to replace existing configuration?\n "
                        f"{self.endpoint_name}:"
                        f"{username}: {config_endpoint.url}",
                        err=True,
                    )
                    if confirm:
                        endpoint_cfg = self._create_endpoint_config()
                        self.write_config_file(new_endpoint=endpoint_cfg)
                    else:
                        return False
            except Exception as ex:
                _LOGGING.warning(f'Invalid config_path file: {ex}')
                confirm = click.confirm(
                    'An error occurred loading the '
                    'configuration file. '
                    'Would you like to recreate it?',
                    err=True,
                )
                if confirm:
                    endpoint_cfg = self._create_endpoint_config()
                    return self.write_config_file(new_endpoint=endpoint_cfg)
                else:
                    return False
            # feedback
            self.echo(
                f'Successfully configured credentials for ' f'{self.endpoint}.'
            )
        else:
            endpoint_cfg = self._create_endpoint_config()
            self.write_config_file(new_endpoint=endpoint_cfg)
        return True

    @staticmethod
    def _filter_objects_by_attrs(
        value: str, objects: List[dict], attrs: List[Tuple[Any, Any]]
    ) -> List[Any]:
        """Filter objects by a given `value` based on attributes.

        Attributes may be a list of tuples with attribute name, type.

        :param value: value to filter
        :param objects: list of dictionaries
        :param attrs: list of tuple of attribute name, type
        :return:
        """
        _objs = []
        for attr in attrs:
            attr_name = attr[0]
            attr_type = attr[1]
            try:
                if attr_type in [str]:
                    f = filter(
                        lambda i: attr_type(value).lower()
                        in i[attr_name].lower(),
                        objects,
                    )
                elif attr_type in [int]:
                    f = filter(
                        lambda i: attr_type(value) == i[attr_name], objects
                    )
                else:
                    f = filter(
                        lambda i: attr_type(value) in i[attr_name], objects
                    )
                # cast list
                _objs = list(f)
            except ValueError as ex:
                _LOGGING.debug(f'{value} ({type(value)}) error: {ex}')

            if _objs:
                break
        return _objs

    @staticmethod
    def pick(objects: List[Dict], options=None, indicator='=>'):
        """Show a ``picker`` for a list of dicts."""
        count = len(objects)
        msg = f"Found {count} matches. Please select one:"
        sel, index = pick(
            title=msg, indicator=indicator, options=options or objects
        )
        return [objects[index]]

    def get_vskey_stor(self, **kwargs) -> bool:
        """Create s3 client to interact with remote minIO."""
        try:
            from minio import Minio
        except ImportError:
            raise VssCliError(
                'minio dependency not found. '
                'try running "pip install vss-cli[stor]"'
            )

        super().get_vskey_stor(
            user=self.username,
            password=self.password,
            s3_endpoint=self.s3_server,
        )
        _LOGGING.debug(
            f's3_endpoint={self.vskey_stor_s3api} '
            f'vskey_stor_s3_gui={self.vskey_stor_s3_gui}'
        )
        return self.vskey_stor

    def get_vm_by_id_or_name(self, vm_id: str, silent=False) -> Optional[List]:
        """Get virtual machine by identifier or name."""
        is_moref = validate_vm_moref('', '', vm_id)
        is_uuid = validate_uuid('', '', vm_id)
        _LOGGING.debug(f'is_moref={is_moref}, is_uuid={is_uuid}')
        if is_moref or is_uuid:
            if is_moref:
                attr = 'moref'
            else:
                attr = 'uuid'
            filters = f'{attr},eq,{vm_id}'
            v = self.get_vms(filter=filters)
            if not v:
                # try template
                v = self.get_templates(filter=filters)
                if not v:
                    if silent:
                        return None
                    else:
                        raise click.BadArgumentUsage(
                            f'vm id {vm_id} could not be found'
                        )
            return v
        else:
            _LOGGING.debug(f'not a moref or uuid {vm_id}')
            # If it's a value error, then the string
            # is not a valid hex code for a UUID.
            # get vm by name
            g_vms = self.get_vms(per_page=3000)
            vm_id = vm_id.lower()
            v = list(filter(lambda i: vm_id in i['name'].lower(), g_vms))
            if not v:
                # try templates:
                g_tmpls = self.get_templates(per_page=2500)
                v = list(filter(lambda i: vm_id in i['name'].lower(), g_tmpls))
                if not v:
                    raise click.BadParameter(f'{vm_id} could not be found')
            v_count = len(v)
            if v_count > 1:
                msg = f"Found {v_count} matches. Please select one:"
                sel, index = pick(
                    title=msg,
                    indicator='=>',
                    options=[
                        f"({i['moref']}) {i['folder']['path']} > {i['name']}"
                        for i in v
                    ],
                )
                return [v[index]]
            return v

    def get_vm_snapshot_by_id_name_or_desc(
        self, vm_id: str, id_name_or_desc: str
    ) -> List[Dict]:
        """Get vm snapshot by id name or description."""
        snapshots = self.get_vm_snapshots(vm_id)
        attributes = [('id', int), ('name', str), ('description', str)]
        objs = self._filter_objects_by_attrs(
            id_name_or_desc, snapshots, attributes
        )
        if not objs:
            raise click.BadParameter(f'{id_name_or_desc} could not be found')
        d_count = len(objs)
        if d_count > 1:
            return self.pick(
                objs,
                options=[f"{i['name']} ({i['description']})" for i in objs],
            )
        return objs

    def get_domain_by_name_or_moref(self, name_or_moref: str) -> List[Dict]:
        """Get domain by name or mo reference."""
        g_domains = self.get_domains()
        attributes = [('name', str), ('moref', str)]
        objs = self._filter_objects_by_attrs(
            name_or_moref, g_domains, attributes
        )
        if not objs:
            raise click.BadParameter(f'{name_or_moref} could not be found')
        d_count = len(objs)
        if d_count > 1:
            return self.pick(
                objs, options=[f"{i['name']} ({i['moref']})" for i in objs]
            )
        return objs

    def get_network_by_name_or_moref(self, name_or_moref: str) -> List[Dict]:
        """Get network by name or mo reference."""
        g_networks = self.get_networks(
            sort='name,desc', show_all=True, per_page=500
        )
        attributes = [('name', str), ('moref', str)]
        objs = self._filter_objects_by_attrs(
            name_or_moref, g_networks, attributes
        )
        if not objs:
            raise click.BadParameter(f'{name_or_moref} could not be found')
        net_count = len(objs)
        if net_count > 1:
            return self.pick(
                objs, options=[f"{i['name']} ({i['moref']})" for i in objs]
            )
        return objs

    def get_folder_by_name_or_moref_path(
        self, name_moref_path: str, silent: bool = False
    ) -> List[Dict]:
        """Get domain by name or mo reference."""
        g_folders = self.get_folders(
            sort='path,desc', show_all=True, per_page=500
        )
        # search by name or moref
        attributes = [('name', str), ('path', str), ('moref', str)]
        objs = self._filter_objects_by_attrs(
            name_moref_path, g_folders, attributes
        )
        if not objs and not silent:
            raise click.BadParameter(f'{name_moref_path} could not be found')
        obj_count = len(objs)
        if obj_count > 1:
            return self.pick(
                objs, options=[f"{i['path']} ({i['moref']})" for i in objs]
            )
        return objs

    def get_os_by_name_or_guest(self, name_or_guest: str) -> List[Dict]:
        """Get operating system by name, ``guest_id`` or ``full_name``."""
        g_os = self.get_os(
            sort='guestFullName,desc', show_all=True, per_page=500
        )
        attributes = [('id', int), ('guest_id', str), ('full_name', str)]
        objs = self._filter_objects_by_attrs(name_or_guest, g_os, attributes)
        if not objs:
            raise click.BadParameter(f'{name_or_guest} could not be found')
        o_count = len(objs)
        if o_count > 1:
            return self.pick(
                objs,
                options=[f"{i['full_name']} ({i['guest_id']})" for i in objs],
            )
        return objs

    def get_vss_service_by_name_label_or_id(
        self, name_label_or_id: Union[str, int]
    ) -> List[Dict]:
        """Get service by name label or identifier."""
        vss_services = self.get_vss_services(
            sort='label,desc', show_all=True, per_page=200
        )
        attributes = [('id', int), ('label', str), ('name', str)]
        objs = self._filter_objects_by_attrs(
            name_label_or_id, vss_services, attributes
        )
        # check if there's no ref
        if not objs:
            raise click.BadParameter(f'{name_label_or_id} could not be found')
        # count for dup results
        o_count = len(objs)
        if o_count > 1:
            return self.pick(objs, options=[f"{i['label']}" for i in objs])
        return objs

    def get_vss_groups_by_name_desc_or_id(
        self, name_desc_or_id: Union[str, int]
    ) -> List[Dict]:
        """Get groups by name, description or identifier."""
        vss_groups = self.get_user_groups(
            sort='name,desc', show_all=True, per_page=100
        )
        attributes = [('id', int), ('name', str), ('description', str)]
        objs = self._filter_objects_by_attrs(
            name_desc_or_id, vss_groups, attributes
        )
        # check if there's no ref
        if not objs:
            raise click.BadParameter(f'{name_desc_or_id} could not be found')
        # count for dup results
        o_count = len(objs)
        if o_count > 1:
            return self.pick(
                objs,
                options=[
                    f"{i['name']} ({i['id']}): {i['description'][:40]}... "
                    for i in objs
                ],
            )
        return objs

    def _get_images_by_name_path_or_id(
        self, f: Callable, name_or_path_or_id: Union[int, str]
    ) -> List[Dict]:
        """Get images by name path or identifier."""
        g_img = f(show_all=True, per_page=500)
        attributes = [('id', int), ('name', str), ('path', str)]
        objs = self._filter_objects_by_attrs(
            name_or_path_or_id, g_img, attributes
        )
        # check if there's no ref
        if not objs:
            raise click.BadParameter(
                f'{name_or_path_or_id} could not be found'
            )
        # count for dup results
        o_count = len(objs)
        if o_count > 1:
            return self.pick(objs, options=[f"{i['name']}" for i in objs])
        return objs

    def get_vmdk_by_name_path_or_id(
        self, name_or_path_or_id: Union[str, int]
    ) -> List[Any]:
        """Get vmdk by name, path or id."""
        return self._get_images_by_name_path_or_id(
            self.get_user_vmdks, name_or_path_or_id
        )

    def get_floppy_by_name_or_path(
        self, name_or_path_or_id: Union[str, int]
    ) -> List[Dict]:
        """Get Floppy image by name, path or identifier."""
        return self._get_images_by_name_path_or_id(
            self.get_floppies, name_or_path_or_id
        )

    def get_iso_by_name_or_path(
        self, name_or_path_or_id: Union[str, int]
    ) -> List[Any]:
        """Get ISO image by name, path or identifier."""
        return self._get_images_by_name_path_or_id(
            self.get_isos, name_or_path_or_id
        )

    def get_clib_deployable_item_by_name_or_id_path(
        self, name_or_id_or_path: Union[str, int]
    ):
        """Get content library deployable items."""
        items = self.get_content_library_items(
            show_all=True,
            sort='path,desc',
            per_page=500,
            filter="type,in,OVF,VM_TEMPLATE",
        )
        attrs = [('id', int), ('name', str)]
        objs = self._filter_objects_by_attrs(name_or_id_or_path, items, attrs)
        # check if there's no ref
        if not objs:
            raise click.BadParameter(
                f'{name_or_id_or_path} could not be found'
            )
        # count for dup results
        o_count = len(objs)
        if o_count > 1:
            return self.pick(objs, options=[f"{i['name']}" for i in objs])
        return objs

    def get_vm_image_by_name_or_id_path(
        self, name_or_path_or_id: Union[str, int]
    ) -> List[Any]:
        """Get VM image by name, path or identifier."""
        return self._get_images_by_name_path_or_id(
            self.get_images, name_or_path_or_id
        )

    def _get_types_by_name(self, name: Union[str, int], types_f, attrs=None):
        g_types = types_f(only_type=False)
        attributes = attrs or [('type', str)]
        objs = self._filter_objects_by_attrs(str(name), g_types, attributes)
        # check if there's no ref
        if not objs:
            raise click.BadParameter(f'{name} could not be found')
        # count for dup results
        o_count = len(objs)
        if o_count > 1:
            return self.pick(
                objs,
                options=[
                    f"{i['type']} - {i['description'][:100]}..." for i in objs
                ],
            )
        return objs

    def get_vm_scsi_type_by_name(self, name: Union[str, int]):
        """Get SCSI type by name."""
        return self._get_types_by_name(
            name, self.get_supported_scsi_controllers
        )

    def get_vm_scsi_sharing_by_name(self, name: Union[str, int]):
        """Get SCSI sharing by name."""
        return self._get_types_by_name(name, self.get_supported_scsi_sharing)

    def get_vm_disk_backing_mode_by_name(self, name: Union[str, int]):
        """Get Disk Backing Mode by name."""
        return self._get_types_by_name(
            name, self.get_supported_disk_backing_modes
        )

    def get_vm_disk_backing_sharing_by_name(self, name: Union[str, int]):
        """Get Disk Sharing Mode by name."""
        return self._get_types_by_name(name, self.get_supported_disk_sharing)

    def get_vm_firmware_by_type_or_desc(self, name: Union[str, int]):
        """Get VM firmware by name."""
        return self._get_types_by_name(
            name,
            self.get_supported_firmware_types,
            attrs=[('type', str), ('description', str)],
        )

    def get_vm_nic_type_by_name(self, name: Union[str, int]):
        """Get VM NIC type by name."""
        g_types = self.get_supported_nic_types(only_type=False)
        attributes = [('type', str)]
        objs = self._filter_objects_by_attrs(name, g_types, attributes)
        # check if there's no ref
        if not objs:
            raise click.BadParameter(f'{name} could not be found')
        # count for dup results
        o_count = len(objs)
        if o_count > 1:
            return self.pick(
                objs,
                options=[
                    f"{i['type']} - {i['description'][:100]}..." for i in objs
                ],
            )
        return objs

    def get_cli_spec_from_api_spec(
        self, payload: dict, template: dict
    ) -> Dict:
        """Get CLI specification from API specification."""
        os_q = self.get_os(filter=f"guest_id,eq,{payload.get('os')}")
        machine_os = os_q[0]['full_name'] if os_q else payload.get('os')
        fo_q = self.get_folder(payload.get('folder'))
        machine_folder = fo_q['path'] if fo_q else payload.get('folder')
        template['built'] = payload.get('built_from')
        template['machine']['name'] = payload.get('name')
        template['machine']['os'] = machine_os
        template['machine']['cpu'] = payload.get('cpu')
        template['machine']['memory'] = payload.get('memory')
        template['machine']['folder'] = machine_folder
        template['machine']['disks'] = payload.get('disks')
        template['networking']['interfaces'] = [
            {
                'network': self.get_network(v['network'])['name'],
                'type': v['type'],
            }
            for v in payload.get('networks')
        ]
        template['metadata']['client'] = payload.get('client')
        template['metadata']['description'] = payload.get('description')
        template['metadata']['usage'] = payload.get('usage')
        template['metadata']['inform'] = payload.get('inform')
        template['metadata']['admin'] = {
            'name': payload.get('admin_name'),
            'email': payload.get('admin_email'),
            'phone': payload.get('admin_phone'),
        }
        template['metadata']['vss_service'] = payload.get('vss_service')
        template['metadata']['vss_options'] = payload.get('vss_options')
        return template

    def get_api_spec_from_cli_spec(self, payload: dict, built: str) -> Dict:
        """Get API specification from CLI specification."""
        try:
            spec_payload = dict()
            # sections
            machine_section = payload['machine']
            networking_section = payload['networking']
            metadata_section = payload['metadata']
            if built == 'os_install':
                # machine section parse and update
                spec_payload.update(machine_section)
                # replace with valid values
                spec_payload['os'] = self.get_os_by_name_or_guest(
                    machine_section['os']
                )[0]['guest_id']
                spec_payload['iso'] = self.get_iso_by_name_or_path(
                    machine_section['iso']
                )[0]['path']
                # folder
                spec_payload['folder'] = self.get_folder_by_name_or_moref_path(
                    machine_section['folder']
                )[0]['moref']
                # networking
                spec_payload['networks'] = [
                    {
                        'network': self.get_network_by_name_or_moref(
                            n['network']
                        )[0]['moref'],
                        'type': n['type'],
                    }
                    for n in networking_section['interfaces']
                ]
                spec_payload['disks'] = [
                    {
                        "capacity_gb": d['capacity_gb'],
                        "backing_mode": self.get_vm_disk_backing_mode_by_name(
                            d['backing_mode']
                        )[0]['type']
                        if d.get('backing_mode')
                        else 'persistent',
                        "backing_sharing": self.get_vm_disk_backing_sharing_by_name(  # NOQA:
                            d['backing_sharing']
                        )[
                            0
                        ][
                            'type'
                        ]
                        if d.get('backing_sharing')
                        else 'sharingnone',
                    }
                    for d in machine_section['disks']
                ]
                # other
                machine_section['power_on'] = machine_section.get(
                    'power_on', False
                )
                # metadata section
                spec_payload.update(metadata_section)
                spec_payload['built'] = built
                spec_payload['client'] = metadata_section['client']
                # optional
                if metadata_section.get('inform') is not None:
                    spec_payload['inform'] = [
                        validate_email(None, 'inform', i)
                        for i in metadata_section['inform']
                    ]
                if metadata_section.get('vss_service') is not None:
                    service = self.get_vss_service_by_name_label_or_id(
                        metadata_section['vss_service']
                    )[0]['id']
                    spec_payload['vss_service'] = service
                if metadata_section.get('metadata_section') is not None:
                    admin_name = metadata_section['admin']['name']
                    admin_email = metadata_section['admin']['email']
                    admin_phone = metadata_section['admin']['phone']
                    if admin_name and admin_email and admin_phone:
                        validate_email(None, '', admin_email)
                        validate_phone_number(None, '', admin_phone)
                    spec_payload['admin'] = (
                        f"{admin_name}:" f"{admin_phone}:{admin_email}"
                    )
            return spec_payload
        except KeyError as ex:
            raise click.BadParameter(f'Invalid CLI specification: {ex}')

    def yaml(self) -> YAML:
        """Create default yaml parser."""
        if self:
            return yaml.yaml()

    def yaml_load(self, source: str) -> Any:
        """Load YAML from source."""
        return self.yaml().load(source)

    def yaml_dump(self, source: Any) -> str:
        """Dump dictionary to YAML string."""
        return cast(str, yaml.dump_yaml(self.yaml(), source))

    def yaml_dump_stream(
        self, data: Any, stream: Any = None, **kw: Any
    ) -> Optional[str]:
        """Dump yaml to stream."""
        return yaml.dump_yaml(self.yaml(), data, stream, **kw)

    def download_inventory_file(
        self, request_id: int, directory: str = ''
    ) -> Dict:
        """Download inventory file to a given directory."""
        with self.spinner(disable=self.debug):
            file_path = self.download_inventory_result(
                request_id=request_id, directory=directory
            )
        obj = {'file': file_path}

        self.echo(
            format_output(self, [obj], columns=[('FILE', 'file')], single=True)
        )
        return obj

    def wait_for_requests_to(
        self,
        obj,
        required: List[str] = (
            RequestStatus.PROCESSED.name,
            RequestStatus.SCHEDULED.name,
        ),
        wait: int = 5,
        max_tries: int = 720,
        in_multiple: bool = False,
    ):
        """Wait for multiple requests to complete."""
        if not in_multiple:
            objs = [
                dict(
                    _links=dict(request=r_url),
                    status=obj['status'],
                    request=dict(id=os.path.basename(r_url)),
                )
                for r_url in obj['_links']['request']
            ]
        else:
            objs = obj
        wq = WorkerQueue(max_workers=len(objs))

        with wq.join(debug=self.debug):
            for obj in objs:
                wq.put(
                    functools.partial(
                        self.wait_for_request_to,
                        obj=obj,
                        required=required,
                        wait=wait,
                        max_tries=max_tries,
                        threaded=True,
                    )
                )
                wq.spawn_worker()

    def wait_for_request_to(
        self,
        obj: dict,
        required: List[str] = (
            RequestStatus.PROCESSED.name,
            RequestStatus.SCHEDULED.name,
        ),
        wait: int = 5,
        max_tries: int = 720,
        threaded: bool = False,
    ) -> Optional[bool]:
        """Wait for request to given status."""
        # wait
        request_message = {}
        err_status = [
            RequestStatus.ERROR.name,
            RequestStatus.ERROR_RETRY.name,
            RequestStatus.CANCELLED.name,
        ]
        wait_status = [
            RequestStatus.PENDING.name,
            RequestStatus.IN_PROGRESS.name,
            RequestStatus.APPROVAL_REQUIRED.name,
        ]
        _LOGGING.debug(
            f'max tries={max_tries}, wait={wait}, '
            f'required status={",".join(required)}'
        )
        request_id = obj["request"]["id"]
        self.secho(
            f'{EMOJI_UNICODE.get(":hourglass_not_done:")} '
            f'Waiting for request {request_id} to complete... ',
            fg='green',
            nl=True,
        )
        # check for request status
        if 199 < obj['status'] < 300:
            pass
        else:
            raise VssCliError('Invalid response from the API.')
        with self.spinner(disable=self.debug or threaded):
            r_url = obj['_links']['request']
            tries = 0
            while True:
                request = self.request(r_url)
                if 'data' in request:
                    status = request['data']['status']
                    request_message = request['data']['message']
                    if status in required:
                        request_status = True
                        break
                    if status in err_status:
                        request_status = False
                        break
                    elif status in wait_status:
                        pass
                else:
                    request_status = False
                    break
                if tries >= max_tries:
                    raise VssCliError(
                        f'Wait for request timed out after '
                        f'{max_tries * wait} seconds.'
                    )
                tries += 1
                sleep(wait)
        # check result status
        request_message_str = format_output(
            self,
            [request_message],
            columns=const.COLUMNS_REQUEST_WAIT,
            single=True,
        )
        sys.stdout.flush()
        if request_status:
            self.secho(
                f'{EMOJI_UNICODE.get(":party_popper:")} '
                f'Request {request_id} completed successfully:',
                fg='green',
            )
            self.echo(f'{request_message_str}')
        else:
            self.secho(
                f'{EMOJI_UNICODE.get(":worried_face:")} '
                f'Request {request_id} completed with errors:',
                err=True,
                fg='red',
            )
            self.echo(f'{request_message_str}')
            return False
        return True
