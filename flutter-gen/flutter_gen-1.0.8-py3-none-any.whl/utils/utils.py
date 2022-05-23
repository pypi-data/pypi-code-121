import yaml
import subprocess
import os
import requests
import shutil

from .intellij import Intellij
from ..rename.config import Config
from tqdm.auto import tqdm


def download_file(url, path):
    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
            with open(path, 'wb')as output:
                shutil.copyfileobj(raw, output)


def get_current_dart_package_name():
    pubspec_text = read("pubspec.yaml")
    pubspec_data = yaml.safe_load(pubspec_text)
    name = pubspec_data["name"]
    return name


def get_current_rename_config():
    pubspec_text = read("pubspec.yaml")
    pubspec_data = yaml.safe_load(pubspec_text)
    name = pubspec_data["name"]
    flutter_rename_app = pubspec_data["flutter_rename_app"]
    application_name = flutter_rename_app["application_name"]
    dart_package_name = flutter_rename_app["dart_package_name"]
    application_id = flutter_rename_app["application_id"]
    bundle_id = flutter_rename_app["bundle_id"]
    android_package_name = flutter_rename_app["android_package_name"]
    return Config(
        name,
        application_name,
        dart_package_name,
        application_id,
        bundle_id,
        android_package_name,
    )


def read(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


def git(*args):
    try:
        subprocess.check_call(["git"] + list(args))
    except Exception as e:
        print(e)


def change_working_dir(path):
    try:
        os.chdir(path)
        print("Current working directory: {0}".format(os.getcwd()))
    except FileNotFoundError:
        print("Directory: {0} does not exist".format(path))
    except NotADirectoryError:
        print("{0} is not a directory".format(path))
    except PermissionError:
        print("You do not have permissions to change to {0}".format(path))


def list_to_separated_string(list: list, delimiter: str):
    return delimiter + delimiter.join(list)


def logError(message):
    print(message)
    Intellij.getInstance().add_error(str(message))


def log(message):
    print(message)
    Intellij.getInstance().add_message(str(message))


def logResult(data):
    print(data)
    Intellij.getInstance().add_result(str(data))


def logAndOpenfile(path):
    Intellij.getInstance().add_message("[Open File] {}".format(path))
    Intellij.getInstance().add_open_file(str(path))


def logAndCommand(command):
    Intellij.getInstance().add_message("[Command] {}".format(command))
    Intellij.getInstance().add_command(str(command))
