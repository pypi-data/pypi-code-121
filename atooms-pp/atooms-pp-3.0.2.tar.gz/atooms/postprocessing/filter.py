# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""
Decorator to filter correlation functions by arbitrary condition
on particle properties.

It uses filters internally.

For 2-body correlations we expect up to two logical conditions. If
there is only one, we filter only the first group of particle, the
second one includes all the particles of the system. Otherwise we
filter two subsets of particles accordingly.
"""

import logging

from .helpers import filter_species

__all__ = ['Filter']
_log = logging.getLogger(__name__)


def Filter(correlation, condition):

    def _filter_generic(system, condition):
        import copy
        s = copy.copy(system)
        s.particle = []
        for particle in system.particle:
            if eval(condition, particle.__dict__):
                s.particle.append(particle)
        return s

    tag = condition.replace(' ', '')
    tag = tag.replace('and', '_')
    tag = tag.replace('or', '+')
    tag = tag.replace('"', '')
    tag = tag.replace("'", '')
    tag = tag.replace('==', '')
    tag = tag.replace('!=', '.not')
    tag = tag.replace(',', '-')
    correlation.tag = tag
    correlation.tag_description = condition

    if correlation.nbodies == 1:
        correlation.add_filter(_filter_generic, condition)

    elif correlation.nbodies == 2:
        # We expect up to two logical conditions
        conditions = condition.split(',')

        # If there is only one, we filter only the first group of
        # particles, the second one includes all the particles of the
        # system, hence the identity function
        if len(conditions) == 1:
            correlation.add_filter(_filter_generic, conditions[0])
            correlation.add_filter(lambda x: x)
        elif len(conditions) == 2:
            # If there are two, we filter two subsets of particles
            # accordingly
            correlation.add_filter(_filter_generic, conditions[0])
            correlation.add_filter(_filter_generic, conditions[1])
        else:
            raise ValueError('too many conditions for a 2 body-correlation function')

    return correlation
