# settings.py
import os, sys
from contextlib import contextmanager
from pathlib import Path

# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
srcPath = os.path.split(settingsPath)[0]
appBasePath = os.path.split(srcPath)[0]
sysArgsException = f"\nProvide a program alias to be run, see list below:"

# runntime parrameters for running apps
appsParamsDir = os.path.join(srcPath, "apps")
appPathAliass = [".", ""]
allApps = "*"
defaultName = "boakboak"
paramsFileExt = ".yml"
exceptionMsg = f"\nRunntime args, kwargs not found: NOTE: use '*' to run all"
fatal = f"found nothing, check your parameters app !"

# signal parameters to indicate venv location
activators = [".venv", "Pipfile"]
packageIndicator = "__init__.py"
venvsPaths = {
    "nt": [".virtualenvs", "Scripts/python.exe"],
    "unix not confirmed": [".local/share/virtualenvs"],
}

# test
testPath = os.path.join(srcPath, "test")

# Path function settings
# os seperator correction
os_sep = lambda x: os.path.abspath(x)


@contextmanager
def temp_chdir(path: Path) -> None:
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
