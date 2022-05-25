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


"""
This is the PyCosmo package.
"""
__all__ = ["Cosmo"]

__author__ = "Adam Amara, Alexander Refregier, Joel Akeret, Lukas Gamper, Uwe Schmitt"
__credits__ = "Institute for Astronomy ETHZ"

import sys
import os

# needed for headless mode on ci server
if os.environ.get("CI") is not None:
    assert "matplotlib" not in sys.modules, "init matplotlib broken"
    import matplotlib

    if sys.platform == "darwin":
        matplotlib.use("macosx")
    else:
        matplotlib.use("Agg")

if True:  # make flake8 happy and avoids resorting by isort
    from . import patches  # noqa: F401
    from .build import build  # noqa: F401

    from .Cosmo import Cosmo  # noqa: F401
    from .Obs import Obs  # noqa: F401

    import pkg_resources


version = pkg_resources.require("PyCosmo")[0].version
__version__ = version
