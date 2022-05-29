import os
import subprocess
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union


class _UnsupportedCommand(Exception):
    pass


@dataclass
class Output:
    """Used to return a task with system output"""

    stdout: str = ""
    stderr: str = ""
    status: int = 0


def _transform_cmd(cmd: Union[str, List[str]]) -> str:
    """
    Common function to handle command strings
    """
    runCmd = ""
    if type(cmd) == list:
        runCmd = " ".join(cmd)
    elif type(cmd) == str:
        runCmd = str(cmd)
    else:
        raise _UnsupportedCommand(f"Unsupported command type: {type(cmd)}")

    return runCmd


def _get_env(env: Dict[str, str]) -> Dict[str, str]:
    """
    Common function to get and set environment variables
    Merge passed in Dict with users envs
    """

    set_envs = {**env, **os.environ.copy()}
    return set_envs


def run(cmd: Union[str, List[str]], env: Optional[Dict[str, str]] = None) -> bool:
    """
    Runs a command, with optional environment variables passed

    This also attaches a copy of the users environment variables for every run
    This makes tasks work in a virtual env too, if the task calls
    a module only installed in one
    (e.g. python -m my_module_I_installed_in_this_venv)

    Returns whether the command has a normal exit (True), or not (False)

    """
    if not env:
        env = {}

    runCmd = _transform_cmd(cmd)
    env = _get_env(env)

    return subprocess.Popen(runCmd, shell=True, env=env).wait() == 0


def run_output(
    cmd: Union[str, List[str]], env: Optional[Dict[str, str]] = None
) -> Output:
    """
    Returns the status of the call, as well as the output
    """
    if not env:
        env = {}

    runCmd = _transform_cmd(cmd)
    env = _get_env(env)

    res = subprocess.run(runCmd, shell=True, capture_output=True, env=env)

    data = Output()
    data.stdout = res.stdout.decode("utf-8").rstrip()
    data.stderr = res.stderr.decode("utf-8").rstrip()
    data.status = res.returncode == 0

    return data


def run_conditional(*args: Callable[[], bool]) -> bool:
    """
    Runs functions in orders, on the condition the previous passes
    Functions must return a status, (True or False)

    Returns whether the command has a normal exit (True), or not (False)
    """
    for f in args:
        if not callable(f):
            print(f"{f} is not callable, bailing")
            return False

        print(f"▸ Running {f.__name__}")
        ret = f()

        # Support void functions
        if ret is None:
            return True
        if not ret:
            print(f"Task {f.__name__} failed, bailing")
            return False

    return True
