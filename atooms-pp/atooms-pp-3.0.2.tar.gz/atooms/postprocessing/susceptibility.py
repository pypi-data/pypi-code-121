#!/usr/bin/env python

"""

"""

from collections import defaultdict
import numpy
from atooms.trajectory import Sliced
from .correlation import Correlation
from .helpers import adjust_skip


class Susceptibility(Correlation):

    def __init__(self, corr_cls, trajectory, norigins=-1, *args, **kwargs):
        """The first positional argument must be the trajectory instance."""
        # Instantiate correlation objects
        # with args passed upon construction
        self.trajectory = trajectory
        self.nbodies = corr_cls.nbodies
        self.phasespace = []  # nothing to dump
        self._corr_cls = corr_cls
        self._args = args
        self._kwargs = kwargs
        self._kwargs['norigins'] = '1'
        self.skip = adjust_skip(self.trajectory, norigins)

    def compute(self):
        y_all, x_all = [], []
        db = defaultdict(list)
        N = len(self.trajectory[0].particle)
        frac = self._kwargs['tgrid'][-1] / self.trajectory.total_time
        for i in range(0, int(len(self.trajectory.steps) * frac) - self.skip, self.skip):
            ths = Sliced(self.trajectory, slice(i, len(self.trajectory.steps), 1))
            corr = self._corr_cls(ths, *self._args, **self._kwargs)
            corr.compute()
            x, y = corr.grid, corr.value
            y_all.append(y)
            x_all.append(x)
            for xi, yi in zip(x, y):
                db[xi].append(yi * N)
        self.grid, self.value = [], []
        for xi in sorted(db):
            yi = numpy.array(db[xi])
            self.grid.append(xi)
            self.value.append(yi.var() / N)
