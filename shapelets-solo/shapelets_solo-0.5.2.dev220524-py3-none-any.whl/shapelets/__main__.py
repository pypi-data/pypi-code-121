# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from __future__ import annotations
import argparse
import datetime
import configparser
from enum import Enum
import json
import os
import time
import typing
from pathlib import Path
import platform
import psutil
import shutil
import subprocess
import sys
import uuid
from tqdm import tqdm
from urllib.request import urlretrieve
import zipfile
import sysconfig

__config_file__ = f"{sysconfig.get_paths()['purelib']}{os.sep}shapelets{os.sep}shapelets.cfg"
if not Path(__config_file__).exists():
    __config_file__ = f"shapelets{os.sep}shapelets.cfg"
if not Path(__config_file__).exists():
    __config_file__ = f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}shapelets.cfg"
__config__ = configparser.RawConfigParser()
__config__.read(__config_file__)

__version__ = __config__.get("config", 'solo_version')
__af_version__ = __config__.get("config", 'af_version')
__python_worker_version__ = __config__.get("config", 'pyworker_version')
__libsodium_version__ = __config__.get("config", 'libsodium_version')
__server_version__ = __config__.get("config", 'server_version')
__hadoop_version__ = __config__.get("config", 'hadoop_version')
__cristal_ui_version__ = __config__.get("config", 'ui_version')

__shapelets_home__ = Path.home() / '.shapelets'
if not __shapelets_home__.exists():
    __shapelets_home__.mkdir()

__libs_folder__ = __shapelets_home__ / 'libs'
if not __libs_folder__.exists():
    __libs_folder__.mkdir()

__runtime_folder__ = __shapelets_home__ / 'runtime'
if not __runtime_folder__.exists():
    __runtime_folder__.mkdir()

# Added this in order to support python 3.8 and above
# Our libraries loads c modules using ctypes, KNOWN ISSUES
if platform.system().lower() == 'windows' and sys.version_info.major == 3 and sys.version_info.minor >= 8:
    # pylint: disable=no-member
    os.add_dll_directory(f"{__libs_folder__}")

__runtime_path_env__ = os.environ.copy()
__runtime_path_env__['PATH'] = f"{__libs_folder__}{os.pathsep}{__runtime_path_env__['PATH']}"
__runtime_path_env__['JAVA_OPTS'] = f"-Djava.library.path={__libs_folder__}"
__runtime_path_env__['SHAPELETS_SHARED_FOLDER'] = str(__shapelets_home__)

__blob_store_root__ = 'https://shapeletsbinariescdn.azureedge.net'
__af_store_root__ = f"{__blob_store_root__}/arrayfire"
__python_worker_store_root__ = f"{__blob_store_root__}/python-khiva-worker"
__libsodium_store_root__ = f"{__blob_store_root__}/libsodium"
__server_store_root__ = f"{__blob_store_root__}/shapelets"
__hadoop_store_root__ = f"{__blob_store_root__}/hadoop"
__cristal_ui_store_root__ = f"{__blob_store_root__}/cristal-ui"

__python_worker_artifact__ = f"shapelets_python_worker-{__python_worker_version__}-py3-none-any.whl"
__server_artifact__ = f"server-{__server_version__}.zip"
__hadoop_artifact__ = f"hadoop-{__hadoop_version__}.zip"
__cristal_ui_artifact__ = f"cristal-ui-{__cristal_ui_version__}.zip"

__pip_install__ = [sys.executable, '-m', 'pip', 'install']

__runtime_path_env__['__HADOOP_HOME__'] = f"{__libs_folder__}{os.pathsep}hadoop-{__hadoop_version__}"
_max_download_tries = 5


class ProcessType(Enum):
    PYTHON_WORKER = 'python'
    SERVER = 'server'

    @staticmethod
    def type_of(process_type: str) -> ProcessType:
        return dict({
            'python': ProcessType.PYTHON_WORKER,
            'server': ProcessType.SERVER,
        }).get(process_type)


class BackEndType(Enum):
    CPU = 'cpu'
    CUDA = 'cuda'
    OPEN_CL = 'opencl'


class ShapeletsProcess:
    """
    Represents a Shapelets process, one of the types defined by ProcessType.
    """

    _DETACHED_PROCESS_FLAG = 0x08000000  # no terminal window, detached process

    @staticmethod
    def pid_files():
        return (file for file in os.listdir(__runtime_folder__) if file.endswith('.txt'))

    @staticmethod
    def report_status():
        for pid_file in ShapeletsProcess.pid_files():
            ShapeletsProcess.load_from_file(pid_file).print_status()

    @staticmethod
    def load_from_file(pid_file: str) -> ShapeletsProcess:
        with open(__runtime_folder__ / pid_file, 'r') as pid_metadata:
            metadata = json.load(pid_metadata)
            instance = ShapeletsProcess(ProcessType.type_of(metadata['type']))
            instance.process_port = metadata['port']
            instance.process_backend = metadata['backend']
            instance.process_start = metadata['start']
            instance.process_cwd = metadata['cwd']
            instance.process_pid = metadata['pid']
        return instance

    def __init__(self, process_type: ProcessType, process_port: str = '443', process_backend: str = 'CPU'):
        self.process_cwd = str(uuid.uuid1())
        self.process_type = process_type
        self.process_port = process_port
        self.process_backend = process_backend
        self.process_pid = None
        self.process_start = None

    def run_detached(self, command: typing.List[str]):
        # check can run and do maintenance
        for pid_file in ShapeletsProcess.pid_files():
            proc = ShapeletsProcess.load_from_file(pid_file)
            if (proc.process_type == self.process_type and proc.process_port == self.process_port):
                if proc.is_running:
                    return
                else:
                    proc.clear_persisted()
        process_cwd = __runtime_folder__ / self.process_cwd
        process_cwd.mkdir()
        if platform.system().lower() == 'windows':
            self.process_pid = str(subprocess.Popen(
                command,
                creationflags=ShapeletsProcess._DETACHED_PROCESS_FLAG,
                env=__runtime_path_env__,
                cwd=process_cwd).pid)
        else:
            self.process_pid = str(subprocess.Popen(
                command,
                env=__runtime_path_env__,
                cwd=process_cwd).pid)
        self.process_start = str(datetime.datetime.utcnow())
        self._persist()

    @property
    def is_running(self) -> bool:
        return psutil.pid_exists(int(self.process_pid))

    def kill(self):
        if self.is_running:
            process = psutil.Process(int(self.process_pid))
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
            print(self)

    def tail_logs(self):
        logs_file = __runtime_folder__ / self.process_cwd / 'log'
        if self.process_type == ProcessType.SERVER:
            logs_file /= 'log.txt'
        if self.process_type == ProcessType.PYTHON_WORKER:
            logs_file /= 'worker-python.log'
        try:
            with open(logs_file, 'r') as file:
                line = ''
                while True:
                    tmp = file.readline()
                    if tmp is not None:
                        line += tmp
                        if line.endswith('\n'):
                            print(line, end='')
                            line = ''
                    else:
                        time.sleep(1)
        except KeyboardInterrupt:
            pass

    def to_dict(self):
        return {
            'type': self.process_type.value,
            'port': self.process_port,
            'backend': self.process_backend,
            'start': self.process_start,
            'cwd': self.process_cwd,
            'pid': self.process_pid,
        }

    def clear_persisted(self):
        os.remove(__runtime_folder__ / self._persist_file_name)
        for _ in range(3):
            try:
                shutil.rmtree(__runtime_folder__ / self.process_cwd)
            except:
                time.sleep(1)
                pass

    @property
    def _persist_file_name(self):
        return f"{self.process_cwd}_{self.process_type.value}_{self.process_pid}.txt"

    def _persist(self):
        with open(__runtime_folder__ / self._persist_file_name, 'w') as pid_file:
            json.dump(self.to_dict(), pid_file, indent=4)
        print(self)
        print(self)

    def __str__(self):
        str_repr = f"{self.process_type.value} "
        str_repr += f"{'OK' if self.is_running else 'DEAD'}: "
        str_repr += f"port:{self.process_port}, "
        str_repr += f"backend:{self.process_backend}, "
        str_repr += f"start:{self.process_start}, "
        str_repr += f"cwd:{self.process_cwd}, "
        str_repr += f"pid:{self.process_pid}"
        return str_repr

    def print_status(self):
        print(self)


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def _check_sha_file(filename) -> str:
    # Python program to find SHA256 hash string of a file
    import hashlib

    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 1M
        for byte_block in iter(lambda: f.read(1048576), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def _download_artifact_with_retries(src_url, dst_artifact, report=True):
    count = 0
    download_successful = False
    while not download_successful and count < _max_download_tries:
        try:
            if report:
                with DownloadProgressBar(unit='B',
                                         unit_scale=True,
                                         unit_divisor=1024,
                                         miniters=1,
                                         desc=src_url.split('/')[-1]) as progress_bar:
                    urlretrieve(src_url, dst_artifact, reporthook=progress_bar.update_to)
            else:
                urlretrieve(src_url, dst_artifact)
            download_successful = True
        except ConnectionResetError as e:
            print(f"The connection was closed while downloading the file {src_url}")
            print(f"Retrying to download file {src_url}")
            count += 1
            os.remove(dst_artifact)

    if not download_successful:
        print(f"Aborting to download file {src_url} after {_max_download_tries} tries")
        return None


def _fetch_sha_file(base_url, dst_root, file_name) -> str:
    src_url = f"{base_url}/{file_name}.sha"
    dst_artifact = f"{dst_root}/{file_name}.sha"
    _download_artifact_with_retries(src_url, dst_artifact, False)

    with open(dst_artifact) as f:
        fetched_sha = f.read()

    return fetched_sha


def _download_resource(base_url: str,
                       dst_root: Path,
                       file_name: str,
                       force: bool = False,
                       unzip: bool = True,
                       pip_install: bool = False,
                       check_sha: bool = True) -> Path:
    src_url = f"{base_url}/{file_name}"
    dst_artifact = dst_root / file_name
    if dst_artifact.exists() and not force:
        print(f"Artifact [{file_name}] already downloaded, try again with [-f True]")

    else:
        print(f"Downloading {src_url} to {dst_root}")
        _download_artifact_with_retries(src_url, dst_artifact)

        if check_sha:
            computed_sha = _check_sha_file(dst_artifact)
            original_sha = _fetch_sha_file(base_url, dst_root, file_name)
            if computed_sha != original_sha:
                os.remove(dst_artifact)
                os.remove(f"{dst_artifact}.sha")
                print(f"The file {file_name} seems to be corrupted. Try to install again")
                return None

        if unzip:
            with zipfile.ZipFile(dst_artifact, 'r') as zip_ref:
                for file in tqdm(iterable=zip_ref.namelist(), total=len(zip_ref.namelist())):
                    zip_ref.extract(member=file, path=dst_root)

    if pip_install:
        subprocess.check_call(
            __pip_install__ + [str(dst_artifact)],
            env=__runtime_path_env__)
    return dst_artifact


def install_command(force: bool = False):
    system_name = platform.system().lower()

    _download_resource(
        __af_store_root__,
        __libs_folder__,
        f"arrayfire-full-{system_name}-{__af_version__}.zip",
        force=force)
    _download_resource(
        __python_worker_store_root__,
        __libs_folder__,
        __python_worker_artifact__,
        force=force,
        unzip=False,
        pip_install=True)
    if platform.system().lower() == 'windows':
        _download_resource(
            __libsodium_store_root__,
            __libs_folder__,
            f"libsodium-{system_name}-{__libsodium_version__}.zip",
            force=force)
    _download_resource(
        __hadoop_store_root__,
        __libs_folder__,
        __hadoop_artifact__,
        force=force)
    _download_resource(
        __cristal_ui_store_root__,
        __libs_folder__,
        __cristal_ui_artifact__,
        force=force)
    _download_resource(
        __server_store_root__,
        __libs_folder__,
        __server_artifact__,
        force=force)


def _update_resource(base_url: str,
                     dst_root: Path,
                     file_name: str,
                     force: bool = False,
                     unzip: bool = True,
                     pip_install: bool = False):
    dst_artifact = dst_root / file_name

    if not dst_artifact.exists() or _check_sha_file(dst_artifact) != _fetch_sha_file(base_url, dst_root, file_name):
        _download_resource(
            base_url,
            dst_root,
            file_name,
            force=force,
            unzip=unzip,
            pip_install=pip_install
        )
        print(f"The dependency {file_name} has been updated.")
    else:
        print(f"The dependency {file_name} is up to date.")


def update_command():
    system_name = platform.system().lower()
    force = True

    _update_resource(
        __af_store_root__,
        __libs_folder__,
        f"arrayfire-full-{system_name}-{__af_version__}.zip",
        force=force)

    _update_resource(
        __python_worker_store_root__,
        __libs_folder__,
        __python_worker_artifact__,
        force=force,
        unzip=False,
        pip_install=True)

    if platform.system().lower() == 'windows':
        _update_resource(
            __libsodium_store_root__,
            __libs_folder__,
            f"libsodium-{system_name}-{__libsodium_version__}.zip",
            force=force)

    _update_resource(
        __hadoop_store_root__,
        __libs_folder__,
        __hadoop_artifact__,
        force=force)

    _update_resource(
        __cristal_ui_store_root__,
        __libs_folder__,
        __cristal_ui_artifact__,
        force=force)

    _update_resource(
        __server_store_root__,
        __libs_folder__,
        __server_artifact__,
        force=force)


def worker_command_start(worker_type: str, port: str, backend: str):
    worker_type = ProcessType.type_of(worker_type)
    if worker_type == ProcessType.PYTHON_WORKER:
        proc = ShapeletsProcess(ProcessType.PYTHON_WORKER, process_port=port, process_backend=backend)
        proc.run_detached(['python-worker', '-p', port, '-b', backend])
    else:
        sys.stderr.write(f"unknown worker type: {worker_type}")
        sys.exit(-1)


def server_command_start():
    if platform.system().lower() == 'windows':
        specific_script = 'server.bat'
    else:
        specific_script = 'server'

    server_exe = str(__libs_folder__ / f'server-{__server_version__}' / 'bin' / specific_script)
    if platform.system().lower() != 'windows':
        os.chmod(server_exe, 0o777)
    ShapeletsProcess(ProcessType.SERVER).run_detached([server_exe])


def start_all_command():
    worker_command_start(ProcessType.PYTHON_WORKER.value, '52000', 'CPU')
    server_command_start()


def stop_command(process_pid: str = None):
    stop_all = process_pid is None or process_pid in ('*', 'all', 'ALL', '.')
    for pid_file in ShapeletsProcess.pid_files():
        proc = ShapeletsProcess.load_from_file(pid_file)
        if stop_all or proc.process_pid == process_pid:
            proc.kill()
            proc.clear_persisted()


def tail_command(system_pid: str):
    for pid_file in ShapeletsProcess.pid_files():
        proc = ShapeletsProcess.load_from_file(pid_file)
        if proc.process_pid == system_pid:
            proc.tail_logs()


def install_backend(backend: str):
    compute_install = ['shapelets-compute', 'install']
    subprocess.run(compute_install + [backend], shell=True, env=__runtime_path_env__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shapelets run-time tools')
    subparsers = parser.add_subparsers(dest='command')

    # install command
    install_parser = subparsers.add_parser('install', help='Installs required 3rd party libs')
    install_parser.add_argument('-f', '--force', default=False, type=bool)
    install_parser.add_argument('-b', '--backend',
                                choices=[BackEndType.CPU.value, BackEndType.CUDA.value, BackEndType.OPEN_CL.value],
                                type=str)

    # install shapelets-compute backend command
    backend_parser = subparsers.add_parser('backend', help='Installs Shapelets-compute backend command')
    backend_parser.add_argument('-b', '--backend',
                                choices=[BackEndType.CPU.value, BackEndType.CUDA.value, BackEndType.OPEN_CL.value],
                                default=BackEndType.CPU.value,
                                type=str)

    # update command
    update_parser = subparsers.add_parser('update', help='Updates Shapelets dependencies')

    # start command
    start_parser = subparsers.add_parser('start', help='Starts a Shapelets process')
    start_command_parser = start_parser.add_subparsers(dest='start_command')
    start_worker_parser = start_command_parser.add_parser('worker', help='Starts a Shapelets worker')
    start_worker_parser.add_argument('-t', '--type',
                                     choices=[ProcessType.PYTHON_WORKER.value],
                                     default=ProcessType.PYTHON_WORKER.value,
                                     type=str)
    start_worker_parser.add_argument('-p', '--port', default='52000', type=str)
    start_worker_parser.add_argument('-b', '--backend', choices=['CPU', 'GPU'], default='CPU', type=str)
    start_server_parser = start_command_parser.add_parser('server', help='Starts the Shapelets server')

    # restart command
    restart_parser = subparsers.add_parser('restart', help='Restarts all Shapelets processes')
    restart_command_parser = restart_parser.add_subparsers(dest='restart_command')

    # status command
    status_parser = subparsers.add_parser('status', help='Reports the status of the system')

    # stop command
    stop_parser = subparsers.add_parser('stop', help='Stops a Shapelets process by pid')
    stop_parser.add_argument('-p', '-pid', '--pid', type=str,
                             help='["*", "all", "ALL", "." to stop all], pid or type (1st col)')

    # logs command
    tail_parser = subparsers.add_parser('tail', help='Tails the logs for a Shapelets process by pid')
    tail_parser.add_argument('-p', '-pid', '--pid', type=str, help='pid or type (1st col)')

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()

    elif args.command == 'install':
        install_command(args.force)

    elif args.command == 'backend':
        install_backend(args.backend)

    elif args.command == 'update':
        update_command()

    elif args.command == 'start':
        if args.start_command is None:
            start_all_command()
        elif args.start_command == 'server':
            server_command_start()
        elif args.start_command == 'worker':
            worker_command_start(args.type, args.port, args.backend)

    elif args.command == 'restart':
        stop_command()
        start_all_command()

    elif args.command == 'status':
        ShapeletsProcess.report_status()

    elif args.command == 'stop':
        stop_command(args.pid)

    elif args.command == 'tail':
        if not args.pid:
            tail_parser.print_help()
        else:
            tail_command(args.pid)
