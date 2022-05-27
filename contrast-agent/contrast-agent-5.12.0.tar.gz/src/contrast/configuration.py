import re
from collections import namedtuple
import os

from contrast import AGENT_CURR_WORKING_DIR
import contrast.utils.configuration_utils as utils

from contrast.utils.decorators import cached_property
from contrast.utils.loggers import DEFAULT_PROGNAME
from contrast.extern import structlog as logging
from contrast.utils.singleton import Singleton

logger = logging.getLogger("contrast")

SPLIT_CWD = AGENT_CURR_WORKING_DIR.split(os.sep)
APP_NAME = SPLIT_CWD[len(SPLIT_CWD) - 1]
ENV_PREFIX = "CONTRAST"

ConfigOption = namedtuple("ConfigOption", ["name", "default_value", "type_cast"])

DEFAULT_SERVICE_HOST = "127.0.0.1"
DEFAULT_SERVICE_PORT = 30555

DEFAULT_TEAMSERVER_TYPE = "EOP"
PUBLIC_SASS_TEAMSERVER_TYPES = {
    "app.contrastsecurity.com": "SAAS_DEFAULT",
    "eval.contrastsecurity.com": "SAAS_POV",
    "ce.contrastsecurity.com": "SAAS_CE",
    "app.contrastsecurity.jp": "SAAS_TOKYO",
    "cs": "SAAS_",
}

PRIVATE_SASS_TEAMSERVER_TYPE = "SAAS_CUSTOM"
PRIVATE_SASS_DOMAIN = ["contrastsecurity.com", "contrastsecurity.jp"]

TESTING_TEAMSERVER_TYPE = "TESTING"
TESTING_TEAMSERVER_NAMES = [
    "darpa",
    "alpha.contrastsecurity.com",
    "apptwo.contrastsecurity.com",
    "teamserver-staging.contsec.jp",
    "teamserver-staging.contsec.com",
    "security-research.contrastsecurity.com",
    "teamserver-ops.contsec.com",
]


class AgentConfig(object):
    def __init__(self):
        self._config = utils.load_yaml_config()

        if not self._config:
            logger.info("No YAML config found; using default settings")
            self._config = {}

        self._config = utils.flatten_config(self._config)

        self.override_configs()

        # fallback for no host or no port specified
        # socket will still take precedence if it exists
        self.check_for_service_config()

        self.check_for_api_config()

        # This stores the session ID sent from TS. We have to separate this value from the value set in the yaml config
        # because the value sent from TS always takes precedence. This value is only sent from TS
        # in response to ApplicationStartup
        self._ts_session_id = None

    def get(self, key, default_value=None):
        return self._config.get(key, default_value)

    def put(self, key, value):
        if not key or key not in self._config:
            logger.error("Invalid contrast config option: %s", key)
            return

        self._config[key] = value

    def log_config(self):
        """
        Log configuration values.

        Config values deemed sensitive are logged as **REDACTED** unless unassigned.
        """
        sensitive_keys = ["api.service_key", "api.api_key", "api.proxy.url"]

        redacted_config = self._config.copy()
        for key in sensitive_keys:
            if redacted_config[key]:
                redacted_config[key] = "**REDACTED**"

        logger.info("Current Configuration", **redacted_config)

    def override_configs(self):
        """
        For each class representing different parts of the config (Agent, etc),
        take the current config and apply any overriding logic such as overriding with
        environment keys/values.

        At this time the order of precedence is:
            os.env > Config yaml

        Meaning that a config value defined in os.environ must be used instead of
        the same config defined in contrast_security.yaml

        Note that CLI args (sys.argv) are not supported. This may change if the
        agent becomes a runner.
        """
        builders = [Api, Agent, Application, Assess, Inventory, Protect, Root, Server]

        for builder in builders:
            builder().build(self._config)

    def check_for_api_config(self):
        """
        Validate api configurations were set if agent communicates directly with
        Contrast UI, without Contrast Service.

        If any api configs are missing, log at ERROR and disable the agent.

        Returns the missing values or an empty list if none were missing.
        """
        if not self.is_service_bypassed:
            return []

        api_keys = [
            "api.url",
            "api.service_key",
            "api.api_key",
            "api.user_name",
        ]

        missing_values = []
        for key in api_keys:
            val = self.get(key)
            if not val:
                missing_values.append(key)

        if missing_values:
            msg = (
                f"Missing a required connection value for: {', '.join(missing_values)}"
            )
            logger.error(msg)
            self.put("enable", False)

        return missing_values

    def check_for_service_config(self):
        """
        Check for and log user-provided config values for connecting to SR.
        Socket config takes precedence if it is user-provided. Otherwise assign
        host/port values if either is not provided.
        """
        socket_key = "agent.service.socket"
        host_key = "agent.service.host"
        port_key = "agent.service.port"

        # Socket is set
        if self.get(socket_key):
            logger.info(
                "Connecting to the Contrast Service using a UnixSocket socket: %s",
                self.get(socket_key),
            )
            return

        # Host and Port are set
        if self.get(host_key) and self.get(port_key):
            logger.info(
                "Connecting to the Contrast Service using a TCP socket: host: %s, port: %s",
                self.get(host_key),
                self.get(port_key),
            )
            return

        # Something is not set

        if self.get(host_key):
            self.put(port_key, DEFAULT_SERVICE_PORT)
            msg = f"{port_key} is not set. Falling back to default TCP socket host: {self.get(host_key)}, port: {self.get(port_key)}"
        elif self.get(port_key):
            self.put(host_key, DEFAULT_SERVICE_HOST)
            msg = f"{host_key} is not set. Falling back to default TCP socket host: {self.get(host_key)}, port: {self.get(port_key)}"
        else:
            self.put(host_key, DEFAULT_SERVICE_HOST)
            self.put(port_key, DEFAULT_SERVICE_PORT)
            msg = f"Neither {socket_key} nor the pair of {host_key} and {port_key} are set. Falling back to default TCP socket host: {self.get(host_key)}, port: {self.get(port_key)}."

        msg_prefix = "Missing a required connection value to the Contrast Service."
        warn_msg = f"{msg_prefix} {msg}"

        logger.warning(warn_msg)

    @property
    def session_id(self):
        return (
            self._ts_session_id
            if self._ts_session_id is not None
            else self.get("application.session_id", "")
        )

    @session_id.setter
    def session_id(self, session_id):
        self._ts_session_id = session_id
        logger.debug("Set session_id to %s", session_id, direct_to_teamserver=1)

    def get_session_metadata(self):
        return self.get("application.session_metadata", "")

    @property
    def app_code(self):
        return self.get("application.code", "")

    @property
    def app_metadata(self):
        return self.get("application.metadata", "")

    @property
    def app_group(self):
        return self.get("application.group", "")

    @property
    def app_tags(self):
        return self.get("application.tags", "")

    @cached_property
    def is_service_bypassed(self):
        bypass = self.get("agent.service.bypass", None)
        is_bypassed = bool(bypass and str(bypass).lower() in ("1", "true"))

        logger.debug("Service bypass is %s", "enabled" if is_bypassed else "disabled")

        return is_bypassed

    @cached_property
    def is_request_audit_enabled(self):
        return self.is_service_bypassed and self.get("api.request_audit.enable")

    @cached_property
    def teamserver_type(self):
        url = self.get("api.url")

        if url is None:
            return ""

        for name, ts_type in PUBLIC_SASS_TEAMSERVER_TYPES.items():
            if name in url:

                # This regex matches https://cs001.contrastsecurity.com
                r_url = re.match(r".*(cs\d{3})\..*", url)
                if r_url:
                    # and gets the second group which is the matched in brackets cs001
                    # adds it to the SAAS_ type and becomes SAAS_CS001
                    numbers = r_url.group(1).upper()

                    return ts_type + numbers

                return ts_type

        for name in TESTING_TEAMSERVER_NAMES:
            if name in url:
                return TESTING_TEAMSERVER_TYPE

        for name in PRIVATE_SASS_DOMAIN:
            if name in url:
                return PRIVATE_SASS_TEAMSERVER_TYPE

        return DEFAULT_TEAMSERVER_TYPE


class ConfigBuilder(object):
    TOP_LEVEL = ""

    def __init__(self):
        self.default_options = []

    def build(self, config):
        """
        Given a dict config, iterate over the default_options and check if
        the corresponding config key/value should be either :
        1. replaced by an existing env var
        2. keep existing config key/val but type-cast the value
        3. add a new key/default_value to the config

        :param config: dict config
        :return: None, config dict is updated pass by reference
        """

        if isinstance(self, Assess):
            sampling_lock_config = SamplingLockConfig()

        for option_name, default_val, type_cast in self.default_options:

            dot_alt = self._dot_alternative(option_name)
            underscore_alt = self._underscore_alternative(option_name)

            env_override = utils.get_env_key(underscore_alt)
            if env_override:
                # replace the config value with the os.env value and apply type-cast
                env_override = type_cast(env_override)
                config[dot_alt] = env_override
                continue

            if "sampling" in option_name and config.get(dot_alt):
                sampling_lock_config.set_sampling_config(option_name.split(".")[-1])

            if dot_alt in config:
                # update the config value with a type-cast value
                val = config[dot_alt]
                val = type_cast(val)
                config[dot_alt] = val
                continue

            # add a new key/default_value to config
            config[dot_alt] = default_val

    def _underscore_alternative(self, key):
        return "__".join(
            [x for x in [ENV_PREFIX, self.TOP_LEVEL, key.replace(".", "__")] if x]
        ).upper()

    def _dot_alternative(self, key):
        return ".".join([self.TOP_LEVEL, key]) if self.TOP_LEVEL else key


class Agent(ConfigBuilder):
    TOP_LEVEL = "agent"

    def __init__(self):
        super().__init__()

        self.default_options = [
            # Some logger default values are handled by the logger
            ConfigOption(
                name="logger.level",
                default_value="",
                type_cast=str,
            ),
            ConfigOption(name="logger.path", default_value="", type_cast=str),
            ConfigOption(
                name="logger.progname",
                default_value=DEFAULT_PROGNAME,
                type_cast=str,
            ),
            ConfigOption(
                name="python.enable_drf_response_analysis",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="python.enable_rep",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="python.enable_profiler",
                default_value=False,
                type_cast=utils.str_to_bool,
            ),
            # TODO: PYT-837 remove this config once exclusions are implemented
            ConfigOption(
                name="python.url_exclusion_patterns",
                default_value=[],
                type_cast=utils.strs_to_regexes,
            ),
            ConfigOption(
                name="python.assess.use_pure_python_hooks",
                default_value=False,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="polling.app_activity_ms", default_value=30000, type_cast=int
            ),
            ConfigOption(
                name="polling.server_activity_ms", default_value=30000, type_cast=int
            ),
            ConfigOption(
                name="polling.accumulated_rules_ms", default_value=30000, type_cast=int
            ),
            ConfigOption(
                name="service.enable", default_value=True, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="service.host", default_value="", type_cast=str),
            ConfigOption(name="service.port", default_value="", type_cast=int),
            ConfigOption(name="service.socket", default_value="", type_cast=str),
        ]


class Api(ConfigBuilder):
    TOP_LEVEL = "api"

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(name="url", default_value="", type_cast=str),
            ConfigOption(name="service_key", default_value="", type_cast=str),
            ConfigOption(name="api_key", default_value="", type_cast=str),
            ConfigOption(name="user_name", default_value="", type_cast=str),
            ConfigOption(
                name="request_audit.enable", default_value=False, type_cast=bool
            ),
            ConfigOption(
                name="request_audit.path",
                default_value=AGENT_CURR_WORKING_DIR,
                type_cast=str,
            ),
            ConfigOption(
                name="request_audit.requests", default_value=False, type_cast=bool
            ),
            ConfigOption(
                name="request_audit.responses", default_value=False, type_cast=bool
            ),
            ConfigOption(
                name="certificate.enable", default_value=False, type_cast=bool
            ),
            ConfigOption(name="certificate.ca_file", default_value="", type_cast=str),
            ConfigOption(name="certificate.cert_file", default_value="", type_cast=str),
            ConfigOption(name="certificate.key_file", default_value="", type_cast=str),
            ConfigOption(name="proxy.enable", default_value=False, type_cast=bool),
            ConfigOption(name="proxy.url", default_value="", type_cast=str),
        ]


class Application(ConfigBuilder):
    TOP_LEVEL = "application"

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(name="code", default_value="", type_cast=str),
            ConfigOption(name="group", default_value="", type_cast=str),
            ConfigOption(name="metadata", default_value="", type_cast=str),
            ConfigOption(
                name="name",
                default_value=os.path.basename(AGENT_CURR_WORKING_DIR),
                type_cast=str,
            ),
            ConfigOption(name="path", default_value="", type_cast=str),
            ConfigOption(name="tags", default_value="", type_cast=str),
            ConfigOption(name="version", default_value="", type_cast=str),
            ConfigOption(name="session_id", default_value="", type_cast=str),
            ConfigOption(name="session_metadata", default_value="", type_cast=str),
        ]


class Assess(ConfigBuilder):
    TOP_LEVEL = "assess"

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(
                name="enable", default_value=None, type_cast=utils.str_to_bool
            ),
            ConfigOption(
                name="enable_scan_response",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="sampling.enable", default_value=False, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="sampling.baseline", default_value=5, type_cast=int),
            ConfigOption(
                name="sampling.request_frequency", default_value=10, type_cast=int
            ),
            ConfigOption(
                name="sampling.window_ms", default_value=180_000, type_cast=int
            ),
            ConfigOption(name="tags", default_value="", type_cast=str),
            ConfigOption(
                name="rules.disabled_rules",
                default_value=[],
                type_cast=utils.parse_disabled_rules,
            ),
            ConfigOption(
                name="stacktraces",
                default_value="ALL",
                type_cast=utils.parse_stacktraces_options,
            ),
            ConfigOption(
                name="max_context_source_events",
                default_value=100,
                type_cast=int,
            ),
            ConfigOption(
                name="max_propagation_events",
                default_value=250,
                type_cast=int,
            ),
            ConfigOption(
                name="time_limit_threshold",
                default_value=300000,  # 5 minutes in ms
                type_cast=int,
            ),
            ConfigOption(
                name="max_rule_reported",
                default_value=100,
                type_cast=int,
            ),
        ]


class Inventory(ConfigBuilder):
    TOP_LEVEL = "inventory"

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(
                name="analyze_libraries",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="enable", default_value=True, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="tags", default_value="", type_cast=str),
        ]


class Protect(ConfigBuilder):
    TOP_LEVEL = "protect"

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(
                name="enable", default_value=None, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="samples.probed", default_value=50, type_cast=int),
            ConfigOption(name="samples.blocked", default_value=25, type_cast=int),
            ConfigOption(name="samples.exploited", default_value=100, type_cast=int),
            ConfigOption(
                name="samples.blocked_at_perimeter", default_value=25, type_cast=int
            ),
            ConfigOption(
                name="rules.bot-blocker.enable",
                default_value=False,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.cmd-injection.detect_chained_commands",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.cmd-injection.detect_parameter_command_backdoors",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.cmd-injection.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.disabled_rules",
                default_value=[],
                type_cast=utils.parse_disabled_rules,
            ),
            ConfigOption(
                name="rules.method-tampering.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.nosql-injection.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.path-traversal.detect_common_file_exploits",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.path-traversal.detect_custom_code_accessing_system_files",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.path-traversal.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.reflected-xss.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_chained_queries",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_dangerous_functions",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_suspicious_unions",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_tautologies",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.ssrf.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.unsafe-file-upload.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.xxe.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
        ]


class Server(ConfigBuilder):
    TOP_LEVEL = "server"

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(
                name="name", default_value=utils.get_hostname(), type_cast=str
            ),
            ConfigOption(name="path", default_value="/", type_cast=str),
            ConfigOption(name="type", default_value="", type_cast=str),
            ConfigOption(name="version", default_value="", type_cast=str),
            ConfigOption(name="environment", default_value="", type_cast=str),
            ConfigOption(name="tags", default_value="", type_cast=str),
        ]


class Root(ConfigBuilder):
    TOP_LEVEL = None

    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(name="enable", default_value=True, type_cast=utils.str_to_bool)
        ]


class SamplingLockConfig(Singleton):
    def init(self):
        self.lock_enable = False
        self.lock_baseline = False
        self.lock_frequency = False
        self.lock_window = False

    def set_sampling_config(self, value):
        if value == "enable":
            self.lock_enable = True
        if value == "baseline":
            self.lock_baseline = True
        if value == "request_frequency":
            self.lock_frequency = True
        if value == "window_ms":
            self.lock_window = True
