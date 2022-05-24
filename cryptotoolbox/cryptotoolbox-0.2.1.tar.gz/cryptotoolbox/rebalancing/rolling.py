#!/usr/bin/env python3
# coding: utf-8

""" Object to roll algorithms. """

# Built-in packages

# Third party packages

# Local packages

__all__ = ['_RollingMechanism']

class _EnsemblingRollingMechanism:
    """ Rolling mechanism. """

    def __init__(self, index, n, s):
        """ Initialize object. """
        self.idx = index
        self.n = n
        self.s = s

    def __call__(self, t=None, T=None, display=True):
        self.display = display
        # Set initial index
        if t is None:
            self.t = self.n

        else:
            self.t = t

        # Set max index
        if T is None:
            self.T = self.idx.size

        else:
            self.T = T

        return self

    def __iter__(self):
        # Iterative method
        return self

    def __next__(self):
        # Next method
        t = self.t

        # Display %
        if self.display:
            self._display()

        if self.t >= self.T - 1:

            raise StopIteration

        # Update rolling
        self.t += self.s

        # Set indexes
        self.d_n = self.idx[max(t - self.n, 0)]
        self.d_1 = self.idx[t - self.s]
        self.d = self.idx[t]
        self.d_s = self.idx[min(t + self.s, self.T - 1)]

        return slice(self.d_n, self.d_1), slice(self.d, self.d_s), None

    def _display(self):
        # Display %
        pct = (self.t - self.n - self.s) / (self.T - self.n - self.T % self.s)

        print('{:.2%}'.format(pct), end='\r')

class _RollingMechanism:
    """ Rolling mechanism. """

    def __init__(self, index, n, s):
        """ Initialize object. """
        self.idx = index
        self.n = n
        self.s = s

    def __call__(self, t=None, T=None, display=True):
        self.display = display
        # Set initial index
        if t is None:
            self.t = self.n

        else:
            self.t = t

        # Set max index
        if T is None:
            self.T = self.idx.size

        else:
            self.T = T

        return self

    def __iter__(self):
        # Iterative method
        return self

    def __next__(self):
        # Next method
        t = self.t

        # Display %
        if self.display:
            self._display()

        if self.t >= self.T - 1:

            raise StopIteration

        # Update rolling
        self.t += self.s

        # Set indexes
        self.d_n = self.idx[max(t - self.n, 0)]
        self.d_1 = self.idx[t - 1]
        self.d = self.idx[t]
        self.d_s = self.idx[min(t + self.s-1, self.T - 1)]

        return slice(self.d_n, self.d_1), slice(self.d, self.d_s), None

    def _display(self):
        # Display %
        pct = (self.t - self.n - self.s) / (self.T - self.n - self.T % self.s)

        print('{:.2%}'.format(pct), end='\r')

class _EvalRollingMechanism:
    """ Rolling mechanism. """

    def __init__(self, index, n, s, s_eval):
        """ Initialize object. """
        self.idx = index
        self.n = n
        self.s = s
        self.s_eval = s_eval

    def __call__(self, t=None, T=None, display=True):
        self.display = display
        # Set initial index
        if t is None:
            self.t = self.n
        else:
            self.t = t

        # Set max index
        if T is None:
            self.T = self.idx.size
        else:
            self.T = T

        return self

    def __iter__(self):
        # Iterative method
        return self

    def __next__(self):
        # Next method
        t = self.t

        # Display %
        if self.display:
            self._display()

        if self.t >= self.T - 1:

            raise StopIteration

        # Update rolling
        self.t += self.s

        # Set indexes
        self.d_n = self.idx[max(t - self.n, 0)]
        self.d_1 = self.idx[t - 1]
        self.d_eval_minus_one = self.idx[t - self.s_eval-1]
        self.d_eval = self.idx[t - self.s_eval]
        self.d = self.idx[t]
        self.d_s = self.idx[min(t + self.s-1, self.T - 1)]
        return slice(self.d_n, self.d_eval_minus_one ), slice(self.d, self.d_s), slice(self.d_eval, self.d_1)

    def _display(self):
        # Display %
        pct = (self.t - self.n - self.s) / (self.T - self.n - self.T % self.s)

        print('{:.2%}'.format(pct), end='\r')

class _ExpandingRollingMechanism:
    """ Rolling mechanism. """

    def __init__(self, index, s):
        """ Initialize object. """
        self.idx = index
        self.s = s

    def __call__(self, t=None, T=None, display=True):
        self.display = display
        # Set initial index
        if t is not None:
            self.t = t
        else :
            self.t = 3 * self.s
        # Set max index
        if T is None:
            self.T = self.idx.size
        else:
            self.T = T
        return self

    def __iter__(self):
        # Iterative method
        return self

    def __next__(self):
        # Next method
        t = self.t
        # Display %
        if self.display:
            self._display()

        if self.t >= self.T - 1:
            raise StopIteration
        # Update rolling
        self.t += self.s
        # Set indexes
        self.d_n = self.idx[0]
        self.d_1 = self.idx[t - 1]
        self.d = self.idx[t]
        self.d_s = self.idx[min(t + self.s-1, self.T - 1)]

        return slice(self.d_n, self.d_1), slice(self.d, self.d_s), None

    def _display(self):
        # Display %
        pct = (self.t)/(self.T)
        print('{:.2%}'.format(pct), end='\r')


class _ExpandingEvalRollingMechanism:
    """ Rolling mechanism. """

    def __init__(self, index, s, s_eval):
        """ Initialize object. """
        self.idx = index
        self.s = s
        self.s_eval = s_eval

    def __call__(self, t=None, T=None, display=True):
        self.display = display
        # Set initial index
        if t is not None:
            self.t = t
        else :
            self.t = 2 * self.s_eval
        # Set max index
        if T is None:
            self.T = self.idx.size
        else:
            self.T = T
        return self

    def __iter__(self):
        # Iterative method
        return self

    def __next__(self):
        # Next method
        t = self.t
        # Display %
        if self.display:
            self._display()

        if self.t >= self.T - 1:
            raise StopIteration
        # Update rolling
        self.t += self.s
        # Set indexes
        self.d_n = self.idx[0]
        self.d_eval = self.idx[t - self.s_eval]
        self.d_eval_minus_one = self.idx[t - self.s_eval-1]

        self.d_1 = self.idx[t - 1]
        self.d = self.idx[t]
        self.d_s = self.idx[min(t + self.s-1, self.T - 1)]

        return slice(self.d_n, self.d_eval_minus_one), slice(self.d, self.d_s), slice(self.d_eval,self.d_1)

    def _display(self):
        # Display %
        pct = (self.t)/(self.T)
        print('{:.2%}'.format(pct), end='\r')
