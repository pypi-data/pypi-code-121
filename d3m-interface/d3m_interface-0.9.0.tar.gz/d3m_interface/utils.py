import shutil
import platform
import socket
from os.path import exists, abspath


def fix_path_for_docker(path):
    if platform.system() == 'Windows':
        path = path.replace('\\', '/')
    return path


def copy_folder(source_path, destination_path, remove_destination=False):
    if remove_destination and exists(destination_path):
        shutil.rmtree(destination_path)

    shutil.copytree(source_path, destination_path)


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def is_openml_dataset(url):
    return url.startswith('https://www.openml.org/')
