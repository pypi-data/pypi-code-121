__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from subprocess import Popen, PIPE, STDOUT
import json
import yaml


def read_json(filename):
    with open(filename, "r") as fd:
        data = json.loads(fd.read())
    return data


def read_yaml(filepath):
    with open(filepath, "r") as fd:
        data = yaml.load(fd.read(), Loader=yaml.SafeLoader)
    return data


def row(cols):
    return "|" + "|".join(cols) + "|\n"


def run_command(cmd, sudo=False, stream=False):
    """run_command uses subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.

    """
    stdout = PIPE if not stream else None
    if sudo is True:
        cmd = ["sudo"] + cmd

    try:
        output = Popen(cmd, stderr=STDOUT, stdout=stdout)

    except FileNotFoundError:
        cmd.pop(0)
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    t = output.communicate()[0], output.returncode
    output = {"message": t[0], "return_code": t[1]}

    if isinstance(output["message"], bytes):
        output["message"] = output["message"].decode("utf-8")

    return output
