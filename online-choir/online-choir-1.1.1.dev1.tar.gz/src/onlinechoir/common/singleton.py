import os
import psutil
from pathlib import Path

from .log import logger
from .platform import get_log_folder


def _pid_file_path(name: str) -> Path:
    return get_log_folder() / (name + '.pid')


def _check_other_processes(name: str, pid: int, process_name: str):
    pid_file = _pid_file_path(name)
    if not pid_file.exists():
        return
    tokens = pid_file.read_text().split(",")
    if len(tokens) != 2:
        return
    try:
        prev_pid = int(tokens[0])
    except ValueError:
        return  # ignore malformed files
    prev_process_name = tokens[1]
    try:
        prev_process = psutil.Process(prev_pid)
    except psutil.NoSuchProcess:
        return
    if prev_pid == os.getpid():
        return  # either own process or dead process
    if prev_process.name() != prev_process_name:
        return  # another process incidentally has the same PID
    raise RuntimeError(f"Another instance of the app is running with PID {prev_process}")


def register_process(name: str):
    own_pid = os.getpid()
    own_process_name = psutil.Process(own_pid).name()
    _check_other_processes(name, own_pid, own_process_name)
    with _pid_file_path(name).open('w') as fd:
        fd.write(f"{own_pid},{own_process_name}")


def unregister_process(name: str):
    pid_file = _pid_file_path(name)
    if not pid_file.exists():
        logger.error(f"PID file missing")
        return
    pid_file.unlink()
