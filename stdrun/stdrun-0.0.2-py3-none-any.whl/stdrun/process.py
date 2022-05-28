from subprocess import Popen, PIPE
from .readline import ReadlineThread
from typing import Callable


def Run(
    command: str,
    stdout_callback: Callable[[str], None] = None,
    stderr_callback: Callable[[str], None] = None,
    shell: bool = False,
) -> int:
    """

    - `command` contains the command to be execute
    - `stdout_callback` is a function to be called when a line is received from the process stdout
    - `stderr_callback` is a function to be called when a line is received from the process stderr

    Returns: The exit code of the process execution
    """

    with Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        shell=shell,
        universal_newlines=True,
        bufsize=1,
    ) as proc:

        if stdout_callback:
            stdout_thread = ReadlineThread(proc.stdout, stdout_callback)
            stdout_thread.start()

        if stderr_callback:
            stderr_thread = ReadlineThread(proc.stderr, stderr_callback)
            stderr_thread.start()

        proc.wait()

        if stdout_callback:
            stdout_thread.join()

        if stderr_callback:
            stderr_thread.join()

        return proc.returncode
