import json
import subprocess
from typing import Any, AnyStr, List
from unittest import TestCase
import yaml
from click.testing import CliRunner
from dnastack import __main__ as dnastack_cli
import os


# ASSERTS
def assert_has_property(self: TestCase, obj: dict, attribute: str):
    self.assertTrue(
        attribute in obj,
        msg="obj lacking an attribute. obj: %s, intendedAttribute: %s"
        % (obj, attribute),
    )


# CONFIG
def clear_config():
    subprocess.call("rm ~/.dnastack/config.yaml && touch ~/.dnastack/config.yaml", shell=True)


def use_config_from_file(filename: str):
    try:
        with open("~/.dnastack/config.yaml", "w") as config_file:
            with open(filename, "r") as config_base:
                obj = json.loads(config_base.read())
                yaml.dump(obj, config_file)
    except Exception as e:
        raise Exception(f"Unable to use config from file {filename}: {e}")


def get_cli_config(
    runner: CliRunner, key: str, delimiter: str = ".", datatype: type = str
):
    result = runner.invoke(
        dnastack_cli.dnastack,
        ["config", "get", key, "--delimiter", delimiter],
    )

    if result.exit_code != 0:
        raise Exception(f"Could not get config for {key}. ({result.output})")
    return datatype(result.output.strip())


def set_cli_config(runner: CliRunner, key: str, val: Any, delimiter: str = "."):
    result = runner.invoke(
        dnastack_cli.dnastack, ["config", "set", key, val, "--delimiter", delimiter]
    )

    if result.exit_code != 0:
        raise Exception(f"Could not set config for {key}. ({result.output})")


def set_auth_params_for_service(runner: CliRunner, service: str, auth_params: dict):

    if service == "dataconnect":
        service = "data_connect"

    # you have to rename the keys for the cli
    auth_params = {
        f"{service}.auth.url": auth_params["url"],
        f"{service}.auth.client.redirect_url": auth_params["client"]["redirect_url"],
        f"{service}.auth.client.id": auth_params["client"]["id"],
        f"{service}.auth.client.secret": auth_params["client"]["secret"],
    }
    for key in auth_params.keys():
        set_cli_config(runner, key, auth_params[key])


# AUTH
def login_with_refresh_token_for_service(
    runner: CliRunner, service: str, refresh_token: str
):

    if service == "dataconnect":
        config_service = "data_connect"
    else:
        config_service = service

    set_cli_config(
        runner, f"{config_service}.auth.refresh_token", refresh_token, delimiter="|"
    )
    runner.invoke(dnastack_cli.dnastack, ["auth", "login", service])
