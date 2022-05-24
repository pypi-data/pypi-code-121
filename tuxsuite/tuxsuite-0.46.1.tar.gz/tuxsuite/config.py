# -*- coding: utf-8 -*-

import os
import tuxsuite.exceptions
from os.path import expanduser
import configparser
import logging
import re
import uuid
import yaml

from tuxsuite import requests
import tuxsuite.schema


def getenv(name, default=None):
    deprecated = os.getenv(f"TUXBUILD_{name}")
    if deprecated:
        logging.warning(
            f"TUXBUILD_{name} is deprecated, please use TUXSUITE_{name} instead"
        )
        return deprecated

    return os.getenv(f"TUXSUITE_{name}", default)


def get_config_file(name):
    config_path = f"~/.config/tuxsuite/{name}"
    deprecated_config_path = f"~/.config/tuxbuild/{name}"
    if os.path.exists(expanduser(deprecated_config_path)):
        logging.warning(
            f"{deprecated_config_path} is deprecated; please rename it to {config_path}."
        )
        return deprecated_config_path
    return config_path


def get_defaults_ini(path):
    return os.path.abspath(os.path.join(expanduser(path), "..", "defaults.ini"))


class Config:
    def __init__(self, config_path=None):
        """
        Retrieve tuxsuite authentication token and API url

        TuxSuite requires an API token. Optionally, a API url endpoint may
        be specified. The API url defaults to https://api.tuxbuild.com/v1.

        The token and url may be specified in environment variables, or in
        a tuxsuite config file. If using the config file, the environment
        variable TUXSUITE_ENV may be used to specify which tuxsuite config
        to use.

        Environment variables:
            TUXSUITE_TOKEN
            TUXSUITE_URL (optional)

        Config file:
            Must be located at ~/.config/tuxsuite/config.ini.
            This location can be overriden by setting the TUXSUITE_CONFIG
            environment variable.
            A minimum config file looks like:

                [default]
                token=vXXXXXXXYYYYYYYYYZZZZZZZZZZZZZZZZZZZg

            Multiple environments may be specified. The environment named
            in TUXSUITE_ENV will be chosen. If TUXSUITE_ENV is not set,
            'default' will be used.

            Fields:
                token
                group (optional)
                project (optional)
                api_url (optional)
                tuxapi_url (optional)
                tuxauth_url (optional)
        """

        # defaults
        self.auth_token = None
        self.group = None
        self.project = None
        self.kbapi_url = "https://api.tuxbuild.com/v1"
        self.tuxapi_url = "https://tuxapi.tuxsuite.com"
        self.tuxauth_url = "https://auth.tuxsuite.com"

        # tuxsuite environment
        self.tuxsuite_env = getenv("ENV", "default")

        # Select the config file
        config_path = getenv("CONFIG", config_path)
        if config_path is None:
            config_path = get_config_file("config.ini")
        config_path_exists = os.path.exists(expanduser(config_path))

        # Load configuration from file
        if config_path_exists:
            config = self._get_config_from_file(config_path, self.tuxsuite_env)
            self.auth_token = config.get("token")
            self.group = config.get("group")
            self.project = config.get("project")
            self.kbapi_url = config.get("api_url", self.kbapi_url).rstrip("/")
            self.tuxapi_url = config.get("tuxapi_url", self.tuxapi_url).rstrip("/")
            self.tuxauth_url = config.get("tuxauth_url", self.tuxauth_url).rstrip("/")

        # override with configuration from env variables
        self.auth_token = getenv("TOKEN", self.auth_token)
        self.group = getenv("GROUP", self.group)
        self.project = getenv("PROJECT", self.project)
        self.kbapi_url = getenv("URL", self.kbapi_url).rstrip("/")

        # token and kbapi should be specified
        if not self.auth_token:
            raise tuxsuite.exceptions.TokenNotFound(
                "Token not found in TUXSUITE_TOKEN nor at [{}] in {}".format(
                    self.tuxsuite_env, config_path
                )
            )
        if not self.kbapi_url:
            raise tuxsuite.exceptions.URLNotFound(
                "TUXSUITE_URL not set in env, or api_url not specified at [{}] in {}.".format(
                    self.tuxsuite_env, config_path
                )
            )

        # group and project should be defined
        if self.group is None or self.project is None:
            (self.group, self.project) = self._get_defaults(
                config_path,
                config_path_exists,
                self.tuxsuite_env,
                self.group,
                self.project,
            )

    def _get_config_from_file(self, config_path, env):
        path = expanduser(config_path)
        defaults = get_defaults_ini(config_path)

        try:
            with open(path, "r"):
                # ensure file exists and is readable
                pass
        except Exception as e:
            raise tuxsuite.exceptions.CantGetConfiguration(str(e))

        # Load the defaults config (if it exists) and path
        try:
            config = configparser.ConfigParser()
            config.read([defaults, path])
        except configparser.Error as exc:
            raise tuxsuite.exceptions.InvalidConfiguration(
                "Error, invalid config file '{}': {}".format(path, str(exc))
            )
        if not config.has_section(env):
            raise tuxsuite.exceptions.InvalidConfiguration(
                "Error, missing section [{}] from config file '{}'".format(env, path)
            )
        return config[env]

    def _get_defaults(self, config_path, config_path_exists, env, group, project):
        defaults = get_defaults_ini(config_path)

        # Add default group and project from tuxauth
        ret = requests.get(
            f"{self.tuxauth_url}/v1/tokens/{uuid.uuid3(uuid.NAMESPACE_DNS, self.auth_token)}"
        )
        try:
            if ret.status_code != 200:
                raise Exception(
                    f"Unable to authenticate to {self.tuxauth_url}: {ret.status_code}"
                )
            user = ret.json()["UserDetails"]
        except Exception as e:
            raise tuxsuite.exceptions.CantGetConfiguration(
                f"Unable to get default group and project: {e}"
            )

        if config_path_exists:
            default_config = configparser.ConfigParser()
            default_config.read(defaults)
            if not default_config.has_section(env):
                default_config.add_section(env)

        if group is None:
            group = user["Groups"][0]
            if config_path_exists:
                default_config.set(env, "group", group)
        if project is None:
            project = user["Name"]
            if config_path_exists:
                default_config.set(env, "project", project)

        if config_path_exists:
            with open(defaults, "w") as f_out:
                default_config.write(f_out)

        return (group, project)

    def get_auth_token(self):
        return self.auth_token

    def get_kbapi_url(self):
        return self.kbapi_url

    def get_tuxsuite_env(self):
        return self.tuxsuite_env


InvalidConfiguration = tuxsuite.exceptions.InvalidConfiguration


class BuildSetConfig:
    def __init__(self, set_name, filename=None):
        self.name = set_name
        self.description = set_name
        self.set_name = set_name
        if filename:
            self.filename = filename
        else:
            self.filename = os.path.expanduser(get_config_file("builds.yaml"))
        self.plan = []
        self.__load_config__()

    def __load_config__(self):
        filename = self.filename
        set_name = self.set_name
        try:
            if re.match(r"^https?://", str(filename)):
                contents = self.__fetch_remote_config__(filename)
            else:
                contents = open(filename).read()
            config = yaml.safe_load(contents)
        except (FileNotFoundError, yaml.loader.ParserError) as e:
            raise InvalidConfiguration(str(e))
        if not config:
            raise InvalidConfiguration(
                f"Build set configuration in {filename} is empty"
            )
        if "sets" not in config:
            raise InvalidConfiguration('Missing "sets" key')

        for set_config in config["sets"]:
            if set_config["name"] == set_name:
                self.name = set_config["name"]
                self.description = set_config["name"]

                if "builds" in set_config:
                    builds = []
                    builds = set_config["builds"]
                    if builds:
                        for build in builds:
                            self.plan.append({"build": build, "tests": []})

                    if not self.plan:
                        raise InvalidConfiguration(
                            f'Build list is empty for set "{set_name}"'
                        )
                    return
                else:
                    raise InvalidConfiguration(
                        f'No "builds" field defined for set "{set_name}"'
                    )
        raise InvalidConfiguration(f'No build set named "{set_name}" in {filename}')

    def __fetch_remote_config__(self, url):
        result = requests.get(url)
        if result.status_code != 200:
            raise InvalidConfiguration(
                f"Unable to retrieve {url}: {result.status_code} {result.reason}"
            )
        return result.text


class PlanConfig:
    def __init__(self, name, description, filename, job_name=None):
        self.name = name
        self.description = description
        self.filename = filename
        self.job_name = job_name
        self.plan = []
        self.schema_warning = ""
        self.plan_type = None
        self.__load_config__()

    def __load_config__(self):
        try:
            if re.match(r"^https?://", str(self.filename)):
                contents = self.__fetch_remote_config__(self.filename)
            else:
                contents = open(self.filename).read()
            config = yaml.safe_load(contents)
        except (FileNotFoundError, yaml.loader.ParserError) as e:
            raise InvalidConfiguration(str(e))

        # calling Parent Plan Type class to get respective plan type obj ( kernel or bake plan)
        self.plan_type = tuxsuite.PlanType.load_plan(config)

        try:
            self.plan_type.check_schema(config)
        except Exception as exc:
            self.schema_warning = str(exc)

        if not isinstance(config, dict):
            raise InvalidConfiguration(
                f"Plan configuration in {self.filename} is invalid"
            )

        if config.get("version") != 1:
            raise InvalidConfiguration(f"Invalid plan {self.filename}: invalid version")

        if not self.name:
            self.name = config["name"]
        if not self.description:
            self.description = config["description"]

        self.plan_type.apply(self)

    def __fetch_remote_config__(self, url):
        result = requests.get(url)
        if result.status_code != 200:
            raise InvalidConfiguration(
                f"Unable to retrieve {url}: {result.status_code} {result.reason}"
            )
        return result.text
