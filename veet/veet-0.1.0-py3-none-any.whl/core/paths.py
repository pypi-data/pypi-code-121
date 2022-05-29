import os

PROJECT_PATH = os.getcwd()
APP_PATH = os.path.join(PROJECT_PATH, 'app')
ROUTES_PATH = os.path.join(PROJECT_PATH, 'routes')
COMMANDS_PATH = os.path.join(PROJECT_PATH, 'commands')
COMMANDS_PATH_APP = os.path.join(PROJECT_PATH, 'app', 'commands')


def list_dir(dir: str):
    modules = [os.path.splitext(_file)[0] for _file in os.listdir(
        dir) if not _file.startswith('__') and not _file.startswith('.')]

    return modules
