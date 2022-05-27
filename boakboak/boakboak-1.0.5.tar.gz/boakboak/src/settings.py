# settings.py
import os, sys

# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
appBasePath = os.path.split(settingsPath)[0]
sysArgsException = f"\nProvide a program alias to be run, see list below:"

# runntime parrameters for running apps
appsParamsDir = os.path.join(appBasePath, "apps")
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

# testing
testPath = os.path.join(appBasePath, "testing")

# os seperator correction
os_sep_adj = lambda x: x.replace("/", os.sep)
