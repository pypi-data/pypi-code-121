#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Create application instance from config files"""

import os
import re
import uuid
import logging
from pathlib import Path
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Text, Tuple, Union
from configparser import BasicInterpolation, ConfigParser, SectionProxy

from pydantic import BaseSettings, Extra, fields, validator
from pydantic.env_settings import SettingsSourceCallable


logger = logging.getLogger(__name__)

ENV_VAR_TEMPLATE = re.compile(r"^\${(.*)}$")

# Skill config default file name
SKILL_CONFIG_FILE = "skill.conf"

# Dotenv variables default file name
DOTENV_FILE = ".env"


class EnvVarInterpolation(BasicInterpolation):
    """
    Interpolation to expand environment variables in the format:

    [section]
    key = ${ENV_VAR:default}

    """

    def before_get(self, parser, section, option, value, defaults):
        """
        If value matches the template (${ENV_VAR:default}),
        extract the value from environment variable,
        or set it to default

        :param parser:
        :param section:
        :param option:
        :param value:
        :param defaults:
        :return:
        """
        match = ENV_VAR_TEMPLATE.match(value)
        if not match:
            return os.path.expandvars(value)

        match = match.group(1)
        env_var, default = match.split(":", 1) if ":" in match else (match, None)
        value = os.getenv(env_var)
        if value:
            logger.debug("Read %s from environment: %s", env_var, value)
        elif default:
            logger.debug("%s is empty, setting to default: %s", env_var, default)
        return value or default


def get_skill_config_file(config: Union[Path, Text] = None) -> Text:
    """
    Check if skill config file exists

    :param config:
    :return:
    """
    config_file = (
        config if config is not None else os.getenv("CONFIG_FILE", SKILL_CONFIG_FILE)
    )

    try:
        with open(config_file):
            logger.info("Using config: %s", config_file)

    except FileNotFoundError as ex:
        if config:
            raise RuntimeError from ex
        logger.error("File not found: %s", repr(config_file))

    return str(config_file)


def load_additional() -> List[Text]:
    """
    Load additional configuration files

    :return:
    """
    config: List[Text] = []
    additional_locations = os.getenv("CONFIG_ADDITIONAL_LOCATION")

    if not additional_locations:
        logger.debug("CONFIG_ADDITIONAL_LOCATION is not set.")
        return config

    paths = [Path(location).absolute() for location in additional_locations.split(",")]
    logger.debug("Will search configuration in %s", repr(paths))

    for path in paths:
        if path.exists():
            logger.debug("Loading additional configuration files from %s", repr(path))
            for _ in path.iterdir():
                if _.is_file() and _.suffix in (".conf", ".cnf"):
                    config += [str(_)]

    return config


def read_config(path: List[Text]) -> ConfigParser:
    """
    Read configuration from files

    :param path:    path to the configuration file
    :return:        configuration dictionary
    """

    logger.debug("Loading configuration from %s", repr(path))

    config = ConfigParser(interpolation=EnvVarInterpolation())
    paths = config.read(path)

    logger.debug("Loaded from %s", repr(paths))

    return config


def init_config(config: Union[Dict, Path, Text, None]) -> ConfigParser:
    """
    Initialize skill configuration:

        1. Defaults from SDK
        2. Additional locations
        3. "skill.conf"

    :param config:
    :return:
    """

    # Merge additional configs
    config_paths = load_additional()

    if not isinstance(config, dict):
        config_paths += [get_skill_config_file(config)]

    parser = read_config(config_paths)

    if isinstance(config, dict):
        logger.debug("Creating app from dictionary: %s", repr(config))
        parser.read_dict(config)

    return parser


def clean_section(d: SectionProxy, **kwargs) -> Dict[Text, Any]:
    """
    Helper to clean a ConfigParser's section and return as dictionary
        convert boolean values to bools, integer values to ints, float values to floats

    :param d:
    :param kwargs:
    :return:
    """

    def get(option, chain: Iterator):
        """
        Consequentially apply operations from the chain on the value provided by `option` parameter,
        if operation raises an exception, try the next one

        :param option:
        :param chain:
        :return:
        """
        try:
            return next(chain)(option)
        except (AttributeError, TypeError, ValueError):
            return get(option, chain)

    return {
        o: kwargs[o]
        if o in kwargs
        else get(o, iter((d.getint, d.getfloat, d.getboolean, d.get)))
        for o, v in {**dict(d.items()), **kwargs}.items()
    }


#
# Skill configuration settings
#


class FormatType(str, Enum):
    """Types of log format: human-readable or machine-readable"""

    GELF = "gelf"
    HUMAN = "human"


class Settings(BaseSettings):
    """Skill settings"""

    # Default values for skill name/title/description and version
    SKILL_NAME: Text = "skill-noname"
    SKILL_TITLE: Text = "Magenta Skill SDK Python"
    SKILL_DESCRIPTION: Text = "Magenta Voice Skill SDK for Python"
    SKILL_VERSION: Text = "1"

    # API base, if None, will default to "/v{settings.SKILL_VERSION}/{settings.SKILL_NAME}"
    API_BASE: Optional[Text] = None

    SKILL_DEBUG: bool = False

    # Basic auth: cvi/API key
    SKILL_API_USER: Text = "cvi"
    SKILL_API_KEY: Text = uuid.uuid1().__str__()

    @validator("SKILL_API_KEY", pre=True, always=True)
    def generate(cls, v):  # pylint: disable=E0213
        return v or uuid.uuid1().__str__()

    # Default HTTP port
    HTTP_PORT: int = 4242

    # Health endpoints for k8s
    K8S_READINESS: Text = "/k8s/readiness"
    K8S_LIVENESS: Text = "/k8s/liveness"

    # Prometheus metrics scraper endpoint
    PROMETHEUS_ENDPOINT: Text = "/prometheus"

    # Skill assessment endpoint
    SKILL_FIT_ASSESSMENT_ENDPOINT: Text = "/skill-fit-assessment"

    # Default request time-out value in seconds:
    # used from built-in httpx client
    REQUESTS_TIMEOUT: float = 5

    #
    # Logging
    #

    # Default log level: WARNING
    LOG_LEVEL: int = logging.WARNING

    # Default log format: GELF
    LOG_FORMAT: FormatType = FormatType.GELF

    @validator("LOG_LEVEL", pre=True, allow_reuse=True)
    def to_int(cls, v):  # pylint: disable=E0213
        return v if isinstance(v, int) else logging.getLevelName(v)

    # Maximal length of a string in the log
    LOG_ENTRY_MAX_STRING: int = 150

    # JSON-formatted list of CORS origins: requests from dev and prod UI
    BACKEND_CORS_ORIGINS: List[Text] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:4242",
        "http://127.0.0.1:4242",
    ]

    # The JWT secret that is used to verify the cvi service-token
    CVI_SERVICE_TOKEN_SECRET: str = "${CVI_SERVICE_TOKEN_SECRET:False}"

    def debug(self) -> bool:
        """
        Tell if skill is in "debug" mode

        :return:
        """
        return self.SKILL_DEBUG

    def app_config(self) -> Dict[Text, Any]:
        """
        This section values will be used to initialize FastAPI object

        :return:
        """
        return dict(
            title=self.SKILL_NAME,
            version=self.SKILL_VERSION,
            description=self.SKILL_DESCRIPTION,
            debug=self.SKILL_DEBUG,
        )

    def http_config(self) -> Dict[Text, Any]:
        """
        These values will be forwarded as keyword arguments to HTTP server

        :return:
        """
        return dict(port=self.HTTP_PORT)

    @classmethod
    def add_fields(cls, **field_definitions: Any):
        """
        Add new fields to the model

        :param field_definitions:
        :return:
        """
        new_fields: Dict[str, fields.ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}

        for f_name, f_def in field_definitions.items():
            f_annotation, f_value = type(f_def), f_def

            # if field is not defined, add new field with annotation to the model
            if f_name not in cls.__fields__:
                if f_annotation:
                    new_annotations[f_name] = f_annotation

                new_fields[f_name] = fields.ModelField.infer(
                    name=f_name,
                    value=f_value,
                    annotation=f_annotation,
                    class_validators=None,
                    config=cls.__config__,  # type: ignore
                )

        cls.__fields__.update(new_fields)
        cls.__annotations__.update(new_annotations)

    def reload(
        self, conf_file: Union[Dict, Path, Text, None] = None, **values
    ) -> "Settings":
        """
        Reload values from new config file:

            creates a new Settings instance,
            and performs in-place update of this singleton

        :param conf_file:
        :param values:
        :return:
        """
        Settings.Config.conf_file = conf_file
        for key, value in Settings(**values):
            setattr(self, key, value)

        return self

    class Config:
        """
        Config values priority:

            1. Arguments passed to the Settings class constructor.
            2. Environment variables.
            3. Variables loaded from a dotenv (.env) file.
            4. Variable values from skill.conf file.
            5. Variables loaded from the secrets directory.

        """

        extra = Extra.allow
        env_file = DOTENV_FILE
        conf_file: Union[Dict, Path, Text, None] = SKILL_CONFIG_FILE

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """
            Override the parent to insert "skill_conf_settings" values

            :param init_settings:
            :param env_settings:
            :param file_secret_settings:
            :return:
            """
            return (
                init_settings,
                env_settings,
                skill_conf_settings,
                file_secret_settings,
            )


def skill_conf_settings(_settings: BaseSettings) -> Dict[str, Any]:
    """
    Read configuration setting in ConfigParser format from "skill.conf":

        replace dashes with underscores in section names and configuration keys,
        join names and keys with underscore ("_") and convert to upper case

        So that a following config:

        ```ini
        [section]
        key = Value
        ```

        will be available as:

        >>> settings.SECTION_KEY
        >>> "Value"

    :param _settings:
    :return:
    """

    try:
        c: ConfigParser = init_config(Settings.Config.conf_file)

        d: Dict[Text, Any] = {
            "_".join((_make_key(section), _make_key(field))): value
            for section in c.sections()
            for field, value in clean_section(c[section]).items()
        }

        if isinstance(_settings, Settings):
            _settings.add_fields(**d)

        return d

    except RuntimeError:
        return {}


def _make_key(string: Text) -> Text:
    """
    Helper to convert section/value keys to env vars format:

        upper case and replace dashes with underscores

    :param string:
    :return:
    """
    return string.upper().replace("-", "_")


settings = Settings()
