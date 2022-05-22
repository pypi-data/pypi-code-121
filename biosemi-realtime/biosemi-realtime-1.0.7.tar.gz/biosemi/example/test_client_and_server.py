import subprocess
import time
import os
import signal
import pathlib
if __name__ == '__main__':
    _path, _ = os.path.split(os.path.realpath(__file__))
    default_settings = _path + os.path.sep + 'default_settings.ini'
    _this_path = pathlib.Path(__file__).parent.resolve()
    client_path = _this_path.parent.__str__() + os.path.sep + 'real_time_app.py'
    server_path = _this_path.parent.__str__() + os.path.sep + 'test_server/test_server.py'
    pid_client = subprocess.Popen([client_path, '--settings_file={:}'.format(default_settings)], shell=False)
    pid_server = subprocess.Popen(server_path, shell=False)

    time.sleep(30)
    os.kill(pid_client.pid, signal.SIGKILL)
    os.kill(pid_server.pid, signal.SIGKILL)
