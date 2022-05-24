import os, json, inspect, copy, sys, socket, re, platform, getpass
import numpy as np
from typing import List, Dict

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ...config.main_configuration import CONFIGURATION

from ._utils import *

from ..main._base import AlphaClass
from ..main._exception import EXCEPTIONS
from ..logger import AlphaLogger

from ...libs import converter_lib, sql_lib, io_lib

_CONFIGURATIONS = {}


class AlphaConfig(AlphaClass):
    __reserved = ["user", "configuration", "project", "ip", "platform"]

    def __init__(
        self,
        name: str = "config",
        filepath: str = None,
        root: str = None,
        filename: str = None,
        log: AlphaLogger = None,
        configuration: str = None,
        data: dict = None,
        origin=None,
        core=None,
        core_configuration=None,
        reserved: List[str] = [],
        required: List[str] = [],
        user: str = None,
        default: str = None
    ):
        if hasattr(self, "tmp"):
            return
        
        if default is not None and os.path.isfile(default):
            default_config = AlphaConfig(
                f"default_{name}",
                filepath=default,
            )
            data = data if data is not None else {}
            merge_configuration(
                data, source_configuration=default_config.data, replace=False
            )

        self.reserved = list(set(reserved).union(set(self.__reserved)))
        self.required = required

        name, filepath, root, filename = ensure_filepath(name, filepath, root, filename)

        self.name = name
        self.user = user
        self.filepath = filepath
        self.root = root
        self.filename = filename
        self.configuration: str = configuration
        self.origin = origin
        self.sub_configurations = {}
        self.core = core

        global _CONFIGURATIONS
        _CONFIGURATIONS[filepath] = self

        super().__init__(log=log)

        self.tmp = {}

        self.data_tmp = {}
        self.data_origin = data if data is not None else {}
        self.data = data if data is not None else {}

        self.valid = True
        self.loaded = False

        self.infos = []
        self.warnings = []

        self.api = None
        self.cnx_str = None

        self.log = log

        self.core_configuration = core_configuration

        if data is None:
            self.__load_raw()

        if data is None and configuration is not None:
            self.set_configuration(configuration)
        else:
            self.__load()

    def __load_raw(self):
        if not self.loaded:
            with open(self.filepath, encoding="utf-8") as json_data_file:
                try:
                    self.data_origin = json.load(json_data_file)
                except Exception as ex:
                    print(f"Configuration file {self.filepath} is invalid: {ex}")
                    exit()
                self.loaded = True

    def set_configuration(self, configuration, force=False):
        if CONFIGURATIONS.is_configured(self) and not force:
            return

        if configuration is None and self.configuration is None:
            self.error(
                f"Configuration need to be explicitely specified in configuration call or config file for {self.filepath} file"
            )
            return
        elif configuration is None and self.configuration is not None:
            configuration = self.configuration

        self.__clean()

        self.configuration = configuration

        self.__load()

    def __clean(self):
        # remove tmp from data_origin
        if len(self.tmp) != 0:
            self.data_origin = {
                x: y for x, y in self.data_origin.items() if x not in self.tmp
            }

    def __load(self):
        self.__check_reserved()

        self.__set_tmps()
        self.__process_tmps()

        self._set_configuration()

        self.core_configuration = (
            self.get("core_configuration", root=False)
            if self.core_configuration is None
            else self.core_configuration
        )

        # check if loaded
        if not CONFIGURATIONS.load_configuration(self) or not self.core_configuration:
            if self.core_configuration:
                self.info(f"Reload configuration: {self.filepath}")
            self.__init_data()
            self.__configure_sub_configurations()
            CONFIGURATIONS.save_configuration(self)
        else:
            self.__configure_sub_configurations()

        if self.core_configuration:
            self.__check_required()
            self.__configure()

    """def set_data(self,value,paths=[]):
        ensure_path(self.data_origin,paths,value=value)"""

    def _set_configuration(self):
        if "configurations" in self.data_origin:
            configurations = {
                x.lower(): y for x, y in self.data_origin["configurations"].items()
            }

            default_configuration = None
            if "default_configuration" in self.data_origin:
                default_configuration = self.data_origin["default_configuration"]

            tmp_configuration = None
            for key, config in self.data_tmp.items():
                if "configuration" in config:
                    tmp_configuration = config["configuration"]
                    self.info(
                        f"Detected configuration <{tmp_configuration}> in {key} section"
                    )

            self.configuration = (
                self.configuration
                if self.configuration
                else (tmp_configuration if tmp_configuration else default_configuration)
            )

            tmp_config = {}
            configuration_names = [
                x.lower() for x in self.data_origin["configurations"].keys()
            ]
            # configuration_names.sort(key=len)

            index = 0
            for configuration_name in configuration_names:
                matchs = re.findall(configuration_name, self.configuration.lower())
                if len(matchs) == 0:
                    continue
                try:
                    merge_configuration(
                        tmp_config, configurations[configuration_name], replace=True
                    )
                    self.info(
                        f"{'Using base' if index == 0 else 'Merging'} configuration {configuration_name}"
                    )
                    index += 1
                except ValueError as ex:
                    raise ex
                    # self.error(ex)
            self.data_tmp["configurations"] = tmp_config

        self.__add_tmp("configuration", self.configuration)

    def __init_data(self):
        config = copy.deepcopy(self.data_origin)
        for key, values in self.data_tmp.items():
            merge_configuration(config, values, replace=True)
            del config[key]

        self.data = self._replace_parameters(config)

    def __configure(self):
        # Paths
        if self.is_path("paths"):
            for path in self.get("paths"):
                sys.path.append(path)

        if self.is_path("envs"):
            for env, value in self.get("envs").items():
                os.environ[env] = value

        if self.core_configuration:
            sequence = ", ".join(
                [
                    f"{tmp}=<{tmp_value}>{'*' if tmp + 's' in self.data_tmp else ''}"
                    for tmp, tmp_value in self.tmp.items()
                ]
            )
            self.info(
                f"Configuration {self.filepath.split(os.sep)[-1]} initiated for: {sequence}"
            )

        # SET ENVIRONMENT VARIABLES
        if self.core is not None:
            set_environment_variables(self.get("environment"))

            exceptions = self.get("exceptions")
            if exceptions is not None:
                for exception_group in exceptions:
                    for (
                        exception_name,
                        exception_configuration,
                    ) in exception_group.items():
                        if not exception_name in EXCEPTIONS:
                            EXCEPTIONS[exception_name] = exception_configuration
                        else:
                            self.error(f"Duplicate exception name for {exception_name}")

    def __configure_sub_configurations(self):
        if not self.core_configuration:
            return

        config = self.data
        # get sub configurations
        self.sub_configurations = {}
        configs_values, paths = get_configs_from_config(config, path=None)

        for i, values in enumerate(configs_values):
            config_path = values[0]
            if not config_path in self.sub_configurations:
                name = config_path.split(os.sep)[-1]

                self.sub_configurations[config_path] = AlphaConfig(
                    name=name,
                    filepath=config_path,
                    log=self.log,
                    origin=self,
                    configuration=self.configuration,
                )

        # replace sub configurations
        set_configs_paths(config, paths, configs_values, self.sub_configurations)
        self.data = config

    def get_config(self, path=[], configuration=None):
        path = self._get_path(path)
        config_data = self.get(path)
        if config_data is None:
            return None

        # TODO: enhance
        config = AlphaConfig(
            name=".".join(path),  # self.name,
            root=self.root,
            log=self.log,
            configuration=self.configuration
            if configuration is None
            else configuration,
            data=config_data,
        )
        return config

    def _replace_parameters(self, config):
        """Replace parameters formatted has {{<parameter>}} by their values in
        a json dict.

        Arguments:
            config {dict} -- json dict to analyse and replace parameters formatted has {{<parameter>}}

        Returns:
            dict -- the input dict with parameters replace by their values
        """

        parameters_name, paths = get_parameters_from_config(config, path=None)
        """
            paths                                    parameters_name
            tests / save_directory                   save_root
            files / google-taxonomy / file_path      sources & file_name
            ips / 62.210.244.105 / web / root        root
            save_root                                root & project_name
            sqllite_path                             root
            web / api_root                           root
        """
        parameters = list(set([x for sublist in parameters_name for x in sublist]))

        parameters_value = {}
        for parameter in parameters:
            if parameter in self.tmp:
                parameters_value[parameter] = self.tmp[parameter]
                continue

            # ([3306, 3308], [['variables'], []])
            if "/" in parameter:
                parameter = parameter.split("/")
            values_paths = search_it(config, parameter)

            # take the first value if any
            if len(values_paths) != 0 and len(values_paths[0]) != 0:
                values, pths = values_paths

                index, path_len = 0, None

                lenghts = [len(x) for x in pths]
                indexs = np.where(lenghts == np.amin(lenghts))[0]

                if len(indexs) == 0:
                    value = self.get(parameter)
                elif len(indexs) == 1:
                    value = values[indexs[0]]
                else:
                    self.error(
                        "Too many possible value at the same level are specified for parameter <%s>"
                        % parameter
                    )
                    exit()

                if isinstance(parameter, list):
                    parameter = "/".join(parameter)
                parameters_value[parameter] = value
            else:
                if isinstance(parameter, list):
                    parameter = "/".join(parameter)
                value = self.get(parameter, force_exit=True)
                parameters_value[parameter] = value

        l = 0
        set_parameter_value(parameters_value, l)

        # Replace parameters values
        set_paths(config, paths, parameters_name, parameters_value)

        # check parameters
        parameters_name, paths = get_parameters_from_config(config, path=None)
        if len(parameters_name) != 0:
            parameters = list(set([x[0] for x in parameters_name if len(x) != 0]))
            for i in range(len(parameters)):
                self.error(
                    'Missing parameter "%s" in configuration %s'
                    % (parameters[i], self.filepath)
                )
            if len(parameters) != 0:
                exit()
        return config

    def _get_value_from_main_config(self, parameter, force_exit=False):
        value = None
        if self.origin is not None:
            value = self.origin.get(parameter)
            if value is not None:
                return value

        if self.name != "config":
            if self.origin is not None:
                value = self.origin.get(parameter)
                if value is not None:
                    return value

        if force_exit:
            self.error(
                "No value is specified for <%s> in %s" % (parameter, self.filepath)
            )
            exit()
        return value

    def get(
        self,
        path=[],
        root: bool = True,
        default=None,
        force_exit: bool = False,
        configuration: str = None,
        type_=None,
        required: bool = False,
    ):
        value = self._get_parameter_path(path)
        if value is None and root:
            value = self._get_value_from_main_config(path, force_exit=force_exit)
        if type_ is not None:
            try:
                value = type_(value)
            except Exception as ex:
                self.error(
                    "Cannot convert parameter <%s> to type <%s> for value <%s>"
                    % (path, type_, value),
                    ex=ex,
                )
        if value is None:
            value = default
        if value is None and required:
            self.error(
                f'Missing "{"/".join(path)}" entry in configuration file {self.filepath}'
            )
            exit()
        return value

    """def _get_parameter_path(self,parameters,data=None,level=1):
        parameters = self._get_path(parameters)
        if parameters == '':
            return self.data

        if data is None:
            data = self.data

        not_init = parameters[0] not in self.data_origin and parameters[0] not in self.tmp

        if parameters[0] not in data and not_init:
            return None

        if len(parameters) == 1:
            if parameters[0] in self.tmp:
                return self.tmp[parameters[0]]
            if parameters[0] in data:
                return data[parameters[0]]
            if parameters[0] in self.data_origin:
                return self.data_origin[parameters[0]]

        return self._get_parameter_path(parameters[1:],data[parameters[0]],level = level + 1)"""

    def _get_parameter_path(
        self, parameters, data=None, data_origin=None, tmp=None, level=1
    ):
        parameters = self._get_path(parameters)
        if parameters == "":
            return self.data

        data = self.data if data is None else data
        data_origin = self.data_origin if data_origin is None else data_origin
        tmp = self.tmp if tmp is None else tmp

        is_in = any([parameters[0] in y for y in [data, data_origin, tmp]])
        if not is_in:
            return None

        if len(parameters) == 1:
            if parameters[0] in tmp:
                return tmp[parameters[0]]
            if parameters[0] in data:
                return data[parameters[0]]
            if parameters[0] in data_origin:
                return data_origin[parameters[0]]

        data = data[parameters[0]] if parameters[0] in data else []
        data_origin = data_origin[parameters[0]] if parameters[0] in data_origin else []
        tmp = tmp[parameters[0]] if parameters[0] in tmp else []

        return self._get_parameter_path(
            parameters[1:], data, data_origin, tmp, level=level + 1
        )

    def _get_path(self, parameters):
        if type(parameters) == str and "/" in parameters:
            parameters = parameters.split("/")
        if type(parameters) == str:
            parameters = [parameters]
        return parameters

    def is_parameter_path(self, parameters, data=None):
        if type(parameters) == str and "/" in parameters:
            parameters = parameters.split("/")
        if type(parameters) == str:
            parameters = [parameters]
        if data is None:
            data = self.data
        if len(parameters) == 0:
            return True
        if parameters[0] not in data:
            return False
        return self.is_parameter_path(parameters[1:], data[parameters[0]])

    def is_path(self, parameters, data=None):
        return self.is_parameter_path(parameters, data=data)

    def save(self):
        self.info(f"Save configuration file at {self.filepath}")

        self.__clean()

        with open(self.filepath, "w", encoding="utf-8") as json_data_file:
            json.dump(
                self.data_origin,
                json_data_file,
                sort_keys=True,
                indent=4,
                ensure_ascii=False,
            )

    def show(self):
        show(self.data)

    def __check_required(self):
        if "required" in self.data:
            self.required = list(set(self.data["required"]).union(set(self.required)))

        for path in self.required:
            if not self.is_path(path):
                self.error(f"Missing '{path}' key in config file {self.filepath}")
                self.valid = False
                exit()

    def __check_reserved(self):
        for reserved_name in self.reserved:
            if reserved_name in self.data_origin:
                self.error(
                    f"<{reserved_name}> entry in configuration {self.filepath} is reserved"
                )
                exit()

    def __add_tmp(self, name, value):
        if name in self.data_origin:
            self.error(f"<{name}> entry in configuration {self.filepath} is reserved")
            exit()

        self.tmp[name] = value
        # self.data_origin[name]  = value # TODO: check

    def get_tmp(self, name):
        if not name in self.tmp:
            return None
        return self.tmp[name]

    def __set_tmps(self):
        # tmps
        self.__add_tmp("project", os.getcwd())

        # USER
        # try:
        if self.user is None:
            try:
                self.user = getpass.getuser()
            except:
                for name in ("USERPROFILE", "HOMEPATH"):
                    user = os.environ.get(name).split(os.sep)[-1]
                    if user:
                        self.user = user
        self.__add_tmp("user", self.user)
        # except Exception as ex:
        #    self.critical(f"Could not detect the system user",out=True,ex=ex)

        current_ip = [
            l
            for l in (
                [
                    ip
                    for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                    if not ip.startswith("127.")
                ][:1],
                [
                    [
                        (s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                        for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
                    ][0][1]
                ],
            )
            if l
        ][0][0]
        self.__add_tmp("ip", current_ip)

        system_platform = platform.system().lower()
        self.__add_tmp("platform", system_platform)

        machine = platform.uname().node.lower()
        self.__add_tmp("machine", machine)

    def get_key(self, raw=False):
        return (
            self.filepath
            + ": "
            + " - ".join(
                "%s=%s" % (x, y)
                for x, y in self.tmp.items()
                if not raw or x != "configuration"
            )
        )

    def __process_tmps(self):
        to_process = ["user", "ip", "platform", "machine"]

        for name in to_process:
            if not name + "s" in self.data_origin:
                continue
            if type(self.data_origin[name + "s"]) != dict:
                self.error(
                    f"In configuration file entry <{name + 's'}> if not a dict type"
                )
                continue
            values = {
                x.lower(): y
                for x, y in self.data_origin[name + "s"].items()
                if self.get_tmp(name) is not None
                and (x.lower() == self.get_tmp(name).lower())
            }
            if len(values) != 0 and self.get_tmp(name) is not None:
                self.data_tmp[name + "s"] = values[self.get_tmp(name).lower()]


def load_raw_sub_configurations(data):
    sub_configurations = {}

    configs_values, paths = get_configs_from_config(data, path=None)
    for i, values in enumerate(configs_values):
        config_path = values[0]
        if not config_path in sub_configurations:
            name = config_path.split(os.sep)[-1]

            sub_configurations[config_path] = AlphaConfig(
                name=name, filepath=config_path
            )
    return sub_configurations


class AlphaConfigurations(object):
    _name = "tmp/configs"
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self._configurations: Dict[str, AlphaConfig] = {}
        if os.path.exists(self._name):
            loaded_configurations = io_lib.unarchive_object(self._name)
            if type(loaded_configurations) == dict:
                for key, values in loaded_configurations.items():
                    if self._is_valid_configuration(values):
                        self._configurations[key] = values

    def _is_valid_configuration(self, configuration):
        valid = False
        if type(configuration) == dict:
            valid = True
            for key, values in configuration.items():
                if type(values) != dict:
                    valid = False
        return valid

    def load_configuration(self, config: AlphaConfig) -> bool:
        path = config.get_key()

        if path in self._configurations:
            loaded_configuration = self._configurations[path]

            if (
                not "sub_configurations" in loaded_configuration
                or not "data_origin" in loaded_configuration
            ):
                return False

            if (
                loaded_configuration
                and loaded_configuration["data_origin"] == config.data_origin
            ):
                for key in loaded_configuration:
                    if hasattr(config, key):
                        setattr(config, key, loaded_configuration[key])

                # check sub configurations
                for path, sub_config in loaded_configuration[
                    "sub_configurations"
                ].items():
                    if os.path.getsize(path) != sub_config["size"]:
                        print("Need to reload %s" % path)
                        return False
                return True
        return False

    def save_configuration(self, config: AlphaConfig):
        key = config.get_key()
        dataset = {
            "data_origin": config.data_origin,
            "data_tmp": config.data_tmp,
            "data": config.data,
            "sub_configurations": {
                x.filepath: {
                    "data_origin": x.data_origin,
                    "data_tmp": x.data_tmp,
                    "data": x.data,
                    "size": os.path.getsize(x.filepath),
                }
                for x in config.sub_configurations.values()
            },
        }
        try:
            self._configurations[key] = dataset
        except:
            self._configurations: Dict[str, object] = {key: dataset}
        io_lib.archive_object(self._configurations, self._name)

    def is_configured(self, config) -> bool:
        path = config.get_key()
        return path in self._configurations


CONFIGURATIONS = AlphaConfigurations()
