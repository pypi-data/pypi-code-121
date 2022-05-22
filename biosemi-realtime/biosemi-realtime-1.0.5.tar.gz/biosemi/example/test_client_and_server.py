import subprocess
import time
import os
import signal
if __name__ == '__main__':
    _path, _ = os.path.split(os.path.realpath(__file__))
    default_settings = _path + os.path.sep + 'default_settings.ini'
    pid_client = subprocess.Popen(['../real_time_app.py', '--settings_file={:}'.format(default_settings)], shell=False)
    pid_server = subprocess.Popen('../test_server/test_server.py', shell=False)

    time.sleep(30)
    os.kill(pid_client.pid, signal.SIGKILL)
    os.kill(pid_server.pid, signal.SIGKILL)
