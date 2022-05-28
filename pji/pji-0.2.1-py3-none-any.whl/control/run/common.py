import io

from .encoding import _try_read_to_bytes, _try_write
from ..model import RunResult
from ..process import common_process
from ...utils import eclosing


def common_run(args, shell: bool = False, stdin=None, stdout=None, stderr=None,
               environ=None, cwd=None, resources=None, identification=None) -> RunResult:
    """
    Create an common process with stream
    :param args: arguments for execution
    :param shell: use shell to execute args
    :param stdin: stdin stream (none means nothing)
    :param stdout: stdout stream (none means nothing)
    :param stderr: stderr stream (none means nothing)
    :param environ: environment variables
    :param cwd: new work dir
    :param resources: resource limit
    :param identification: user and group for execution
    :return: run result of this time
    """

    stdin_need_close = not stdin
    stdin = stdin or io.BytesIO()

    stdout_need_close = not stdout
    stdout = stdout or io.BytesIO()

    stderr_need_close = not stderr
    stderr = stderr or io.BytesIO()

    with eclosing(stdin, stdin_need_close) as stdin, \
            eclosing(stdout, stdout_need_close) as stdout, \
            eclosing(stderr, stderr_need_close) as stderr:
        with common_process(
                args=args, shell=shell,
                environ=environ, cwd=cwd,
                resources=resources, identification=identification,
        ) as cp:
            cp.communicate(_try_read_to_bytes(stdin), wait=False)
            cp.join()

            _try_write(stdout, cp.stdout)
            _try_write(stderr, cp.stderr)

        return cp.result
