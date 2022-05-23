from .utils import *
import os
import json
from sys import platform
import fnmatch

MAX_FILES_STORE = 30


def get_local_data_dictionary():
    if platform == "darwin" or platform == "win32" or platform == "win64":
        # Windows
        folder = os.path.join(os.path.expanduser("~"), ".flutter_gen")
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            files = len(fnmatch.filter(os.listdir(folder), '*.*'))
            if files >= MAX_FILES_STORE:
                for file in os.scandir(folder):
                    os.remove(file.path)
        return folder
    else:
        print("This OS is not supported")


def read_json(path):
    try:
        with open(path, encoding="utf8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logError(e)


def create_file(content, file_name, file_extension=None, folder=None):
    if folder:
        if file_extension:
            file_path = "{}/{}.{}".format(folder, file_name, file_extension)
        else:
            file_path = "{}/{}".format(folder, file_name)
    else:
        if file_extension:
            file_path = "{}.{}".format(file_name, file_extension)
        else:
            file_path = "{}".format(file_name)
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content.encode("utf8"))
    except Exception as e:
        print(e)
        return None
    return file_path


def is_file_path_exist(path):
    return os.path.exists(path)
