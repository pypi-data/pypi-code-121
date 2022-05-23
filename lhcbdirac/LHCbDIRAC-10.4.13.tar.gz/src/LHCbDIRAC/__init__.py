###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
   LHCbDIRAC - LHCb extension of DIRAC

   References:
    DIRAC: https://github.com/DIRACGrid/DIRAC
    LHCbDIRAC: https://gitlab.cern.ch/lhcb-dirac/LHCbDIRAC

   The distributed data production and analysis system of LHCb.
"""
import os

from pkg_resources import get_distribution, DistributionNotFound


rootPath = os.path.dirname(os.path.realpath(__path__[0]))

# Define Version
try:
    __version__ = get_distribution(__name__).version
    version = __version__
except DistributionNotFound:
    # package is not installed
    version = "Unknown"


def extension_metadata():
    return {
        "primary_extension": True,
        "priority": 100,
        "setups": {
            "LHCb-Production": "dips://lhcb-conf-dirac.cern.ch:9135/Configuration/Server",
            "LHCb-Certification": "dips://lhcb-cert-dirac.cern.ch:9135/Configuration/Server",
        },
        "default_setup": "LHCb-Production",
    }
