"""
Progress bar support.

We support progress bars via tqdm. If the module is not found, we
provide a fallback class that monkey-patches it.
"""

import sys

# See https://stackoverflow.com/questions/3160699/python-progress-bar for simple fallbacks

# These module level variables can be tweaked at run time
active = False
ncols = 80
bar_format = '# {l_bar} {bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_noinv_fmt}{postfix}]'


class NoProgressBar(object):

    """Fallback progress bar that monkey patches tqdm"""

    def __init__(self, iterable=None, *args, **kwargs):
        self.iterable = iterable

    def update(self, value):
        pass

    def close(self):
        pass

    def __len__(self):
        return len(self.iterable)

    def __iter__(self):
        iterable = self.iterable
        for obj in iterable:
            yield obj

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


try:
    from tqdm import tqdm

    class CustomProgressBar(tqdm):

        """Slightly customized tqdm progress bar"""

        def __init__(self, *args, **kwargs):
            # If active option is passed it takes precedence over the module level variable
            if 'active' in kwargs:
                _active = kwargs['active']
                kwargs.pop('active')
            else:
                _active = active
            tqdm.__init__(self, disable=not _active,
                          bar_format=bar_format, ncols=ncols, file=sys.stdout, *args, **kwargs)

        def update(self, n=1):
            if not self.disable:
                tqdm.update(self, n-self.n)

    progress = CustomProgressBar

except ImportError:
    progress = NoProgressBar
