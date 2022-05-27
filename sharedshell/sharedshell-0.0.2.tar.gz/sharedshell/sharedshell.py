import os
import platform
import signal
import subprocess
import types
from contextlib import ContextDecorator

PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
DEVNULL = subprocess.DEVNULL

class SharedShell(ContextDecorator):
    """ A context dependent new shell. """

    _shell_resource = None

    _MARKER_BEGIN = '#### BEGIN ####'
    _MARKER_END = '#### END ####'
    _ERROR = ' WITH ERROR ####'

    def __init__(self):
        """ Initialize the shell. """

        self._shell_resource = subprocess.Popen(
            'cmd /V:ON' if platform.system() == 'Windows' else 'sh',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )

    def __enter__(self):
        """ Enter context. """

        return self

    def __exit__(self, *_exc):
        """ Free the shell resources. """

        os.kill(self._shell_resource.pid, signal.SIGTERM)

    def run(self, cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        """ Executes the command string. """

        shell = self._shell_resource

        shell.stdin.write(
            'echo {quote}{marker}{quote}{sep}'.format(
                marker=self._MARKER_BEGIN,
                quote='' if platform.system() == 'Windows' else '\'',
                sep=os.linesep
            )
        )
        shell.stdin.write(
            '(({cmd} && echo {marker} && >&2 echo {marker}) || (echo {quote}{error}{quote} && >&2 echo {marker})){sep}'.format(
                cmd=cmd_str,
                marker='{quote}{marker}{quote}'.format(marker=self._MARKER_END, quote='' if platform.system() == 'Windows' else '\''),
                quote='' if platform.system() == 'Windows' else '\'',
                error=self._MARKER_END + self._ERROR,
                sep=os.linesep
            )
        )
        shell.stdin.flush()

        line = shell.stdout.readline().rstrip()
        while line != self._MARKER_BEGIN:
            line = shell.stdout.readline().rstrip()
        if platform.system() == 'Windows':
            line = shell.stdout.readline() # nueva línea al final del echo
            line = shell.stdout.readline() # la línea echo del comando
        out = ''
        line = shell.stdout.readline().rstrip()
        while not line.startswith(self._MARKER_END):
            out = out + line + os.linesep
            line = shell.stdout.readline().rstrip()

        err = ''
        line = shell.stderr.readline().rstrip()
        while not line.startswith(self._MARKER_END):
            err = err + line + os.linesep
            line = shell.stderr.readline().rstrip()

        ret = types.SimpleNamespace()
        setattr(ret, 'returncode', 1 if line.endswith(self._ERROR) else 0)

        if stderr == subprocess.PIPE:
            setattr(ret, 'stderr', err)
        elif stderr == subprocess.STDOUT:
            out = out + os.linesep + err
        elif stderr != subprocess.DEVNULL:
            stderr.write(err)

        if stdout == subprocess.PIPE:
            setattr(ret, 'stdout', out)
        elif stdout != subprocess.DEVNULL:
            stdout.write(out)

        return ret
