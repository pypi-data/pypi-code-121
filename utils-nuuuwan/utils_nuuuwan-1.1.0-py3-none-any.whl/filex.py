"""Filex."""

import random

from utils import timex

MIN_INT, MAX_INT = 10 ** 15, 10 ** 16 - 1


def read(file_name):
    """Read."""
    with open(file_name, 'r') as fin:
        content = fin.read()
        fin.close()
        return content


def write(file_name, content, mode='w'):
    """Write."""
    with open(file_name, mode) as fout:
        fout.write(content)
        fout.close()


def get_tmp_file():
    """Get tmp file name."""
    return '/tmp/tmp.%s.%d' % (
        timex.format_time(timex.get_unixtime(), '%Y%m%d%H%M%S'),
        random.randint(MIN_INT, MAX_INT),
    )
