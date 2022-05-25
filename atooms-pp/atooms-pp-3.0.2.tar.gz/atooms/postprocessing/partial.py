# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""
Fake decorator to compute partial correlation functions.

It uses filters internally.
"""

import logging

from .helpers import filter_species
from . import core

_log = logging.getLogger(__name__)


# TODO: add output_path to all interfaces
class Partial(object):

    def __init__(self, corr_cls, species, *args, **kwargs):
        """The first positional argument must be the trajectory instance."""
        # Instantiate correlation objects
        # with args passed upon construction
        self.partial = {}
        self.nbodies = corr_cls.nbodies
        self.species = species
        self._output_path = core.pp_output_path

        if self.nbodies == 1:
            for i in range(len(self.species)):
                isp = self.species[i]
                self.partial[isp] = corr_cls(*args, **kwargs)
                self.partial[isp].add_filter(filter_species, isp)
                self.partial[isp].tag = str(isp)
                self.partial[isp].tag_description = 'species %s' % isp

        elif self.nbodies == 2:
            for i in range(len(self.species)):
                for j in range(len(self.species)):
                    isp = self.species[i]
                    jsp = self.species[j]
                    self.partial[(isp, jsp)] = corr_cls(*args, **kwargs)
                    self.partial[(isp, jsp)].add_filter(filter_species, isp)
                    # Slight optimization: avoid filtering twice when isp==jsp
                    if isp != jsp:
                        self.partial[(isp, jsp)].add_filter(filter_species, jsp)
                    self.partial[(isp, jsp)].tag = '%s-%s' % (isp, jsp)
                    self.partial[(isp, jsp)].tag_description = 'species pair %s-%s' % (isp, jsp)

    @property
    def output_path(self):
        return self._output_path
        
    @output_path.setter
    def output_path(self, path):
        self._output_path = path
        for key in self.partial:
            self.partial[key].output_path = path
                    
    def add_weight(self, trajectory=None, field=None, fluctuations=False):
        for key in self.partial:
            self.partial[key].add_weight(trajectory, field, fluctuations)

    def need_update(self):
        need = False
        for partial in self.partial.values():
            if partial.need_update():
                need = True
                break
        return need

    def compute(self):
        if self.nbodies == 1:
            for i in range(len(self.species)):
                isp = self.species[i]
                self.partial[isp].compute()

        elif self.nbodies == 2:
            for i in range(len(self.species)):
                for j in range(len(self.species)):
                    isp = self.species[i]
                    jsp = self.species[j]
                    if j >= i:
                        self.partial[(isp, jsp)].compute()
                    else:
                        # The isp-jsp has been already calculated
                        self.partial[(isp, jsp)].grid = self.partial[(jsp, isp)].grid
                        self.partial[(isp, jsp)].value = self.partial[(jsp, isp)].value

    def write(self):
        for partial in self.partial.values():
            partial.write()
                        
    def do(self, update=False):
        if update and not self.need_update():
            return

        self.compute()

        for partial in self.partial.values():
            try:
                partial.analyze()
            except ImportError as e:
                _log.warn('Could not analyze due to missing modules, continuing...')
                _log.warn(e)

            partial.write()
