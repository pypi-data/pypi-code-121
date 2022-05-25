###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
""" Tornado-based HTTPs TransformationManager service.
"""
from DIRAC import gLogger
from DIRAC.TransformationSystem.Service.TornadoTransformationManagerHandler import (
    TornadoTransformationManagerHandler as TornadoTManagerBase,
)
from LHCbDIRAC.TransformationSystem.Service.TransformationManagerHandler import TransformationManagerHandlerMixin


sLog = gLogger.getSubLogger(__name__)


class TornadoTransformationManagerHandler(TransformationManagerHandlerMixin, TornadoTManagerBase):
    log = sLog
