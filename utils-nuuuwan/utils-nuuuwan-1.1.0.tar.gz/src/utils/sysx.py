"""System utils."""
import logging
import os
import subprocess
import time

import psutil

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('sysx')


def log_metrics():
    """Log system metrics.

    .. code-block:: python

        >>> from utils import sysx
        >>> print(sysx.log_metrics())
        {"ut": 1620724794.43984, "pid": 15129,
            "cpu_percent": 16.3, "vm_percent": 65.7}

    Note:
        Needs psutil

        .. code-block:: bash

            pip install psutil
    """
    return {
        'ut': time.time(),
        'pid': os.getpid(),
        'cpu_percent': psutil.cpu_percent(),
        'vm_percent': psutil.virtual_memory().percent,
    }


def run(cmd):
    """Run commands.

    .. code-block:: python

        >>> from utils import sysx
        >>> print(sysx.run('echo "hello"'))
        ['hello']

    """
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, _) = process.communicate()
    return output.decode().split('\n')[:-1]


def str_color(output_str, color_code=31):
    """Wrap standard print command, to add color."""
    color_cmd = '\033[0;%dm' % (color_code)
    end_cmd = '\033[0m'
    return '%s%s%s' % (color_cmd, str(output_str), end_cmd)


def retry(process_name, func_process, max_t_wait=60):
    """Retry function, until it returns not None."""
    t_wait = 1
    while True:
        result = func_process()
        if result is not None:
            log.info('"%s" complete.', process_name)
            return result

        if t_wait > max_t_wait:
            log.warning(
                '"%s" reached max retry limit (%ds). Aborting.',
                process_name,
                max_t_wait,
            )
            return None

        log.warning(
            '"%s" returned None. Waiting %ds...',
            process_name,
            t_wait,
        )
        time.sleep(t_wait)
        t_wait = t_wait * 1.414
