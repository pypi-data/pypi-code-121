import os
from contextlib import contextmanager
from os import listdir
from os.path import join

from fiddler import constants


def file_list(root_dir):
    result = []
    if not os.path.isdir(root_dir):
        return result

    for f in listdir(root_dir):
        file_stats = os.stat(join(root_dir, f))
        result.append(
            {'name': f, 'size': file_stats.st_size, 'modified': file_stats.st_mtime}
        )
    return result


def getProgressBar(
    iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'
):
    """
    Adapted with love from https://stackoverflow.com/a/34325723

    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    BAR_COLOR = constants.bcolors.OKBLUE
    EMPTY_CHARACTER = '-'
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + EMPTY_CHARACTER * (length - filledLength)
    return f'{constants.ONE_LINE_PRINT}{prefix} |{BAR_COLOR}{bar}{constants.bcolors.ENDCOLOR}| {percent}% {suffix}'


@contextmanager
def open_file_w_auto_close(filename, mode='rb'):
    f = open(filename, mode=mode)
    try:
        yield f
    finally:
        f.close()
