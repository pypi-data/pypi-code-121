import os
import shutil


def _get_env(port):
    return {"ZEPPELIN_PORT": str(port)}


def _get_cmd():
    executable = "zeppelin-daemon"
    cmd = [
        get_apache_zeppelin_executable(executable),
        'start'
    ]
    return cmd


def get_apache_zeppelin_executable(executable):
    # Find Apache Zeppelin daemon
    # the installation process should place it on the path
    if shutil.which(executable):
        return executable
    raise FileNotFoundError(f'Could not find {executable} in PATH')


def get_icon_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'icons', 'zeppelin.svg'
    )


def setup_apache_zeppelin():
    server_process = {
        'command': _get_cmd,
        'environment': _get_env,
        'timeout': 500,
        'new_browser_tab': True,
        'absolute_url': False,
        'launcher_entry': {
            'title': 'Zeppelin',
            'icon_path': get_icon_path()
        }
    }
    return server_process
