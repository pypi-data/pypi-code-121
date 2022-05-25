# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import os

import numpy as np


def _check_a_ode(a=1.0):
    """
    Ensures that the a vector used in for the Boltz integrator is listed in increasing
    order.
    """
    aa = np.atleast_1d(a)
    ind_sort = aa.argsort()
    ind_unsort = ind_sort.argsort()
    a_sort = aa[ind_sort]
    return a_sort, ind_unsort


def relative_differences(a=1.0, b=1.0):
    a = np.atleast_1d(a)
    b = np.atleast_1d(b)
    return np.absolute((a - b) / a)


def get_active_branch_name():

    parent_of_here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    head = os.path.join(parent_of_here, ".git", "HEAD")

    try:

        with open(head, "r") as fh:
            content = fh.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                return line.partition("refs/heads/")[2]

    except IOError:
        return None
