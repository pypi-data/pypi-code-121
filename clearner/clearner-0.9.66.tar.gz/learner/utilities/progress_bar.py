# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import time
from sklearn.model_selection import GridSearchCV
from sklearn import model_selection
from sklearn.externals.joblib import Parallel


# the code adapted from MNE-Python
class ProgressBar:
    """Generate a command-line progressbar"""
    template = '\r[{0}{1}] {2:.0f}% | {3:.02f} sec | {4} '

    def __init__(self, title='', max_value=1, initial_value=0, max_chars=80, progress_character='#', verbose_bool=True):
        """Instantiate a progressbar object using the default or provided parameters

        :param title: message to include at end of progress bar
        :param max_value: maximum value of process (e.g. number of samples to process, bytes to download, etc.)
        :param initial_value: initial value of process, useful when resuming process from a specific value
        :param max_chars: number of characters to use for progress bar
        :param progress_character: Character in the progress bar that indicates the portion completed
        """
        self.cur_value = initial_value
        self.max_value = float(max_value)
        self.title = title
        self.max_chars = max_chars
        self.progress_character = progress_character
        self._do_print = verbose_bool
        self.start = time.time()

        self.closed = False
        self.update()

    def update(self):
        """Update progressbar with current value of process

        :return: None
        """

        progress = min(float(self.cur_value) / self.max_value, 1.)
        num_chars = int(progress * self.max_chars)
        num_left = self.max_chars - num_chars

        duration = time.time() - self.start

        # the \r tells the cursor to return to the beginning of the line rather than starting a new line.  This allows
        # having a progressbar-style display in the console window.
        bar = self.template.format(self.progress_character * num_chars, ' ' * num_left, progress * 100,
                                   duration, self.title)
        # force a flush because sometimes when using bash scripts and pipes, the output is not printed until after the
        # program exits.
        if self._do_print:
            sys.stdout.write(bar)
            sys.stdout.flush()

        if progress == 1:
            self.close()

        self.cur_value += 1

    def close(self):
        """Finish the progressbar using a linebreak and flushing the output"""
        if not self.closed:
            sys.stdout.write('\n')
            sys.stdout.flush()
            self.closed = True

    def __call__(self, sequence):
        sequence = iter(sequence)
        while True:
            try:
                yield next(sequence)
                self.update()
            except StopIteration:
                return


class GridSearchCVProgressBar(GridSearchCV):
    """Monkey patch Parallel to have a progress bar during grid search"""

    def _get_param_iterator(self):
        """Return ParameterGrid instance for the given param_grid

        :return: ParameterGrid iterator
        """
        iterator = super(GridSearchCVProgressBar, self)._get_param_iterator()
        iterator = list(iterator)
        n_candidates = len(iterator)

        cv = model_selection._split.check_cv(self.cv, None)
        n_splits = getattr(cv, 'n_splits', 3)
        max_value = n_candidates * n_splits

        class ParallelProgressBar(Parallel):
            def __call__(self, iterable):
                bar = ProgressBar(max_value=max_value, title='GridSearch')
                iterable = bar(iterable)
                return super(ParallelProgressBar, self).__call__(iterable)

        # monkey patch
        model_selection._search.Parallel = ParallelProgressBar

        return iterator
