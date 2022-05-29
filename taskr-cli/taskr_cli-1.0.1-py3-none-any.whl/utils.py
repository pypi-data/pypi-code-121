"""
A collection of some python library/project specific utilities.
Possibly more generic ones to follow
"""
import glob
import os
import shutil
import sys
from typing import Dict, Optional


def _removeFolder(path: str, root: str = "./") -> None:
    shutil.rmtree(os.path.join(root, path), ignore_errors=True)


def cleanBuilds() -> bool:
    """
    Finds common build/dist fdlders and removes them recursively from the base
    of the project, where 'tasks.py' is
    """
    try:
        _removeFolder("dist")
        _removeFolder("build")

        ret = glob.glob("*egg-info")
        if len(ret) > 0:
            _removeFolder(ret[0])

        return True

    except Exception as e:
        print(f"Error removing build files: {e}")
        return False


def cleanCompiles() -> bool:
    """
    Finds compiled (.pyc) files and removes them recursively from the base
    of the project, where 'tasks.py' is
    """
    try:
        for root, dirs, files in os.walk(".", topdown=False):
            if "__pycache__" in dirs:
                _removeFolder("__pycache__", root)
            for name in files:
                if ".pyc" in name:
                    os.remove(os.path.join(root, name))

        return True

    except Exception as e:
        print(f"Error cleaning compiled folders: {e}")
        return False


def inVenv() -> bool:
    """
    Let's you know if you're in a virtual environment or not.
    """
    return sys.prefix != sys.base_prefix or os.environ.get("VIRTUAL_ENV") is not None


def readEnvFile(filename: str) -> Dict[str, str]:
    """
    Reads in a file of ENV settings and returns a Dict
    Ana alternative way of running 'source vars.env' before a command
    """
    if not os.path.exists(filename):
        print(f"Environment File {filename} not found")
        return {}

    ret = {}
    try:
        with open(filename) as file:
            for line in file:
                pair = line.split("=")
                ret[pair[0].strip()] = pair[1].strip()
    except Exception as e:
        print(f"Error processing .env file: {e}. Skipping")

    return ret


def _bump(version: str) -> str:
    """
    Internal function for easier testing
    TODO - use regex maybe - seems overkill
    """
    cleaned = version.replace("'", "").replace(",", "").replace('"', "")  # "1.2.3"
    verSplit = cleaned.split(".")  # ["1", "2", "3"]
    oldMinor = verSplit[2].strip()  # "3"
    newMinor = str(int(oldMinor) + 1)  # "4"
    newVersion = f"{verSplit[0]}.{verSplit[1]}.{newMinor}"  # "1.2.4"
    return newVersion


def bumpVersion(version: Optional[str] = None) -> bool:
    """
    Bumps the minor version in setup.py by 1, or the given argument
    May support other files in the future
    """
    filename = "setup.py"

    with open(filename, "r") as fd:
        temp = fd.read()

    try:
        out = []
        for line in temp.split("\n"):
            if "version=" in line:
                toReplace = line.split("=")[1]
                if version is None:
                    version = _bump(toReplace)
                line = line.replace(toReplace, f'"{version}",')
                out.append(line)
            else:
                out.append(line)
    except Exception as e:
        raise Exception(f"while bumping version: {e}")

    with open(filename, "w") as fd:
        fd.write("\n".join(out))

    return True


def addTaskrToEnv() -> bool:
    """
    Adds an environment variable to a venv to allow taskr to run from anywhere
    This seems horrible but... whatever
    """
    return _injectPath({'TASKR_DIR': os.getcwd()})


def _injectPath(envs: Dict[str, str]) -> bool:
    """
    Add environment variable to venv activation script,
    so they are applied when you load a venv

    TODO
        - Any tests?
        - Generate script for this instead and just add that
          to the script?

    """
    if not inVenv():
        print("Not in virtual environment, can't modify")
        return False

    envLocation = os.environ["VIRTUAL_ENV"]
    command = "export"
    file = "activate"

    if "win" in sys.platform:
        command = "set"
        file = "activate.bin"

    activationScript = os.path.join(envLocation, f"bin/{file}")
    print(f"Editing {activationScript}")

    if not os.path.exists(activationScript):
        print("Activation script not found, can't edit")
        return False

    temp = envs.copy()
    with open(activationScript, 'r') as f:
        for k, v in temp.items():
            if k in f.read():
                print(f"{k} already in script, skipping")
                del envs[k]

    if len(envs) > 1:
        with open(activationScript, "a") as myfile:
            for k, v in envs.items():
                myfile.write(f"\n{command} {k}={v}\n")

        print("venv script modified, reload to take affect")

    return True
