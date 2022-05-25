import os.path
import sys
import threading
import time
import urllib
import webbrowser
from subprocess import Popen

from ..model.build_pack import BuildPack
from ..output_callback import OutputCallBack
from ..util import execute, run_process


class ClosableProcessWrapperThread(threading.Thread):
    def __init__(self, process: Popen, callback):
        super(ClosableProcessWrapperThread, self).__init__()
        self.process: Popen = process
        self.callback: OutputCallBack = callback

    def stop(self):
        self.process.terminate()

    def run(self):
        pid = self.process.pid
        while True:
            nextline = self.process.stdout.readline()
            if nextline == "" and self.process.poll() is not None:
                break
            self.callback.print_line(f"[{pid}] {nextline.strip()}")
        self.callback.print_line("Process Finished.")


def deploy(
    build_pack: BuildPack, component, package_dir, build_dir, callback: OutputCallBack
):
    virtualenv = f"{build_dir}/virtualenv.pyz"
    if not os.path.isfile(virtualenv):
        callback.print_header("Going to download virtualenv")
        urllib.request.urlretrieve(
            "https://bootstrap.pypa.io/virtualenv.pyz", virtualenv
        )

    python_location = sys.executable

    venv = f"{build_dir}/venv"
    if not os.path.isdir(venv):
        callback.print_header("Going to create virtualenv")
        cmd = [python_location, virtualenv, venv]
        for line in execute(cmd):
            callback.print_line(line)

    callback.print_header("Going to install dependency")
    for requirement_file in build_pack.local.requirement_files:
        cmd = [f"{venv}/bin/pip", "install", "-r", f"{package_dir}/{requirement_file}"]
        for line in execute(cmd):
            callback.print_line(line.rstrip())

    callback.print_header(f"Going to run local service in background.\n")
    command = build_pack.local.run_command
    command = f"{venv}/bin/{command}"
    callback.print_line(f"Going to execute command {command}")
    cmd = command.split(" ")
    thread = ClosableProcessWrapperThread(run_process(cmd), callback)
    thread.start()

    url = f"http://127.0.0.1:{component['spec']['container']['ports'][0]['containerPort']}"
    callback.print_line(f"Service will be up on {url}")
    webbrowser.open(url)

    return thread
