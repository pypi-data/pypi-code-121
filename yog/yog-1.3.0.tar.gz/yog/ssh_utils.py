import logging
import os
import re
import subprocess
from hashlib import sha512
from random import randrange
from re import Pattern
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Tuple, List, Optional, Set

from paramiko import SSHClient, PKey

log = logging.getLogger(__name__)


def check_call(ssh: SSHClient, command: str, assert_stderr_empty: bool = False, send_stdin: Optional[str] = None, ):
    stdin, stdout, stderr = ssh.exec_command(command)
    if send_stdin is not None:
        stdin.write(send_stdin)
    stdin.close()
    rc = stdout.channel.recv_exit_status()

    if rc != 0:
        print(f"'{command}' returned exit code {rc}")
        _dump_lines("stdout", stdout.readlines())
        _dump_lines("stderr", stderr.readlines())
        raise NonzeroExitCodeError(rc)

    if assert_stderr_empty:
        stderr_contents = stderr.readlines()
        if stderr_contents:
            print(f"'{command}' expected empty stderr but it wasn't empty.")
            _dump_lines("stderr", stderr.readlines())
            raise StdErrNotEmptyError(stderr_contents)


def check_output(ssh: SSHClient, command: str, send_stdin: Optional[str] = None) -> Tuple[List[str], List[str]]:
    stdin, stdout, stderr = ssh.exec_command(command)
    if send_stdin is not None:
        stdin.write(send_stdin)

    rc = stdout.channel.recv_exit_status()

    if rc != 0:
        _dump_lines("stdout", stdout.readlines())
        _dump_lines("stderr", stderr.readlines())
        raise NonzeroExitCodeError(rc)

    return stdout.readlines(), stderr.readlines()


def check_code(ssh: SSHClient,
               command: str,
               assert_stderr_empty: bool = False,
               send_stdin: Optional[str] = None,
               assert_stdout_empty: bool = False
               ) -> bool:
    stdin, stdout, stderr = ssh.exec_command(command)
    if send_stdin is not None:
        stdin.write(send_stdin)
    rc = stdout.channel.recv_exit_status()

    if rc != 0:
        return False

    if assert_stderr_empty:
        stderr_contents = stderr.readlines()
        if stderr_contents:
            return False

    if assert_stdout_empty:
        stdout_contents = stdout.readlines()
        if stdout_contents:
            return False

    return True


def check_stdout(ssh: SSHClient, command: str) -> str:
    return check_output(ssh, command)[0]


def check_stderr(ssh: SSHClient, command: str) -> str:
    return check_output(ssh, command)[1]


def _dump_lines(title: str, lines: List[str]):
    print(f"--------------{title}------------")
    for line in lines:
        print(line)
    print("--------------------------------")


class NonzeroExitCodeError(RuntimeError):
    code: int

    def __init__(self, code: int):
        self.code = code


class StdErrNotEmptyError(RuntimeError):
    contents: List[str]

    def __init__(self, contents: List[str]):
        self.contents = contents


def get_host_key(ssh: SSHClient) -> PKey:
    return ssh.get_transport().get_remote_server_key()


def get_pids_binding_port(bound_port: int) -> Set[int]:
    lsof_lines = str(subprocess.check_output(["lsof", "-i", f":{bound_port}"]), encoding="utf-8")
    lsof_lines = lsof_lines.splitlines()[1:]
    lsof_lines = [re.split(r"\s+", str(l)) for l in lsof_lines]
    pids_bound = {int(l[1]) for l in lsof_lines if l[4] == "IPv4"}
    return pids_bound


# always prints:
# debug1: Local forwarding listening on 127.0.0.1 port 44444.
# this means success:
# debug1: channel 0: new [port listener]

success_pattern: Pattern = re.compile(r"^(debug1: channel \d+: new \[port listener])|(debug1: remote forward success for: listen \d+, connect localhost:\d+)$")


def _render_cmd(rand_port, prefix, host, forward_flag, expr):
    return prefix + ["ssh", "-v", "-4", "-o", "ExitOnForwardFailure=yes",
                     "-N", forward_flag, expr.format(rand_port),
                     host]

# 2 bugs:
# * stderr will keep printing but i've stopped reading it. This will cause a deadlock eventually. fix by just moving to
#  a new thread and babysitting stderr there
# * when proxying, remote ssh process doesn't die when local ssh process dies. this keeps the port bound.

# crazy idea: fuck asyncio, fuck threads, etc. Popen(bash -c ssh 2>/tmp/namedtmpfile) and then fucking read
# the tempfile over and over till I find my shit.


class ScopedProxiedRemoteSSHTunnel:
    proxy_host: Optional[str]
    host: str
    port_forwarded: int
    forward_type: str

    proc: Optional[subprocess.Popen]

    def __init__(self, host: str,
                 port_forwarded: int,
                 proxy_host: Optional[str] = None,
                 forward_type: str = "local",
                 force_random_port: int = None):
        self.host = host
        self.port_forwarded = port_forwarded
        self.proxy_host = proxy_host
        self.forward_type = forward_type
        self.force_random_port = force_random_port

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self) -> int:
        if self.forward_type == "local":
            forward_flag = "-L"
            forward_expr = f"{{}}:localhost:{self.port_forwarded}"
        elif self.forward_type == "remote":
            forward_flag = "-R"
            forward_expr = f"{self.port_forwarded}:localhost:{{}}"
        else:
            raise ValueError(f"Illegal value for forward_type: \"{self.forward_type}\" must be one of local, remote")

        if self.proxy_host is not None:
            cmd_prefix = ["ssh", "-t", "-t", self.proxy_host]
        else:
            cmd_prefix = []

        self.proc, rport = _setup_tunnel(cmd_prefix, self.host, forward_flag, forward_expr, self.force_random_port)
        return rport

    def disconnect(self):
        if self.proc is not None:
            self.proc.kill()
            log.debug(f"SSH tunnel ended.")


def _setup_tunnel(cmd_prefix, host, forward_flag, forward_expr, force_random_port=None) -> Tuple[subprocess.Popen, int]:
    tries = 25
    port = None
    proc = None
    while tries > 0 and proc is None:
        if force_random_port is None:
            port = randrange(1024, 65535 + 1)
        else:
            port = force_random_port
        cmd = _render_cmd(port, cmd_prefix, host, forward_flag, forward_expr)
        stderr_file = NamedTemporaryFile("w", delete=False)
        stdout_file = NamedTemporaryFile("w", delete=False)
        try:
            proc = _try_setup_tunnel(port, cmd, stdout_file, stderr_file)
        except RuntimeError as e:
            log.info(f"SSH tunnel open threw exception. Tries left: {tries}", exc_info=e)
            tries -= 1
        finally:
            os.remove(stderr_file.name)
            os.remove(stdout_file.name)

    if proc is None:
        log.error(f"Gave up. Couldn't open ssh tunnel.")
        raise RuntimeError(f"Couldn't open SSH tunnel.")

    if port is None:
        raise RuntimeError("port was none. this should never happen.")
    return proc, port


def _try_setup_tunnel(port: int, cmd: List[str], stdout_file: NamedTemporaryFile, stderr_file: NamedTemporaryFile) -> Optional[subprocess.Popen]:
    proc = subprocess.Popen(cmd, stdout=stdout_file, stderr=stderr_file, stdin=subprocess.PIPE)
    confirmed = False
    timeout = 10.0
    while not (confirmed or proc.returncode is not None) and timeout > 0:
        sleep(0.1)
        timeout -= 0.1
        for fobj in [stdout_file, stderr_file]:
            fobj.flush()
            with open(fobj.name, "r") as fin:
                for line in fin:
                    if success_pattern.match(line.strip()):
                        confirmed = True

    if not confirmed:
        outputs = []
        for fileobj in [stdout_file, stderr_file]:
            with open(fileobj.name, "r") as fin:
                outputs.append(fin.read())
        stderr = "\n".join(outputs)
        if "Address already in use" in stderr:
            log.info(f"Port {port} already in use.")
        else:
            log.error(f"SSH tunnel didn't stay open. Weird.")
            log.error("--------------ssh stderr-------------------")
            log.error(stderr)
            log.error("--------------end ssh stderr---------------")
        return None
    else:
        log.debug(f"SSH tunnel started.")
        return proc


def compare_local_and_remote(body: bytes, remote_path: str, ssh: SSHClient, root: bool = False):
    expected: str = sha512(body).hexdigest()

    found: Optional[str]
    if check_code(ssh, f"{'sudo ' if root else ''}test -f \"{remote_path}\""):
        found: str = re.split(r"\s+", check_output(ssh, f"{'sudo ' if root else ''}sha512sum \"{remote_path}\"")[0][0], 1)[0]
    else:
        found = None

    return expected == found, expected, found
