import sys
from subprocess import PIPE, Popen

from exec_utils.exec_strict_error import ExecStrictError
from exec_utils.slurper import Slurper
from exec_utils.burper import Burper


class ExecHandler(object):
    def __init__(self, log_file=None, log_console=False, cwd=None, capture_output=True, env=None,
                 log_handle=None, return_stderr=False):
        self.log_file = log_file
        self.capture_output = capture_output
        self.cwd = cwd
        self.env = env
        self.log_console = log_console
        self.log_handle = log_handle
        self.return_stderr = return_stderr

    def prepare(self, cmd, stdin_bytes=None):
        self.cmd = cmd
        self.handle = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self.cwd, env=self.env)

        self.stdout = Slurper(self.handle.stdout, self.log_file, self.log_console,
                              self.log_handle, sys.stdout, self.capture_output)
        self.stderr = Slurper(self.handle.stderr, self.log_file, self.log_console,
                              self.log_handle, sys.stderr, self.capture_output)

        self.stdin = None

        if stdin_bytes is not None:
            stdin = Burper(stdin_bytes, self.handle.stdin)
            stdin.start()
        else:
            self.handle.stdin.close()

    def wait(self):
        self.handle.wait()

        self.stdout.join()
        self.stderr.join()

        stdout_str = self.stdout.result
        stderr_str = self.stderr.result
        if self.stdin:
            self.stdin.join()

        if self.handle.returncode != 0:
            raise ExecStrictError("error while executing %s,\nstdout: %s\nstderr: %s\n" % (
                repr(self.cmd),
                stdout_str,
                stderr_str), stdout_str, stderr_str, self.handle.returncode)
        if self.capture_output:
            if self.return_stderr:
                return stdout_str, stderr_str
            else:
                return stdout_str
        else:
            return None

    def kill(self):
        self.handle.kill()


def exec_strict(cmd, stdin_str=None, stdin_bytes=None, log_file=None,
                log_console=False, cwd=None, capture_output=True, env=None,
                log_handle=None, return_stderr=False):
    """
    Execute a command, blocking during the execution. Returns the stdout of the
    the command, and can optionally write the output (stderr and stdout) to a logfile and or the console

    raises a exec_utils.ExecStrictError if the process was not successfully.

    :param cmd: list of the command to be executed
    :param stdin_str: stdin as a str, cannot be set together with stdin_bytes
    :param stdin_bytes: stdin as byte array, cannot be set together with stdin_str
    :param log_file: if set, stdout/stderr will be written to this file, file will be opened in append mode
    :param log_console: if true, the processes stdout/stderr will be forwarded to the scripts stdout/stderr
    :param log_handle: if set, will be called for every log line
    :param cwd: if set, the process will be started in the given directory as working directory
    :param capture_output: if set to false, the process will not capture the output, default is true
    :param return_stderr: if set to True, the exec_strict call will return a tuplet containing stdout, stderr
    :param env: if set, the given dict will be used to setup the env variable. if not set the env of the
                current process is used. Be aware, you might need to set PATH and other variables when manually
                configuring an env
    :return: the stdout output, OR (stdout, stderr,) if return_stderr is set to True
    """

    if stdin_str is not None:
        if stdin_bytes is not None:
            raise ValueError('stdin_str and stdin_bytes must not both be defined.')

        stdin_bytes = stdin_str.encode("utf-8")

    eh = ExecHandler(log_file=log_file,
                     log_console=log_console,
                     cwd=cwd,
                     env=env,
                     capture_output=capture_output,
                     log_handle=log_handle,
                     return_stderr=return_stderr)

    eh.prepare(cmd, stdin_bytes)

    return eh.wait()
