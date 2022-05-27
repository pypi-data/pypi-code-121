import sys
from subprocess import Popen

from exec_utils.exec_strict_error import ExecStrictError


class ExecHandlerDirect(object):
    def __init__(self, cwd=None, env=None):
        self.cwd = cwd
        self.env = env

    def prepare(self, cmd):
        self.cmd = cmd
        self.handle = Popen(self.cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=self.cwd, env=self.env)

    def wait(self):
        self.handle.wait()
        if self.handle.returncode != 0:
            raise ExecStrictError("error while executing %s" % repr(self.cmd),
                                  stdout=None,
                                  stderr=None,
                                  exit_code=self.handle.returncode)
        return None

    def kill(self):
        self.handle.kill()


def exec_strict_direct(cmd, cwd=None, env=None):
    """
    Execute a command, blocking during the execution.

    Stdout/stderr are not caputred and are forwarded to sys.stdout and sys.stderr

    raises a exec_utils.ExecStrictError if the process was not successfully.

    :param cmd: list of the command to be executed
    :param cwd: if set, the process will be started in the given directory as working directory
    :param env: if set, the given dict will be used to setup the env variable. if not set the env of the
                current process is used. Be aware, you might need to set PATH and other variables when manually
                configuring an env
    :return: None

    """

    eh = ExecHandlerDirect(
        cwd=cwd,
        env=env)

    eh.prepare(cmd)

    return eh.wait()
