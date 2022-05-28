import io
import random
import time
from itertools import chain

from .encoding import _try_write, _try_read_to_bytes
from ..model import RunResult
from ..model import TimingContent as _AbstractTimingContent
from ..process import interactive_process
from ...utils import eclosing

_STDIN_SHUFFLE_EPS = 1e-4


class TimingStdin(_AbstractTimingContent):
    def to_shuffled(self):
        groups = []
        current_group = []
        for ftime, content in self.lines:
            if current_group:
                if abs(ftime - current_group[0][0]) < _STDIN_SHUFFLE_EPS:
                    current_group.append((ftime, content))
                else:
                    groups.append(current_group)
                    current_group = [(ftime, content)]
            else:
                current_group.append((ftime, content))

        if current_group:
            groups.append(current_group)

        for group in groups:
            random.shuffle(group)

        final_items = list(chain(*(group for group in groups)))
        return self.__class__(final_items)


class TimingStdout(_AbstractTimingContent):
    pass


class TimingStderr(_AbstractTimingContent):
    pass


def timing_run(args, shell: bool = False, stdin=None, stdout=None, stderr=None,
               environ=None, cwd=None, resources=None, identification=None, shuffle=False) -> RunResult:
    """
    Create an timing process with stream
    :param args: arguments for execution
    :param shell: use shell to execute args
    :param stdin: stdin stream (none means nothing)
    :param stdout: stdout stream (none means nothing)
    :param stderr: stderr stream (none means nothing)
    :param environ: environment variables
    :param cwd: new work dir
    :param resources: resource limit
    :param identification: user and group for execution
    :param shuffle: Shuffle the inputs with similar timestamp.
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
        _stdin = TimingStdin.loads(_try_read_to_bytes(stdin))
        if shuffle:
            _stdin = _stdin.to_shuffled()

        with interactive_process(
                args=args, shell=shell,
                environ=environ, cwd=cwd,
                resources=resources, identification=identification,
        ) as ip:
            for _time, _line in _stdin.lines:
                _target_time = ip.start_time + _time
                while time.time() < _target_time and not ip.completed:
                    time.sleep(max(min(0.2, _target_time - time.time()), 0.0))

                try:
                    ip.print_stdin(_line)
                except BrokenPipeError:
                    break

            ip.close_stdin()

            _stdout, _stderr = [], []
            for _time, _tag, _line in ip.output_yield:
                if _tag == 'stdout':
                    _stdout.append((_time, _line))
                elif _tag == 'stderr':
                    _stderr.append((_time, _line))
                else:
                    raise ValueError('Unknown output type - {type}.'.format(type=repr(_time)))  # pragma: no cover

            ip.join()
            _try_write(stdout, TimingStdout.loads(_stdout).dumps())
            _try_write(stderr, TimingStderr.loads(_stderr).dumps())

            return ip.result
